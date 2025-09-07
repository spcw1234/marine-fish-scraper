import time
import json
import network
import machine
import ubinascii
import sys
import math
from machine import Pin, I2C, Timer, WDT
import gc

# lib 경로 추가 및 import
try:
    from lib.ads1115 import ADS1115
    from lib.umqttsimple import MQTTClient
except ImportError:
    # 대안 경로로 시도
    sys.path.append('lib')
    from ads1x15 import ADS1115
    from umqttsimple import MQTTClient

import ssd1306

# 설정값들
WIFI_SSID = "SK_4974_2.4G"
WIFI_PASSWORD = "BQP06@0276"
MQTT_SERVER = "spcwtech.mooo.com"
MQTT_PORT = 1883
# ESP32의 고유 칩 ID를 클라이언트 ID로 사용
UNIQUE_ID = ubinascii.hexlify(machine.unique_id()).decode()
MQTT_CLIENT_ID = "esp32_nitrate_" + UNIQUE_ID
MQTT_USER = ""  # 필요시 설정
MQTT_PASSWORD = ""  # 필요시 설정
# MQTT 토픽 설정
MQTT_TOPIC_STATUS = UNIQUE_ID + "/nitrate/sta"  # 데이터 발행용
MQTT_TOPIC_COMMAND = UNIQUE_ID + "/nitrate/con"  # 명령 수신용

# 핀 설정 (ESP32 S3)
# ADS1115용 I2C0
I2C0_SCL = 4
I2C0_SDA = 5
# SSD1306용 I2C1
I2C1_SCL = 6
I2C1_SDA = 7
LED_PIN = 2

# ISE 센서 보정값 (실제 센서에 맞게 조정 필요)
# 질산염 ISE는 농도가 높을수록 전압이 낮아지는 특성 (음이온)
# 실제 측정 데이터 기반 보정 포인트들
# 형식: (전압_mV, 실제_농도_ppm)
CALIBRATION_POINTS = [
    (3000, 0),      # 기준점: 높은 전압 = 낮은 농도 (0ppm)
    (2800, 5.0),    # 수조 측정: 2800mV = 5ppm 
    (2600, 62.0),   # 표준용액 측정: 2600mV = 62ppm (10⁻³ mol/L)
    # 추가 보정 포인트들을 여기에 추가 가능
    # (전압이 낮을수록 농도가 높음)
]

# 전압 분할기 설정 (5V → 3.3V)
# PH4502C는 5V 출력, 전압 분할기로 3.3V로 낮춰서 ADS1115에 입력
# 분할비 = 원래전압/분할된전압 = 5V/3.3V ≈ 1.515
VOLTAGE_DIVIDER_RATIO = 1.515  # 5V/3.3V

# 칼만 필터 설정
KALMAN_Q = 0.01  # 프로세스 노이즈 (작을수록 더 안정적)
KALMAN_R = 0.5   # 측정 노이즈 (작을수록 측정값을 더 신뢰)

# Nernst 방정식 상수
NERNST_SLOPE_25C = 59.16  # mV/decade at 25°C for monovalent ion
NITRATE_MOLAR_MASS = 62.0  # NO3- molar mass (g/mol)
# 캘리브레이션에서 E0(표준전위)와 실제 기울기는 자동 계산됨


class SimpleKalmanFilter:
    """간단한 1차원 칼만 필터"""
    def __init__(self, q=KALMAN_Q, r=KALMAN_R, initial_value=0):
        self.q = q  # 프로세스 노이즈
        self.r = r  # 측정 노이즈
        self.x = initial_value  # 상태 추정값
        self.p = 1.0  # 오차 공분산
        self.is_initialized = False
    
    def update(self, measurement):
        """새로운 측정값으로 필터 업데이트"""
        if not self.is_initialized:
            self.x = measurement
            self.is_initialized = True
            return self.x
        
        # 예측 단계
        self.p += self.q
        
        # 업데이트 단계
        k = self.p / (self.p + self.r)  # 칼만 게인
        self.x += k * (measurement - self.x)  # 상태 업데이트
        self.p *= (1 - k)  # 오차 공분산 업데이트
        
        return self.x

