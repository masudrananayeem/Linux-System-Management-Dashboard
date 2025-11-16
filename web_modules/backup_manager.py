#!/usr/bin/env python3
"""
Backup management module for web dashboard
"""

import os
import subprocess
import tarfile
from datetime import datetime

class BackupManager:
    def __init__(self, backup_dir="~/backups"):
        self.backup_dir = os.path.expanduser(backup_dir)
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_full_backup(self, source_dir="~"):
        """Create a full backup of specified directory"""
        try:
            source_dir = os.path.expanduser(source_dir)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.backup_dir, f"full_backup_{timestamp}.tar.gz")
            
            with tarfile.open(backup_file, "w:gz") as tar:
                tar.add(source_dir, arcname=os.path.basename(source_dir))
            
            size = os.path.getsize(backup_file)
            return {
                'success': True,
                'message': f'Full backup created: {backup_file}',
                'file': backup_file,
                'size': self._bytes_to_human(size)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def list_backups(self):
        """List all available backups"""
        try:
            backups = []
            for file in os.listdir(self.backup_dir):
                if file.endswith('.tar.gz'):
                    filepath = os.path.join(self.backup_dir, file)
                    stat = os.stat(filepath)
                    backups.append({
                        'name': file,
                        'size': self._bytes_to_human(stat.st_size),
                        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    })
            
            return sorted(backups, key=lambda x: x['modified'], reverse=True)
        except Exception as e:
            return {'error': str(e)}
    
    def _bytes_to_human(self, bytes):
        """Convert bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes < 1024.0:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024.0
        return f"{bytes:.2f} PB"
