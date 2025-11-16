#!/usr/bin/env python3
"""
System monitoring module for web dashboard
"""

import psutil
import subprocess
import os
from datetime import datetime

class SystemMonitor:
    def get_system_overview(self):
        """Get comprehensive system overview"""
        try:
            # CPU information
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_cores = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory information
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk information
            disk = psutil.disk_usage('/')
            
            # System information
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            return {
                'cpu': {
                    'percent': cpu_percent,
                    'cores': cpu_cores,
                    'frequency': cpu_freq.current if cpu_freq else 'N/A'
                },
                'memory': {
                    'total': self._bytes_to_gb(memory.total),
                    'used': self._bytes_to_gb(memory.used),
                    'free': self._bytes_to_gb(memory.available),
                    'percent': memory.percent
                },
                'disk': {
                    'total': self._bytes_to_gb(disk.total),
                    'used': self._bytes_to_gb(disk.used),
                    'free': self._bytes_to_gb(disk.free),
                    'percent': disk.percent
                },
                'system': {
                    'boot_time': boot_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'uptime': str(uptime).split('.')[0],
                    'load_avg': os.getloadavg()
                }
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_detailed_cpu_info(self):
        """Get detailed CPU information"""
        try:
            return {
                'physical_cores': psutil.cpu_count(logical=False),
                'logical_cores': psutil.cpu_count(logical=True),
                'usage_per_core': psutil.cpu_percent(percpu=True, interval=1),
                'current_frequency': psutil.cpu_freq().current if psutil.cpu_freq() else 'N/A',
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _bytes_to_gb(self, bytes):
        """Convert bytes to gigabytes"""
        return round(bytes / (1024 ** 3), 2)