class NitrateSensor:
    def __init__(self):
        # WDT 초기화 (최대 8초 - ESP32 S3의 최대값)
        try:
            self.wdt = WDT(timeout=8000)  # 8초 WDT
            print("WDT 초기화 완료 (8초 타임아웃)")
        except Exception as e:
            print("WDT 초기화 실패:", e)
            self.wdt = None
        
        # 내장 LED 초기화
        self.led = Pin(LED_PIN, Pin.OUT)
        self.led.off()
        
        # 메모리 정리
        gc.collect()
        
        # 칼만 필터 초기화 (전압용, 농도용)
        self.voltage_filter = SimpleKalmanFilter(q=KALMAN_Q, r=KALMAN_R)
        self.concentration_filter = SimpleKalmanFilter(q=KALMAN_Q*0.5, r=KALMAN_R*2)
        
        # I2C 초기화 (두 개의 독립적인 I2C 버스)
        # I2C0: ADS1115용
        self.i2c0 = I2C(0, scl=Pin(I2C0_SCL), sda=Pin(I2C0_SDA), freq=400000)
        print("I2C0 (ADS1115) 스캔 결과:", [hex(addr) for addr in self.i2c0.scan()])
        
        # I2C1: SSD1306용
        self.i2c1 = I2C(1, scl=Pin(I2C1_SCL), sda=Pin(I2C1_SDA), freq=400000)
        print("I2C1 (SSD1306) 스캔 결과:", [hex(addr) for addr in self.i2c1.scan()])
        
        # ADS1115 초기화 (I2C0 사용)
        try:
            # PH4502C 모듈은 최대 3.3V 출력
            # gain=2는 ±2.048V 범위 (3.3V 센서에는 부족)
            # gain=1은 ±4.096V 범위 (3.3V 센서에 적합)
            # gain=2/3은 ±6.144V 범위 (불필요하게 큰 범위)
            self.ads = ADS1115(self.i2c0, address=0x48, gain=1)
            print("ADS1115 초기화 완료 (±4.096V 범위, PH4502C용)")
        except Exception as e:
            print("ADS1115 초기화 실패:", e)
            self.ads = None
        
        # SSD1306 OLED 디스플레이 초기화 (I2C1 사용)
        try:
            self.oled = ssd1306.SSD1306_I2C(128, 64, self.i2c1, addr=0x3C)
            self.oled.fill(0)
            self.oled.text("Nitrate Sensor", 0, 0)
            self.oled.text("Initializing...", 0, 20)
            self.oled.show()
            print("SSD1306 OLED 초기화 완료")
        except Exception as e:
            print("SSD1306 초기화 실패:", e)
            self.oled = None
        
        # WiFi 연결
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        
        # MQTT 클라이언트
        self.mqtt_client = None
        self.mqtt_connected = False
        
        # 측정 데이터
        self.last_voltage = 0
        self.last_concentration = 0
        self.last_raw_voltage = 0  # 원시 전압값 저장용
        
        # 타이머
        self.measurement_timer = Timer(0)
        self.display_timer = Timer(1)
        self.mqtt_timer = Timer(2)
        
        # 캘리브레이션 포인트 (전압[mV], 농도[ppm])
        self.calibration_points = [(3000, 0), (2800, 5), (2600, 62)]
        
        # Nernst 방정식 파라미터 (캘리브레이션에서 계산됨)
        self.nernst_e0 = None  # 표준전위 (mV)
        self.nernst_slope = None  # 실제 기울기 (mV/decade)
        self.calculate_nernst_parameters()
        
    def calculate_nernst_parameters(self):
        """캘리브레이션 포인트로부터 Nernst 방정식 파라미터 계산"""
        if len(self.calibration_points) < 2:
            print("Nernst 파라미터 계산 실패: 캘리브레이션 포인트 부족")
            return
            
        # 0ppm을 제외한 포인트들로 계산 (log(0) 불가능)
        valid_points = [(v, c) for v, c in self.calibration_points if c > 0]
        
        if len(valid_points) < 2:
            print("Nernst 파라미터 계산 실패: 유효한 농도 포인트 부족")
            return
            
        # 두 포인트로 기울기 계산: S = (E2-E1) / (log10(c2)-log10(c1))
        v1, c1_ppm = valid_points[0]
        v2, c2_ppm = valid_points[-1]
        
        # ppm을 mol/L로 변환 (ppm = mg/L, mol/L = mg/L / (molar_mass * 1000))
        c1_mol = (c1_ppm / 1000) / NITRATE_MOLAR_MASS  # mol/L
        c2_mol = (c2_ppm / 1000) / NITRATE_MOLAR_MASS  # mol/L
        
        # Nernst 기울기 계산
        self.nernst_slope = (v2 - v1) / (math.log10(c2_mol) - math.log10(c1_mol))
        
        # E0 계산: E0 = E1 - S * log10(c1)
        self.nernst_e0 = v1 - self.nernst_slope * math.log10(c1_mol)
        
        print(f"Nernst 파라미터 계산 완료:")
        print(f"  E0 = {self.nernst_e0:.2f} mV")
        print(f"  기울기 = {self.nernst_slope:.2f} mV/decade")
        print(f"  이론값 = {NERNST_SLOPE_25C:.2f} mV/decade (25°C)")
        
    def feed_watchdog(self):
        """WDT 피드 - 안전하게 처리"""
        if self.wdt:
            try:
                self.wdt.feed()
            except Exception:
                pass  # WDT 피드 실패는 조용히 처리
        
    def connect_wifi(self):
        """WiFi 연결"""
        if not self.wlan.isconnected():
            print("WiFi 연결 중...")
            self.wlan.connect(WIFI_SSID, WIFI_PASSWORD)
            
            timeout = 0
            while not self.wlan.isconnected() and timeout < 20:
                time.sleep(1)
                timeout += 1
                self.led.on()
                time.sleep(0.1)
                self.led.off()
                self.feed_watchdog()  # WDT 피드
                
            if self.wlan.isconnected():
                print("WiFi 연결됨:", self.wlan.ifconfig())
                gc.collect()  # 메모리 정리
                return True
            else:
                print("WiFi 연결 실패")
                return False
        return True
    
    def connect_mqtt(self):
        """MQTT 브로커 연결"""
        try:
            print(f"MQTT 연결 시도: {MQTT_SERVER}:{MQTT_PORT}")
            print(f"클라이언트 ID: {MQTT_CLIENT_ID}")
            
            self.mqtt_client = MQTTClient(
                MQTT_CLIENT_ID,
                MQTT_SERVER,
                port=MQTT_PORT,
                user=MQTT_USER if MQTT_USER else None,
                password=MQTT_PASSWORD if MQTT_PASSWORD else None
            )
            # 메시지 수신 콜백 설정
            self.mqtt_client.set_callback(self.mqtt_callback)
            self.mqtt_client.connect()
            # 명령 토픽 구독
            self.mqtt_client.subscribe(MQTT_TOPIC_COMMAND.encode())
            self.mqtt_connected = True
            print("MQTT 연결 성공!")
            print(f"구독 토픽: {MQTT_TOPIC_COMMAND}")
            print(f"발행 토픽: {MQTT_TOPIC_STATUS}")
            gc.collect()  # 메모리 정리
            return True
        except Exception as e:
            print("MQTT 연결 실패:", e)
            self.mqtt_connected = False
            return False
    
    def mqtt_callback(self, topic, msg):
        """MQTT 메시지 수신 콜백"""
        try:
            topic_str = topic.decode()
            msg_str = msg.decode()
            print(f"MQTT 수신: {topic_str} -> {msg_str}")
            
            if topic_str == MQTT_TOPIC_COMMAND:
                # 명령 처리
                if msg_str == "calibrate":
                    print("보정 명령 수신")
                    # 보정 로직 추가 가능
                elif msg_str.startswith("cal:"):
                    # 실시간 보정: "cal:전압,농도" 형식
                    # 예: "cal:2885,5.0"
                    try:
                        cal_data = msg_str[4:].split(',')
                        voltage = float(cal_data[0])
                        concentration = float(cal_data[1])
                        self.add_calibration_point(voltage, concentration)
                        print(f"보정 완료: {voltage}mV = {concentration}ppm")
                    except Exception as e:
                        print("보정 데이터 파싱 오류:", e)
                elif msg_str == "reset":
                    print("리셋 명령 수신")
                    machine.reset()
                elif msg_str == "reset_filter":
                    print("칼만 필터 리셋")
                    self.voltage_filter = SimpleKalmanFilter(q=KALMAN_Q, r=KALMAN_R)
                    self.concentration_filter = SimpleKalmanFilter(q=KALMAN_Q*0.5, r=KALMAN_R*2)
                    print("칼만 필터 초기화 완료")
                elif msg_str == "status":
                    print("상태 요청 수신")
                    # 즉시 상태 발송
                    self.publish_data()
                elif msg_str == "debug":
                    print("디버그 정보:")
                    print(f"보정 포인트: {CALIBRATION_POINTS}")
                    print(f"현재 전압: {self.last_voltage}mV")
                    print(f"현재 농도: {self.last_concentration}ppm")
                    print(f"칼만 필터 상태 - 전압: {self.voltage_filter.x:.2f}, 농도: {self.concentration_filter.x:.3f}")
        except Exception as e:
            print("MQTT 콜백 오류:", e)
    
    def read_ise_voltage(self):
        """ISE 센서에서 전압 읽기"""
        if not self.ads:
            return None
            
        try:
            # ADS1115에서 단일 채널 읽기 (채널 0)
            # rate=4는 1600SPS (샘플 속도)
            raw_value = self.ads.read(0, 4)
            
            # 16비트 부호있는 정수로 변환
            if raw_value > 32767:
                raw_value -= 65536
            
            # 전압으로 변환 (gain=1일 때 ±4.096V 범위)
            measured_voltage = raw_value * 4.096 / 32767
            
            # 전압 분할기 보정 적용 (실제 ISE 전압 계산)
            actual_voltage = measured_voltage * VOLTAGE_DIVIDER_RATIO
            
            return actual_voltage * 1000  # mV로 변환
            
        except Exception as e:
            print("전압 읽기 오류:", e)
            return None
    
    def calculate_concentration(self, voltage_mv):
        """Nernst 방정식을 사용한 농도 계산"""
        if voltage_mv is None:
            return None
            
        if self.nernst_e0 is None or self.nernst_slope is None:
            print("Nernst 파라미터가 없음 - 캘리브레이션 필요")
            return None
            
        try:
            print(f"측정 전압: {voltage_mv:.2f}mV")
            
            # Nernst 방정식: E = E0 + S * log10(c)
            # 농도 계산: c = 10^((E - E0) / S)
            log_concentration = (voltage_mv - self.nernst_e0) / self.nernst_slope
            concentration_mol = 10 ** log_concentration
            
            # mol/L을 ppm으로 변환: ppm = mol/L * molar_mass * 1000
            concentration_ppm = concentration_mol * NITRATE_MOLAR_MASS * 1000
            
            print(f"Nernst: {concentration_ppm:.3f}ppm")
            
            return max(0, concentration_ppm)  # 음수 방지
                
        except Exception as e:
            print("Nernst 농도 계산 오류:", e)
            return None
    
    def add_calibration_point(self, voltage_mv, actual_ppm):
        """보정 포인트 추가 (런타임 중 보정 가능)"""
        global CALIBRATION_POINTS
        CALIBRATION_POINTS.append((voltage_mv, actual_ppm))
        self.calibration_points.append((voltage_mv, actual_ppm))
        print(f"보정 포인트 추가: {voltage_mv:.2f}mV = {actual_ppm:.3f}ppm")
        # Nernst 파라미터 재계산
        self.calculate_nernst_parameters()
    
    def update_display(self):
        """OLED 디스플레이 업데이트"""
        if not self.oled:
            return
            
        try:
            self.oled.fill(0)
            
            # 제목
            self.oled.text("Nitrate ISE", 0, 0)
            
            # WiFi 상태
            wifi_status = "WiFi: OK" if self.wlan.isconnected() else "WiFi: --"
            self.oled.text(wifi_status, 0, 12)
            
            # MQTT 상태
            mqtt_status = "MQTT: OK" if self.mqtt_connected else "MQTT: --"
            self.oled.text(mqtt_status, 0, 24)
            
            # 전압 표시
            voltage_text = "V: {:.2f}mV".format(self.last_voltage)
            self.oled.text(voltage_text, 0, 36)
            
            # 농도 표시
            if self.last_concentration is not None:
                if self.last_concentration < 1:
                    conc_text = "C: {:.3f}ppm".format(self.last_concentration)
                elif self.last_concentration < 100:
                    conc_text = "C: {:.2f}ppm".format(self.last_concentration)
                else:
                    conc_text = "C: {:.1f}ppm".format(self.last_concentration)
            else:
                conc_text = "C: --ppm"
            self.oled.text(conc_text, 0, 48)
            
            self.oled.show()
            
        except Exception as e:
            print("디스플레이 업데이트 오류:", e)
    
    def publish_data(self):
        """MQTT로 데이터 전송 (간소화된 데이터만)"""
        if not self.mqtt_connected or not self.mqtt_client:
            print("MQTT 발행 실패: 연결되지 않음")
            return
            
        try:
            self.feed_watchdog()  # WDT 피드
            
            # 간소화된 데이터만 전송
            data = {
                "raw_mv": round(self.last_raw_voltage, 2),          # 원시 전압값
                "filtered_mv": round(self.last_voltage, 2),        # 보정후 전압값 (칼만필터링)
                "ppm": round(self.last_concentration, 3) if self.last_concentration else 0  # ppm 농도
            }
            
            payload = json.dumps(data)
            print(f"MQTT 발행: {payload}")
            
            result = self.mqtt_client.publish(MQTT_TOPIC_STATUS, payload)
            if result == 0:
                print("MQTT 전송 성공")
            else:
                print(f"MQTT 전송 실패: {result}")
            
            gc.collect()  # 메모리 정리
            
        except Exception as e:
            print("MQTT 전송 오류:", e)
            self.mqtt_connected = False
    
    def measurement_callback(self, timer):
        """주기적 측정 콜백 (칼만 필터 적용)"""
        try:
            self.feed_watchdog()  # WDT 피드
            
            # LED 점멸로 측정 표시
            self.led.on()
            
            # 원시 전압 측정
            raw_voltage = self.read_ise_voltage()
            if raw_voltage is not None:
                # 원시 전압값 저장
                self.last_raw_voltage = raw_voltage
                
                # 칼만 필터로 전압 안정화
                filtered_voltage = self.voltage_filter.update(raw_voltage)
                self.last_voltage = filtered_voltage
                
                # 필터링된 전압으로 농도 계산
                raw_concentration = self.calculate_concentration(filtered_voltage)
                if raw_concentration is not None:
                    # 칼만 필터로 농도 안정화
                    filtered_concentration = self.concentration_filter.update(raw_concentration)
                    self.last_concentration = filtered_concentration
                    
                    print("측정: 원시={:.2f}mV, 필터링={:.2f}mV, 농도={:.3f}ppm".format(
                        raw_voltage, filtered_voltage, filtered_concentration))
                else:
                    print("측정: 원시={:.2f}mV, 필터링={:.2f}mV, 농도=계산실패".format(
                        raw_voltage, filtered_voltage))
            
            self.led.off()
            gc.collect()  # 메모리 정리
            
        except Exception as e:
            print("측정 오류:", e)
            self.led.off()
    
    def display_callback(self, timer):
        """주기적 디스플레이 업데이트 콜백"""
        self.feed_watchdog()  # WDT 피드
        self.update_display()
    
    def mqtt_callback_timer(self, timer):
        """주기적 MQTT 데이터 발송 콜백"""
        self.feed_watchdog()  # WDT 피드
        if self.mqtt_connected:
            self.publish_data()
        else:
            print("MQTT 연결 끊어짐 - 발송 실패")
    
    def start_monitoring(self):
        """모니터링 시작"""
        print("질산염 ISE 모니터링 시작")
        
        # WiFi 연결
        if self.connect_wifi():
            # MQTT 연결
            self.connect_mqtt()
        
        # 초기 디스플레이 업데이트
        self.update_display()
        
        # 테스트 데이터 발송 제거 (실제 측정값만 발송)
        print("질산염 ISE 모니터링 활성화")
        
        # 타이머 시작 (측정: 2초마다, 디스플레이: 1초마다)
        self.measurement_timer.init(period=2000, mode=Timer.PERIODIC, 
                                  callback=self.measurement_callback)
        self.display_timer.init(period=1000, mode=Timer.PERIODIC, 
                              callback=self.display_callback)
        
        # MQTT 발행 타이머 추가 (2초마다 발행)
        self.mqtt_timer = Timer(2)
        self.mqtt_timer.init(period=2000, mode=Timer.PERIODIC, 
                           callback=self.mqtt_callback_timer)
        
        print("모니터링 활성화됨")
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self.measurement_timer.deinit()
        self.display_timer.deinit()
        self.mqtt_timer.deinit()
        
        # WDT 정리 (ESP32에서는 명시적 해제가 없음)
        if self.wdt:
            print("WDT 정리 중...")
            self.wdt = None
        
        if self.mqtt_client:
            try:
                self.mqtt_client.disconnect()
            except Exception:
                pass
        
        gc.collect()  # 마지막 메모리 정리
        print("모니터링 중지됨")

