"""
Session management for marine fish scraper
스크래핑 세션 관리 시스템
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from logger import get_logger
from taxonomy_manager import SpeciesInfo


@dataclass
class ScrapingSession:
    """스크래핑 세션 정보"""
    session_id: str
    created_at: datetime
    updated_at: datetime
    target_species: List[Dict[str, Any]]  # SpeciesInfo를 dict로 저장
    images_per_species: int
    total_species: int
    completed_species: int
    total_downloaded: int
    current_species_index: int
    status: str  # 'running', 'paused', 'completed', 'failed'
    error_message: Optional[str] = None
    
    def __post_init__(self):
        """초기화 후 처리"""
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScrapingSession':
        """딕셔너리로부터 생성"""
        return cls(**data)
    
    def get_progress_percentage(self) -> float:
        """진행률 반환 (0.0 ~ 100.0)"""
        if self.total_species == 0:
            return 0.0
        return (self.completed_species / self.total_species) * 100.0
    
    def is_completed(self) -> bool:
        """완료 여부 확인"""
        return self.status == 'completed' or self.completed_species >= self.total_species
    
    def update_progress(self, completed_species: int, total_downloaded: int):
        """진행 상황 업데이트"""
        self.completed_species = completed_species
        self.total_downloaded = total_downloaded
        self.updated_at = datetime.now()
        
        if self.completed_species >= self.total_species:
            self.status = 'completed'


class SessionManager:
    """세션 관리자"""
    
    def __init__(self, sessions_dir: str = "sessions"):
        self.logger = get_logger("session_manager")
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(exist_ok=True)
        
        # 현재 활성 세션
        self.current_session: Optional[ScrapingSession] = None
    
    def create_session(self, target_species: List[SpeciesInfo], images_per_species: int) -> ScrapingSession:
        """새 세션 생성"""
        session_id = str(uuid.uuid4())[:8]  # 짧은 ID 사용
        
        # SpeciesInfo를 dict로 변환
        species_dicts = [species.to_dict() for species in target_species]
        
        session = ScrapingSession(
            session_id=session_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            target_species=species_dicts,
            images_per_species=images_per_species,
            total_species=len(target_species),
            completed_species=0,
            total_downloaded=0,
            current_species_index=0,
            status='running'
        )
        
        self.current_session = session
        self.save_session(session)
        
        self.logger.info(f"새 세션 생성: {session_id} ({len(target_species)}종)")
        return session
    
    def save_session(self, session: ScrapingSession) -> bool:
        """세션 저장"""
        try:
            session_file = self.sessions_dir / f"session_{session.session_id}.json"
            
            # 임시 파일에 먼저 저장
            temp_file = session_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(session.to_dict(), f, ensure_ascii=False, indent=2)
            
            # 성공하면 원본 파일로 이동
            temp_file.replace(session_file)
            
            self.logger.debug(f"세션 저장 완료: {session.session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"세션 저장 실패: {session.session_id} - {e}")
            return False
    
    def load_session(self, session_id: str) -> Optional[ScrapingSession]:
        """세션 로드"""
        try:
            session_file = self.sessions_dir / f"session_{session_id}.json"
            
            if not session_file.exists():
                self.logger.warning(f"세션 파일이 존재하지 않음: {session_id}")
                return None
            
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            session = ScrapingSession.from_dict(data)
            self.current_session = session
            
            self.logger.info(f"세션 로드 완료: {session_id}")
            return session
            
        except Exception as e:
            self.logger.error(f"세션 로드 실패: {session_id} - {e}")
            return None
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """저장된 세션 목록 반환"""
        sessions = []
        
        try:
            for session_file in self.sessions_dir.glob("session_*.json"):
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 기본 정보만 추출
                    session_info = {
                        'session_id': data.get('session_id'),
                        'created_at': data.get('created_at'),
                        'status': data.get('status'),
                        'total_species': data.get('total_species', 0),
                        'completed_species': data.get('completed_species', 0),
                        'total_downloaded': data.get('total_downloaded', 0),
                        'progress_percentage': (data.get('completed_species', 0) / max(1, data.get('total_species', 1))) * 100
                    }
                    sessions.append(session_info)
                    
                except Exception as e:
                    self.logger.warning(f"세션 파일 읽기 오류: {session_file.name} - {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"세션 목록 조회 실패: {e}")
        
        # 생성일 기준 내림차순 정렬
        sessions.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return sessions
    
    def delete_session(self, session_id: str) -> bool:
        """세션 삭제"""
        try:
            session_file = self.sessions_dir / f"session_{session_id}.json"
            
            if session_file.exists():
                session_file.unlink()
                self.logger.info(f"세션 삭제 완료: {session_id}")
                
                # 현재 세션이 삭제된 세션이면 초기화
                if self.current_session and self.current_session.session_id == session_id:
                    self.current_session = None
                
                return True
            else:
                self.logger.warning(f"삭제할 세션 파일이 존재하지 않음: {session_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"세션 삭제 실패: {session_id} - {e}")
            return False
    
    def pause_session(self, session_id: str) -> bool:
        """세션 일시정지"""
        if self.current_session and self.current_session.session_id == session_id:
            self.current_session.status = 'paused'
            self.current_session.updated_at = datetime.now()
            return self.save_session(self.current_session)
        return False
    
    def resume_session(self, session_id: str) -> bool:
        """세션 재시작"""
        session = self.load_session(session_id)
        if session and session.status == 'paused':
            session.status = 'running'
            session.updated_at = datetime.now()
            return self.save_session(session)
        return False
    
    def complete_session(self, session_id: str) -> bool:
        """세션 완료 처리"""
        if self.current_session and self.current_session.session_id == session_id:
            self.current_session.status = 'completed'
            self.current_session.updated_at = datetime.now()
            return self.save_session(self.current_session)
        return False
    
    def fail_session(self, session_id: str, error_message: str) -> bool:
        """세션 실패 처리"""
        if self.current_session and self.current_session.session_id == session_id:
            self.current_session.status = 'failed'
            self.current_session.error_message = error_message
            self.current_session.updated_at = datetime.now()
            return self.save_session(self.current_session)
        return False
    
    def update_current_session_progress(self, completed_species: int, total_downloaded: int):
        """현재 세션의 진행 상황 업데이트"""
        if self.current_session:
            self.current_session.update_progress(completed_species, total_downloaded)
            self.save_session(self.current_session)
    
    def get_current_session(self) -> Optional[ScrapingSession]:
        """현재 활성 세션 반환"""
        return self.current_session
    
    def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """오래된 세션 정리"""
        cleaned_count = 0
        cutoff_date = datetime.now().timestamp() - (days_old * 24 * 3600)
        
        try:
            for session_file in self.sessions_dir.glob("session_*.json"):
                try:
                    # 파일 수정 시간 확인
                    if session_file.stat().st_mtime < cutoff_date:
                        session_file.unlink()
                        cleaned_count += 1
                        self.logger.debug(f"오래된 세션 삭제: {session_file.name}")
                        
                except Exception as e:
                    self.logger.warning(f"세션 파일 정리 오류: {session_file.name} - {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"세션 정리 중 오류: {e}")
        
        if cleaned_count > 0:
            self.logger.info(f"오래된 세션 정리 완료: {cleaned_count}개")
        
        return cleaned_count
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """세션 통계 반환"""
        sessions = self.list_sessions()
        
        if not sessions:
            return {}
        
        total_sessions = len(sessions)
        completed_sessions = sum(1 for s in sessions if s.get('status') == 'completed')
        running_sessions = sum(1 for s in sessions if s.get('status') == 'running')
        failed_sessions = sum(1 for s in sessions if s.get('status') == 'failed')
        
        total_species = sum(s.get('total_species', 0) for s in sessions)
        total_downloaded = sum(s.get('total_downloaded', 0) for s in sessions)
        
        return {
            'total_sessions': total_sessions,
            'completed_sessions': completed_sessions,
            'running_sessions': running_sessions,
            'failed_sessions': failed_sessions,
            'completion_rate': (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0,
            'total_species_processed': total_species,
            'total_images_downloaded': total_downloaded,
            'average_images_per_session': total_downloaded / total_sessions if total_sessions > 0 else 0
        }
    
    def export_session_data(self, session_id: str, export_path: str) -> bool:
        """세션 데이터 내보내기"""
        try:
            session = self.load_session(session_id)
            if not session:
                return False
            
            export_data = {
                'session_info': session.to_dict(),
                'export_timestamp': datetime.now().isoformat(),
                'statistics': {
                    'progress_percentage': session.get_progress_percentage(),
                    'is_completed': session.is_completed(),
                    'species_count': len(session.target_species),
                    'average_images_per_species': session.total_downloaded / max(1, session.completed_species)
                }
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"세션 데이터 내보내기 완료: {session_id} -> {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"세션 데이터 내보내기 실패: {session_id} - {e}")
            return False