<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# MicroPython 개발 가이드

이 프로젝트는 ESP32/ESP8266용 MicroPython 개발 환경입니다. 코드 생성 시 다음 가이드라인을 따라주세요:

## 코드 스타일
- MicroPython 특화 모듈 사용: `machine`, `network`, `time` 등
- 메모리 효율적인 코드 작성 (마이크로컨트롤러 환경)
- 한국어 주석과 출력 메시지 사용
- 예외 처리 포함 (하드웨어 오류 대응)

## 하드웨어 고려사항
- ESP32: GPIO 2 (내장 LED), GPIO 0 (내장 버튼)
- ESP8266: GPIO 2 (내장 LED), GPIO 0 (내장 버튼)
- 핀 번호는 보드별로 다를 수 있음을 주석으로 명시

## 라이브러리 구조
- `lib/utils.py`: 공통 유틸리티 클래스
- `examples/`: 기능별 예제 코드
- `main.py`: 메인 실행 파일
- `boot.py`: 시스템 초기화

## 네트워킹
- WiFi 연결 시 타임아웃 처리
- 연결 상태 확인 로직 포함
- 네트워크 오류 시 적절한 메시지 출력

## 에러 처리
- ImportError: PC 환경에서 실행 시 적절한 메시지
- 하드웨어 오류: 센서 없음, 핀 오류 등
- 네트워크 오류: WiFi 연결 실패, 요청 타임아웃
