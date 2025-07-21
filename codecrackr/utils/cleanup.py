import os
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, Any

from config import Config

logger = logging.getLogger(__name__)

class CleanupManager:
    def __init__(self):
        self.config = Config()
        self.temp_dir = self.config.TEMP_DIR
        self.cleanup_hours = self.config.TEMP_DIR_CLEANUP_HOURS
    
    def cleanup_temp_files(self, max_age_hours: int = None) -> Dict[str, int]:
        """Clean up temporary files older than specified hours"""
        if max_age_hours is None:
            max_age_hours = self.cleanup_hours
        
        stats = {
            'directories_removed': 0,
            'files_removed': 0,
            'bytes_freed': 0,
            'errors': []
        }
        
        try:
            if not os.path.exists(self.temp_dir):
                return stats
            
            current_time = datetime.now()
            cutoff_time = current_time - timedelta(hours=max_age_hours)
            
            for item in os.listdir(self.temp_dir):
                item_path = os.path.join(self.temp_dir, item)
                
                try:
                    # Get creation/modification time
                    stat = os.stat(item_path)
                    item_time = datetime.fromtimestamp(stat.st_mtime)
                    
                    if item_time < cutoff_time:
                        if os.path.isdir(item_path):
                            # Calculate directory size
                            dir_size = self._get_directory_size(item_path)
                            shutil.rmtree(item_path)
                            stats['directories_removed'] += 1
                            stats['bytes_freed'] += dir_size
                            logger.info(f"Removed directory: {item_path} ({dir_size} bytes)")
                            
                        elif os.path.isfile(item_path):
                            file_size = os.path.getsize(item_path)
                            os.remove(item_path)
                            stats['files_removed'] += 1
                            stats['bytes_freed'] += file_size
                            logger.info(f"Removed file: {item_path} ({file_size} bytes)")
                            
                except Exception as e:
                    stats['errors'].append(str(e))
                    logger.error(f"Error cleaning up {item_path}: {e}")
                    
        except Exception as e:
            stats['errors'].append(str(e))
            logger.error(f"Error during cleanup: {e}")
        
        return stats
    
    def cleanup_specific_repo(self, repo_path: str) -> bool:
        """Clean up a specific repository directory"""
        try:
            if os.path.exists(repo_path):
                if os.path.isdir(repo_path):
                    shutil.rmtree(repo_path)
                    logger.info(f"Removed repository directory: {repo_path}")
                else:
                    os.remove(repo_path)
                    logger.info(f"Removed repository file: {repo_path}")
                return True
        except Exception as e:
            logger.error(f"Error removing repository {repo_path}: {e}")
            return False
    
    def get_temp_directory_stats(self) -> Dict[str, Any]:
        """Get statistics about temporary directory"""
        stats = {
            'total_directories': 0,
            'total_files': 0,
            'total_size': 0,
            'oldest_item': None,
            'newest_item': None,
            'items': []
        }
        
        try:
            if not os.path.exists(self.temp_dir):
                return stats
            
            oldest_time = None
            newest_time = None
            
            for item in os.listdir(self.temp_dir):
                item_path = os.path.join(self.temp_dir, item)
                
                try:
                    stat = os.stat(item_path)
                    item_time = datetime.fromtimestamp(stat.st_mtime)
                    item_size = self._get_item_size(item_path)
                    
                    stats['total_size'] += item_size
                    
                    if os.path.isdir(item_path):
                        stats['total_directories'] += 1
                    else:
                        stats['total_files'] += 1
                    
                    stats['items'].append({
                        'name': item,
                        'path': item_path,
                        'size': item_size,
                        'modified': item_time.isoformat(),
                        'type': 'directory' if os.path.isdir(item_path) else 'file'
                    })
                    
                    if oldest_time is None or item_time < oldest_time:
                        oldest_time = item_time
                    
                    if newest_time is None or item_time > newest_time:
                        newest_time = item_time
                        
                except Exception as e:
                    logger.error(f"Error getting stats for {item_path}: {e}")
            
            stats['oldest_item'] = oldest_time.isoformat() if oldest_time else None
            stats['newest_item'] = newest_time.isoformat() if newest_time else None
            
        except Exception as e:
            logger.error(f"Error getting temp directory stats: {e}")
        
        return stats
    
    def _get_directory_size(self, path: str) -> int:
        """Get total size of a directory"""
        total_size = 0
        
        try:
            for root, dirs, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        total_size += os.path.getsize(file_path)
                    except (OSError, FileNotFoundError):
                        pass
        except Exception:
            pass
        
        return total_size
    
    def _get_item_size(self, path: str) -> int:
        """Get size of a file or directory"""
        try:
            if os.path.isdir(path):
                return self._get_directory_size(path)
            else:
                return os.path.getsize(path)
        except Exception:
            return 0
    
    def schedule_cleanup(self, interval_hours: int = 1):
        """Schedule periodic cleanup (for background tasks)"""
        import threading
        
        def cleanup_worker():
            while True:
                try:
                    stats = self.cleanup_temp_files()
                    if stats['directories_removed'] > 0 or stats['files_removed'] > 0:
                        logger.info(f"Cleanup completed: {stats}")
                except Exception as e:
                    logger.error(f"Scheduled cleanup error: {e}")
                
                time.sleep(interval_hours * 3600)
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
        logger.info(f"Scheduled cleanup every {interval_hours} hours")
    
    def cleanup_old_sessions(self, session_data: Dict[str, Any], max_age_hours: int = 2) -> Dict[str, int]:
        """Clean up old session data"""
        stats = {
            'sessions_removed': 0,
            'errors': []
        }
        
        try:
            current_time = datetime.now()
            cutoff_time = current_time - timedelta(hours=max_age_hours)
            
            expired_sessions = []
            for session_id, data in session_data.items():
                try:
                    created_at = data.get('created_at')
                    if created_at and isinstance(created_at, str):
                        created_time = datetime.fromisoformat(created_at)
                        if created_time < cutoff_time:
                            expired_sessions.append(session_id)
                except Exception as e:
                    stats['errors'].append(str(e))
            
            for session_id in expired_sessions:
                del session_data[session_id]
                stats['sessions_removed'] += 1
            
            logger.info(f"Cleaned up {stats['sessions_removed']} expired sessions")
            
        except Exception as e:
            stats['errors'].append(str(e))
            logger.error(f"Error cleaning up sessions: {e}")
        
        return stats

# Global cleanup instance
cleanup_manager = CleanupManager()

def cleanup_temp_files(max_age_hours: int = None) -> Dict[str, int]:
    """Convenience function for global cleanup"""
    return cleanup_manager.cleanup_temp_files(max_age_hours)

def get_temp_stats() -> Dict[str, Any]:
    """Convenience function for getting temp directory stats"""
    return cleanup_manager.get_temp_directory_stats()

# Example usage
if __name__ == "__main__":
    # Test cleanup
    stats = cleanup_temp_files()
    print("Cleanup stats:", stats)
    
    # Get directory stats
    dir_stats = get_temp_stats()
    print("Directory stats:", dir_stats)
