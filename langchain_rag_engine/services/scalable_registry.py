"""
Scalable Registry Service
Replaces in-memory registries with database-backed storage for multi-instance deployments
"""

import asyncio
from typing import Dict, Optional, Set
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from db.database import SessionLocal
from db import models


class ScalableRegistry:
    """
    Database-backed registry to replace in-memory storage
    Supports multi-instance deployments and horizontal scaling
    """

    def __init__(self):
        # Keep small in-memory cache for performance, but persist to DB
        self._local_cache: Dict[str, Dict] = {}
        self._cleanup_interval = 300  # 5 minutes

    def _get_db_session(self) -> Session:
        """Get database session"""
        return SessionLocal()

    def create_stream_session(self, request_id: str, user_id: int, question: str, conversation_id: Optional[int] = None) -> bool:
        """Create a new streaming session in database"""
        try:
            db = self._get_db_session()
            session = models.StreamSession(
                request_id=request_id,
                user_id=user_id,
                question=question,
                conversation_id=conversation_id,
                status="active"
            )
            db.add(session)
            db.commit()
            db.refresh(session)

            # Update local cache
            self._local_cache[request_id] = {
                "user_id": user_id,
                "question": question,
                "conversation_id": conversation_id,
                "status": "active",
                "created_at": session.created_at
            }

            return True
        except Exception as e:
            print(f"❌ Failed to create stream session: {e}")
            return False
        finally:
            db.close()

    def get_stream_session(self, request_id: str) -> Optional[Dict]:
        """Get streaming session data"""
        # Check local cache first
        if request_id in self._local_cache:
            return self._local_cache[request_id]

        # Check database
        try:
            db = self._get_db_session()
            session = db.query(models.StreamSession).filter(
                models.StreamSession.request_id == request_id
            ).first()

            if session:
                data = {
                    "user_id": session.user_id,
                    "question": session.question,
                    "conversation_id": session.conversation_id,
                    "status": session.status,
                    "created_at": session.created_at
                }
                # Cache locally
                self._local_cache[request_id] = data
                return data
        except Exception as e:
            print(f"❌ Failed to get stream session: {e}")
        finally:
            db.close()

        return None

    def update_stream_session_status(self, request_id: str, status: str) -> bool:
        """Update streaming session status"""
        try:
            db = self._get_db_session()
            session = db.query(models.StreamSession).filter(
                models.StreamSession.request_id == request_id
            ).first()

            if session:
                session.status = status
                session.updated_at = datetime.utcnow()
                db.commit()

                # Update local cache
                if request_id in self._local_cache:
                    self._local_cache[request_id]["status"] = status

                return True
        except Exception as e:
            print(f"❌ Failed to update stream session: {e}")
        finally:
            db.close()

        return False

    def delete_stream_session(self, request_id: str) -> bool:
        """Delete streaming session"""
        try:
            db = self._get_db_session()
            session = db.query(models.StreamSession).filter(
                models.StreamSession.request_id == request_id
            ).first()

            if session:
                db.delete(session)
                db.commit()

                # Remove from local cache
                self._local_cache.pop(request_id, None)

                return True
        except Exception as e:
            print(f"❌ Failed to delete stream session: {e}")
        finally:
            db.close()

        return False

    def get_active_stream_count(self, user_id: int) -> int:
        """Get count of active streams for a user"""
        try:
            db = self._get_db_session()
            count = db.query(models.StreamSession).filter(
                models.StreamSession.user_id == user_id,
                models.StreamSession.status == "active"
            ).count()
            return count
        except Exception as e:
            print(f"❌ Failed to get active stream count: {e}")
            return 0
        finally:
            db.close()

    def register_task(self, task_id: str, request_id: str, task_type: str = "streaming") -> bool:
        """Register a task in the database"""
        try:
            db = self._get_db_session()
            task = models.TaskRegistry(
                task_id=task_id,
                request_id=request_id,
                task_type=task_type,
                status="running"
            )
            db.add(task)
            db.commit()
            return True
        except Exception as e:
            print(f"❌ Failed to register task: {e}")
            return False
        finally:
            db.close()

    def get_task(self, task_id: str) -> Optional[Dict]:
        """Get task information"""
        try:
            db = self._get_db_session()
            task = db.query(models.TaskRegistry).filter(
                models.TaskRegistry.task_id == task_id
            ).first()

            if task:
                return {
                    "task_id": task.task_id,
                    "request_id": task.request_id,
                    "task_type": task.task_type,
                    "status": task.status,
                    "metadata": task.metadata,
                    "created_at": task.created_at
                }
        except Exception as e:
            print(f"❌ Failed to get task: {e}")
        finally:
            db.close()

        return None

    def update_task_status(self, task_id: str, status: str, metadata: Optional[Dict] = None) -> bool:
        """Update task status"""
        try:
            db = self._get_db_session()
            task = db.query(models.TaskRegistry).filter(
                models.TaskRegistry.task_id == task_id
            ).first()

            if task:
                task.status = status
                if metadata:
                    task.metadata = metadata
                task.updated_at = datetime.utcnow()
                db.commit()
                return True
        except Exception as e:
            print(f"❌ Failed to update task status: {e}")
        finally:
            db.close()

        return False

    def cleanup_expired_sessions(self):
        """Clean up expired streaming sessions and tasks"""
        try:
            db = self._get_db_session()

            # Clean up old stream sessions (older than 1 hour)
            cutoff_time = datetime.utcnow() - timedelta(hours=1)
            expired_sessions = db.query(models.StreamSession).filter(
                models.StreamSession.created_at < cutoff_time
            ).all()

            for session in expired_sessions:
                db.delete(session)

            # Clean up old tasks (older than 24 hours)
            task_cutoff = datetime.utcnow() - timedelta(hours=24)
            expired_tasks = db.query(models.TaskRegistry).filter(
                models.TaskRegistry.created_at < task_cutoff
            ).all()

            for task in expired_tasks:
                db.delete(task)

            db.commit()
            print(f"🧹 Cleaned up {len(expired_sessions)} sessions and {len(expired_tasks)} tasks")

        except Exception as e:
            print(f"❌ Failed to cleanup expired sessions: {e}")
        finally:
            db.close()

    async def start_cleanup_task(self):
        """Start background cleanup task"""
        while True:
            await asyncio.sleep(self._cleanup_interval)
            self.cleanup_expired_sessions()


# Global instance
_scalable_registry: Optional[ScalableRegistry] = None

def get_scalable_registry() -> ScalableRegistry:
    """Get the global scalable registry instance"""
    global _scalable_registry
    if _scalable_registry is None:
        _scalable_registry = ScalableRegistry()
    return _scalable_registry