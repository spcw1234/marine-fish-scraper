"""
Advanced error handling system with retry mechanisms and circuit breaker pattern
"""
import time
import functools
from typing import Callable, Any, Optional, Dict, List, Type, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError
from logger import get_logger


class ErrorType(Enum):
    """에러 타입 분류"""
    NETWORK = "network"
    FILE_SYSTEM = "file_system"
    DATA_VALIDATION = "data_validation"
    RATE_LIMIT = "rate_limit"
    AUTHENTICATION = "authentication"
    UNKNOWN = "unknown"


class ErrorSeverity(Enum):
    """에러 심각도"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ErrorRecord:
    """에러 기록"""
    timestamp: datetime
    error_type: ErrorType
    severity: ErrorSeverity
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    resolved: bool = False


class CircuitBreakerState(Enum):
    """Circuit Breaker 상태"""
    CLOSED = "closed"      # 정상 동작
    OPEN = "open"          # 차단 상태
    HALF_OPEN = "half_open"  # 테스트 상태


@dataclass
class CircuitBreaker:
    """Circuit Breaker 패턴 구현"""
    failure_threshold: int = 5
    recovery_timeout: int = 60  # 초
    success_threshold: int = 3  # HALF_OPEN에서 CLOSED로 전환하기 위한 성공 횟수
    
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None
    
    def can_execute(self) -> bool:
        """실행 가능 여부 확인"""
        if self.state == CircuitBreakerState.CLOSED:
            return True
        elif self.state == CircuitBreakerState.OPEN:
            if self.last_failure_time and \
               datetime.now() - self.last_failure_time > timedelta(seconds=self.recovery_timeout):
                self.state = CircuitBreakerState.HALF_OPEN
                self.success_count = 0
                return True
            return False
        elif self.state == CircuitBreakerState.HALF_OPEN:
            return True
        return False
    
    def record_success(self):
        """성공 기록"""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
        elif self.state == CircuitBreakerState.CLOSED:
            self.failure_count = max(0, self.failure_count - 1)
    
    def record_failure(self):
        """실패 기록"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.state == CircuitBreakerState.CLOSED:
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitBreakerState.OPEN
        elif self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.OPEN
            self.success_count = 0


class RetryConfig:
    """재시도 설정"""
    def __init__(self, 
                 max_attempts: int = 3,
                 base_delay: float = 1.0,
                 max_delay: float = 60.0,
                 exponential_base: float = 2.0,
                 jitter: bool = True):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def get_delay(self, attempt: int) -> float:
        """재시도 지연 시간 계산"""
        delay = self.base_delay * (self.exponential_base ** (attempt - 1))
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            import random
            delay *= (0.5 + random.random() * 0.5)  # 50-100% 범위의 지터
        
        return delay


