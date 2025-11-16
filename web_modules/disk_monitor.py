#!/usr/bin/env python3
"""
Disk monitoring module for web dashboard
"""

import psutil
import subprocess

class DiskMonitor:
    def get_disk_usage(self):
        """Get disk usage information for all partitions"""
        try:
            disks = []
            for partition in psutil.disk_partitions():
                # Skip special filesystems
                if partition.fstype in ['squashfs', 'tmpfs', 'devtmpfs']:
                    continue
                
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disks.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': self._bytes_to_human(usage.total),
                        'used': self._bytes_to_human(usage.used),
                        'free': self._bytes_to_human(usage.free),
                        'percent': usage.percent,
                        'total_bytes': usage.total,
                        'used_bytes': usage.used
                    })
                except PermissionError:
                    # Skip partitions we can't access
                    continue
            
            return disks
        except Exception as e:
            return {'error': str(e)}
    
    def get_large_files(self, path="~", limit=20):
        """Find large files in specified directory"""
        try:
            path = os.path.expanduser(path)
            result = subprocess.run(
                ['find', path, '-type', 'f', '-exec', 'du', '-h', '{}', ';'],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                files = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        size, filepath = line.split('\t', 1)
                        files.append({'size': size, 'path': filepath})
                
                # Sort by size and return top N
                return sorted(files, key=lambda x: self._parse_size(x['size']), reverse=True)[:limit]
            else:
                return {'error': 'Failed to find large files'}
                
        except subprocess.TimeoutExpired:
            return {'error': 'Operation timed out'}
        except Exception as e:
            return {'error': str(e)}
    
    def _bytes_to_human(self, bytes):
        """Convert bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes < 1024.0:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024.0
        return f"{bytes:.2f} PB"
    
    def _parse_size(self, size_str):
        """Parse human-readable size to bytes for sorting"""
        units = {'B': 1, 'K': 1024, 'M': 1024**2, 'G': 1024**3, 'T': 1024**4}
        number = float(size_str[:-1])
        unit = size_str[-1]
        return number * units.get(unit, 1)