def main():
    """메인 함수"""
    print("ESP32 S3 질산염 ISE 센서 시작")
    
    # 센서 객체 생성
    sensor = NitrateSensor()
    
    try:
        # 모니터링 시작
        sensor.start_monitoring()
        
        # 메인 루프
        while True:
            try:
                sensor.feed_watchdog()  # WDT 피드
                
                # WiFi 연결 확인 및 재연결
                if not sensor.wlan.isconnected():
                    print("WiFi 연결 끊어짐, 재연결 시도")
                    sensor.connect_wifi()
                
                # MQTT 연결 확인 및 재연결
                if sensor.wlan.isconnected() and not sensor.mqtt_connected:
                    print("MQTT 재연결 시도")
                    sensor.connect_mqtt()
                
                # MQTT 메시지 확인 (논블로킹)
                if sensor.mqtt_connected:
                    try:
                        sensor.mqtt_client.check_msg()
                    except Exception:
                        sensor.mqtt_connected = False
                
                gc.collect()  # 메모리 정리
                time.sleep(10)  # 10초마다 연결 상태 확인
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print("메인 루프 오류:", e)
                time.sleep(5)
    
    except KeyboardInterrupt:
        print("사용자에 의해 중단됨")
    except Exception as e:
        print("예상치 못한 오류:", e)
    finally:
        sensor.stop_monitoring()
        print("프로그램 종료")

if __name__ == "__main__":
    main()