class ErrorHandler:
    """고급 에러 처리 시스템"""
    
    def __init__(self, logger_name: str = "error_handler"):
        self.logger = get_logger(logger_name)
        self.error_history: List[ErrorRecord] = []
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # 기본 재시도 설정
        self.retry_configs = {
            ErrorType.NETWORK: RetryConfig(max_attempts=3, base_delay=1.0),
            ErrorType.FILE_SYSTEM: RetryConfig(max_attempts=2, base_delay=0.5),
            ErrorType.RATE_LIMIT: RetryConfig(max_attempts=5, base_delay=5.0, max_delay=300.0),
            ErrorType.DATA_VALIDATION: RetryConfig(max_attempts=1),  # 재시도 없음
            ErrorType.AUTHENTICATION: RetryConfig(max_attempts=2, base_delay=2.0),
            ErrorType.UNKNOWN: RetryConfig(max_attempts=2, base_delay=1.0)
        }
    
    def classify_error(self, exception: Exception) -> ErrorType:
        """예외를 에러 타입으로 분류"""
        if isinstance(exception, (ConnectionError, Timeout, requests.exceptions.RequestException)):
            return ErrorType.NETWORK
        elif isinstance(exception, (IOError, OSError, FileNotFoundError, PermissionError)):
            return ErrorType.FILE_SYSTEM
        elif isinstance(exception, (ValueError, TypeError, KeyError)):
            return ErrorType.DATA_VALIDATION
        elif "rate limit" in str(exception).lower() or "429" in str(exception):
            return ErrorType.RATE_LIMIT
        elif "401" in str(exception) or "403" in str(exception) or "unauthorized" in str(exception).lower():
            return ErrorType.AUTHENTICATION
        else:
            return ErrorType.UNKNOWN
    
    def get_error_severity(self, error_type: ErrorType, exception: Exception) -> ErrorSeverity:
        """에러 심각도 결정"""
        if error_type == ErrorType.AUTHENTICATION:
            return ErrorSeverity.HIGH
        elif error_type == ErrorType.FILE_SYSTEM and isinstance(exception, PermissionError):
            return ErrorSeverity.HIGH
        elif error_type == ErrorType.NETWORK:
            return ErrorSeverity.MEDIUM
        elif error_type == ErrorType.RATE_LIMIT:
            return ErrorSeverity.LOW
        else:
            return ErrorSeverity.MEDIUM
    
    def record_error(self, exception: Exception, context: Dict[str, Any] = None) -> ErrorRecord:
        """에러 기록"""
        error_type = self.classify_error(exception)
        severity = self.get_error_severity(error_type, exception)
        
        error_record = ErrorRecord(
            timestamp=datetime.now(),
            error_type=error_type,
            severity=severity,
            message=str(exception),
            context=context or {}
        )
        
        self.error_history.append(error_record)
        
        # 로그 기록
        log_message = f"{error_type.value.upper()}: {exception}"
        if context:
            log_message += f" | Context: {context}"
        
        if severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message)
        elif severity == ErrorSeverity.HIGH:
            self.logger.error(log_message)
        elif severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_message)
        else:
            self.logger.debug(log_message)
        
        return error_record
    
    def get_circuit_breaker(self, key: str) -> CircuitBreaker:
        """Circuit Breaker 인스턴스 반환"""
        if key not in self.circuit_breakers:
            self.circuit_breakers[key] = CircuitBreaker()
        return self.circuit_breakers[key]
    
    def with_retry(self, 
                   error_types: Union[ErrorType, List[ErrorType]] = None,
                   circuit_breaker_key: str = None,
                   custom_retry_config: RetryConfig = None):
        """재시도 데코레이터"""
        if isinstance(error_types, ErrorType):
            error_types = [error_types]
        
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                # Circuit Breaker 확인
                if circuit_breaker_key:
                    circuit_breaker = self.get_circuit_breaker(circuit_breaker_key)
                    if not circuit_breaker.can_execute():
                        raise Exception(f"Circuit breaker is OPEN for {circuit_breaker_key}")
                
                last_exception = None
                
                for attempt in range(1, 10):  # 최대 시도 횟수
                    try:
                        result = func(*args, **kwargs)
                        
                        # 성공 시 Circuit Breaker 업데이트
                        if circuit_breaker_key:
                            circuit_breaker.record_success()
                        
                        # 성공한 경우 이전 에러를 해결된 것으로 표시
                        if last_exception:
                            self._mark_error_resolved(last_exception)
                        
                        return result
                        
                    except Exception as e:
                        last_exception = e
                        error_record = self.record_error(e, {
                            'function': func.__name__,
                            'attempt': attempt,
                            'args': str(args)[:100],
                            'kwargs': str(kwargs)[:100]
                        })
                        
                        error_type = self.classify_error(e)
                        
                        # 재시도 가능한 에러 타입인지 확인
                        if error_types and error_type not in error_types:
                            if circuit_breaker_key:
                                circuit_breaker.record_failure()
                            raise e
                        
                        # 재시도 설정 가져오기
                        retry_config = custom_retry_config or self.retry_configs.get(error_type)
                        if not retry_config or attempt >= retry_config.max_attempts:
                            if circuit_breaker_key:
                                circuit_breaker.record_failure()
                            raise e
                        
                        # 재시도 지연
                        delay = retry_config.get_delay(attempt)
                        self.logger.debug(f"Retrying {func.__name__} in {delay:.2f}s (attempt {attempt}/{retry_config.max_attempts})")
                        time.sleep(delay)
                        
                        error_record.retry_count = attempt
                
                # 모든 재시도 실패
                if circuit_breaker_key:
                    circuit_breaker.record_failure()
                raise last_exception
            
            return wrapper
        return decorator
    
    def _mark_error_resolved(self, exception: Exception):
        """에러를 해결된 것으로 표시"""
        for error_record in reversed(self.error_history):
            if error_record.message == str(exception) and not error_record.resolved:
                error_record.resolved = True
                break
    
    def handle_gracefully(self, 
                         default_return: Any = None,
                         log_level: str = "warning"):
        """우아한 에러 처리 데코레이터 (예외를 발생시키지 않음)"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    self.record_error(e, {
                        'function': func.__name__,
                        'graceful_handling': True
                    })
                    
                    log_message = f"Gracefully handled error in {func.__name__}: {e}"
                    if log_level == "error":
                        self.logger.error(log_message)
                    elif log_level == "warning":
                        self.logger.warning(log_message)
                    else:
                        self.logger.debug(log_message)
                    
                    return default_return
            return wrapper
        return decorator
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """에러 통계 반환"""
        if not self.error_history:
            return {}
        
        total_errors = len(self.error_history)
        resolved_errors = sum(1 for e in self.error_history if e.resolved)
        
        # 타입별 통계
        type_stats = {}
        for error_type in ErrorType:
            count = sum(1 for e in self.error_history if e.error_type == error_type)
            if count > 0:
                type_stats[error_type.value] = count
        
        # 심각도별 통계
        severity_stats = {}
        for severity in ErrorSeverity:
            count = sum(1 for e in self.error_history if e.severity == severity)
            if count > 0:
                severity_stats[severity.value] = count
        
        # 최근 에러들
        recent_errors = [
            {
                'timestamp': e.timestamp.isoformat(),
                'type': e.error_type.value,
                'severity': e.severity.value,
                'message': e.message[:100],
                'resolved': e.resolved
            }
            for e in self.error_history[-10:]
        ]
        
        return {
            'total_errors': total_errors,
            'resolved_errors': resolved_errors,
            'resolution_rate': resolved_errors / total_errors if total_errors > 0 else 0,
            'error_types': type_stats,
            'error_severities': severity_stats,
            'recent_errors': recent_errors,
            'circuit_breaker_states': {
                key: breaker.state.value 
                for key, breaker in self.circuit_breakers.items()
            }
        }
    
    def reset_circuit_breaker(self, key: str) -> bool:
        """Circuit Breaker 리셋"""
        if key in self.circuit_breakers:
            self.circuit_breakers[key] = CircuitBreaker()
            self.logger.info(f"Circuit breaker reset: {key}")
            return True
        return False
    
    def clear_error_history(self, older_than_days: int = None):
        """에러 히스토리 정리"""
        if older_than_days:
            cutoff_date = datetime.now() - timedelta(days=older_than_days)
            self.error_history = [
                e for e in self.error_history 
                if e.timestamp > cutoff_date
            ]
        else:
            self.error_history.clear()
        
        self.logger.info(f"Error history cleared (older than {older_than_days} days)" if older_than_days else "Error history cleared")
    
    def export_error_log(self, file_path: str):
        """에러 로그 내보내기"""
        import json
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'statistics': self.get_error_statistics(),
            'error_history': [
                {
                    'timestamp': e.timestamp.isoformat(),
                    'error_type': e.error_type.value,
                    'severity': e.severity.value,
                    'message': e.message,
                    'context': e.context,
                    'retry_count': e.retry_count,
                    'resolved': e.resolved
                }
                for e in self.error_history
            ]
        }
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Error log exported to {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to export error log: {e}")


# 전역 에러 핸들러 인스턴스
_global_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """전역 에러 핸들러 인스턴스 반환"""
    global _global_error_handler
    
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler()
    
    return _global_error_handler


# 편의 함수들
def with_retry(*args, **kwargs):
    """재시도 데코레이터 (전역 에러 핸들러 사용)"""
    return get_error_handler().with_retry(*args, **kwargs)


def handle_gracefully(*args, **kwargs):
    """우아한 에러 처리 데코레이터 (전역 에러 핸들러 사용)"""
    return get_error_handler().handle_gracefully(*args, **kwargs)


def record_error(exception: Exception, context: Dict[str, Any] = None) -> ErrorRecord:
    """에러 기록 (전역 에러 핸들러 사용)"""
    return get_error_handler().record_error(exception, context)