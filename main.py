#!/usr/bin/env python3
"""
LSMD Web Dashboard Launcher
Simple version to get started
"""

import os
import sys
import webbrowser
import threading
import time

def check_dependencies():
    """Check if required Python packages are installed"""
    try:
        import flask
        import psutil
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install with: pip3 install flask psutil")
        return False

def main():
    print("🚀 Starting LSMD Web Dashboard...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Import and run the app
    try:
        from web_app.app import app
        
        # Open browser after delay
        def open_browser():
            time.sleep(2)
            webbrowser.open('http://localhost:5000')
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        print("🌐 Web dashboard starting at: http://localhost:5000")
        print("⏹️  Press Ctrl+C to stop the server")
        print("=" * 50)
        
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except Exception as e:
        print(f"❌ Error starting web server: {e}")
        print("Trying to fix app.py...")
        fix_app_py()
        sys.exit(1)

def fix_app_py():
    """Create a fixed version of app.py"""
    fixed_content = '''#!/usr/bin/env python3
"""
LSMD Web Dashboard - Flask Backend
Fixed version
"""

from flask import Flask, render_template, jsonify, request
import sys
import os
import subprocess
import psutil
from datetime import datetime

app = Flask(__name__)

class SystemManager:
    """System manager for web dashboard"""
    
    def get_system_info(self):
        try:
            # CPU information
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_cores = psutil.cpu_count()
            
            # Memory information
            memory = psutil.virtual_memory()
            
            # Disk information
            disk = psutil.disk_usage('/')
            
            # System information
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            info = {
                'hostname': subprocess.getoutput('hostname'),
                'cpu_percent': cpu_percent,
                'cpu_cores': cpu_cores,
                'memory_percent': memory.percent,
                'memory_total': self._bytes_to_gb(memory.total),
                'memory_used': self._bytes_to_gb(memory.used),
                'disk_usage': disk.percent,
                'disk_total': self._bytes_to_gb(disk.total),
                'disk_used': self._bytes_to_gb(disk.used),
                'uptime': str(uptime).split('.')[0],
                'load_avg': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0],
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            return info
        except Exception as e:
            return {'error': str(e)}

    def get_process_list(self):
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    process_info = proc.info
                    process_info['cpu_percent'] = process_info['cpu_percent'] or 0.0
                    process_info['memory_percent'] = process_info['memory_percent'] or 0.0
                    processes.append(process_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            return processes[:50]
        except Exception as e:
            return {'error': str(e)}

    def get_disk_info(self):
        try:
            disks = []
            for partition in psutil.disk_partitions():
                if partition.fstype in ['squashfs', 'tmpfs', 'devtmpfs', 'overlay']:
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
                        'percent': usage.percent
                    })
                except (PermissionError, FileNotFoundError):
                    continue
            
            return disks
        except Exception as e:
            return {'error': str(e)}

    def _bytes_to_gb(self, bytes):
        return round(bytes / (1024 ** 3), 2)

    def _bytes_to_human(self, bytes):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes < 1024.0:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024.0
        return f"{bytes:.2f} PB"

system_manager = SystemManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/system-info')
def api_system_info():
    data = system_manager.get_system_info()
    return jsonify(data)

@app.route('/api/processes')
def api_processes():
    data = system_manager.get_process_list()
    return jsonify(data)

@app.route('/api/disk-info')
def api_disk_info():
    data = system_manager.get_disk_info()
    return jsonify(data)

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    print("Starting LSMD Web Dashboard...")
    print("Dashboard available at: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
'''

    # Write fixed app.py
    app_py_path = os.path.join('web_app', 'app.py')
    os.makedirs('web_app', exist_ok=True)
    
    with open(app_py_path, 'w') as f:
        f.write(fixed_content)
    
    print("✅ Fixed app.py created")
    print("Please run: python3 main.py again")

if __name__ == '__main__':
    main()
