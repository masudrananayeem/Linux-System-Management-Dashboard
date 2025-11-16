#!/usr/bin/env python3
"""
Process management module for web dashboard
"""

import psutil
import subprocess

class ProcessManager:
    def get_all_processes(self):
        """Get list of all running processes"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status']):
                processes.append(proc.info)
            return sorted(processes, key=lambda x: x['cpu_percent'] or 0, reverse=True)
        except Exception as e:
            return {'error': str(e)}
    
    def search_processes(self, query):
        """Search processes by name or PID"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
                if (query.lower() in proc.info['name'].lower() or 
                    query == str(proc.info['pid'])):
                    processes.append(proc.info)
            return processes
        except Exception as e:
            return {'error': str(e)}
    
    def kill_process(self, pid):
        """Kill a process by PID"""
        try:
            process = psutil.Process(pid)
            process_name = process.name()
            process.terminate()  # Graceful termination first
            return {'success': True, 'message': f'Process {process_name} (PID: {pid}) terminated'}
        except psutil.NoSuchProcess:
            return {'success': False, 'error': f'Process with PID {pid} not found'}
        except psutil.AccessDenied:
            return {'success': False, 'error': f'Access denied to terminate process {pid}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
