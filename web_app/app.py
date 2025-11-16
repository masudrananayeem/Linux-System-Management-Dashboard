#!/usr/bin/env python3
"""
LSMD Web Dashboard - Flask Backend using Shell Scripts
Updated with System Health endpoint and better error handling
"""

from flask import Flask, render_template, jsonify, request
import subprocess
import json
import os
import psutil
from datetime import datetime

app = Flask(__name__)

class ShellSystemManager:
    def __init__(self):
        self.modules_dir = "modules"
    
    def run_module(self, module, action, param=None):
        """Execute a module script and return JSON result"""
        try:
            script_path = os.path.join(self.modules_dir, f"{module}.sh")
            if not os.path.exists(script_path):
                return {'error': f'Module {module} not found'}
            
            # Make sure script is executable
            os.chmod(script_path, 0o755)
            
            cmd = [script_path, action]
            if param:
                cmd.append(str(param))
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            print(f"Running: {' '.join(cmd)}")  # Debug
            print(f"Output: {result.stdout}")   # Debug
            if result.stderr:
                print(f"Error: {result.stderr}")    # Debug
            
            if result.returncode == 0:
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError as e:
                    return {'error': f'Invalid JSON from module: {e}', 'raw_output': result.stdout}
            else:
                return {'error': result.stderr or 'Module execution failed'}
                
        except subprocess.TimeoutExpired:
            return {'error': 'Module execution timed out'}
        except Exception as e:
            return {'error': str(e)}
    
    # System Information
    def get_system_info(self):
        # Use the system.sh script
        result = self.run_module('system', 'info')
        if 'error' in result:
            # Fallback to direct Python implementation
            return self._get_system_info_fallback()
        return self._convert_system_info(result)
    
    def _get_system_info_fallback(self):
        """Fallback system info using Python"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            return {
                'cpu_usage': cpu_percent,
                'cpu_cores': psutil.cpu_count(),
                'memory': {
                    'total': memory.total,
                    'used': memory.used,
                    'free': memory.available,
                    'percent': memory.percent
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.percent
                },
                'uptime': str(uptime).split('.')[0],
                'load_avg': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0],
                'hostname': subprocess.getoutput('hostname'),
                'users': len(psutil.users()),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _convert_system_info(self, data):
        """Convert system info to consistent format"""
        if 'error' in data:
            return data
        
        # Convert bytes to GB for frontend
        if 'memory' in data and isinstance(data['memory'], dict):
            memory = data['memory']
            data['memory_total_gb'] = self._bytes_to_gb(memory.get('total', 0))
            data['memory_used_gb'] = self._bytes_to_gb(memory.get('used', 0))
            data['memory_percent'] = memory.get('percent', 0)
        
        if 'disk' in data and isinstance(data['disk'], dict):
            disk = data['disk']
            data['disk_total_gb'] = self._bytes_to_gb(disk.get('total', 0))
            data['disk_used_gb'] = self._bytes_to_gb(disk.get('used', 0))
            data['disk_usage'] = disk.get('percent', 0)
        
        # Ensure all required fields exist
        data['cpu_percent'] = data.get('cpu_usage', 0)
        
        return data

    # Process Management
    def get_process_list(self):
        result = self.run_module('processes', 'list')
        if 'error' in result:
            return self._get_process_list_fallback()
        return result
    
    def _get_process_list_fallback(self):
        """Fallback process list using Python"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status', 'memory_info']):
                try:
                    process_info = proc.info
                    processes.append({
                        'pid': process_info['pid'],
                        'user': process_info['username'],
                        'cpu': process_info['cpu_percent'] or 0.0,
                        'memory': process_info['memory_percent'] or 0.0,
                        'name': process_info['name'],
                        'status': process_info['status']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            processes.sort(key=lambda x: x['cpu'], reverse=True)
            return processes[:20]
        except Exception as e:
            return {'error': str(e)}
    
    def kill_process(self, pid):
        return self.run_module('processes', 'kill', pid)
    
    # Disk Management
    def get_disk_info(self):
        result = self.run_module('disk', 'usage')
        if 'error' in result:
            return self._get_disk_info_fallback()
        return result
    
    def _get_disk_info_fallback(self):
        """Fallback disk info using Python"""
        try:
            disks = []
            for partition in psutil.disk_partitions():
                if partition.fstype in ['squashfs', 'tmpfs', 'devtmpfs']:
                    continue
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disks.append({
                        'filesystem': partition.device,
                        'size': self._bytes_to_human(usage.total),
                        'used': self._bytes_to_human(usage.used),
                        'available': self._bytes_to_human(usage.free),
                        'use_percent': f"{usage.percent}%",
                        'mounted': partition.mountpoint
                    })
                except PermissionError:
                    continue
            return disks
        except Exception as e:
            return {'error': str(e)}
    
    def get_large_files(self):
        result = self.run_module('disk', 'large_files')
        if 'error' in result:
            return self._get_large_files_fallback()
        return result
    
    def _get_large_files_fallback(self):
        """Fallback large files using Python"""
        try:
            large_files = []
            # Simple implementation to find large files
            for root, dirs, files in os.walk(os.path.expanduser('~')):
                for file in files:
                    if len(large_files) >= 10:
                        break
                    try:
                        filepath = os.path.join(root, file)
                        size = os.path.getsize(filepath)
                        if size > 100 * 1024 * 1024:  # 100MB
                            large_files.append({
                                'size': self._bytes_to_human(size),
                                'file': filepath
                            })
                    except (OSError, PermissionError):
                        continue
            return large_files
        except Exception as e:
            return {'error': str(e)}
    
    # Backup Management
    def create_backup(self):
        return self.run_module('backup', 'create')
    
    def list_backups(self):
        result = self.run_module('backup', 'list')
        if 'error' in result or not result:
            return []
        return result
    
    # User Management
    def get_users(self):
        result = self.run_module('users', 'list')
        if 'error' in result:
            return self._get_users_fallback()
        return result
    
    def _get_users_fallback(self):
        """Fallback users list using Python"""
        try:
            users = []
            result = subprocess.run(['getent', 'passwd'], capture_output=True, text=True)
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split(':')
                    if len(parts) >= 7:
                        uid = int(parts[2])
                        if uid >= 1000 and uid < 65534:
                            users.append({
                                'username': parts[0],
                                'uid': uid,
                                'gid': int(parts[3]),
                                'home': parts[5],
                                'shell': parts[6],
                                'gecos': parts[4]
                            })
            return users
        except Exception as e:
            return {'error': str(e)}
    
    def create_user(self, username):
        return self.run_module('users', 'add', username)
    
    def delete_user(self, username):
        return self.run_module('users', 'delete', username)
    
    # System Health - Comprehensive system information
    def get_system_health(self):
        """Get comprehensive system health information"""
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
            disk_io = psutil.disk_io_counters()
            
            # Network information
            net_io = psutil.net_io_counters()
            
            # System information
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            health_data = {
                'cpu': {
                    'percent': cpu_percent,
                    'cores': cpu_cores,
                    'frequency': {
                        'current': cpu_freq.current if cpu_freq else 0,
                        'max': cpu_freq.max if cpu_freq else 0
                    }
                },
                'memory': {
                    'total': self._bytes_to_gb(memory.total),
                    'used': self._bytes_to_gb(memory.used),
                    'free': self._bytes_to_gb(memory.available),
                    'percent': memory.percent,
                    'swap_total': self._bytes_to_gb(swap.total),
                    'swap_used': self._bytes_to_gb(swap.used),
                    'swap_percent': swap.percent
                },
                'disk': {
                    'total': self._bytes_to_gb(disk.total),
                    'used': self._bytes_to_gb(disk.used),
                    'free': self._bytes_to_gb(disk.free),
                    'percent': disk.percent,
                    'read_bytes': disk_io.read_bytes if disk_io else 0,
                    'write_bytes': disk_io.write_bytes if disk_io else 0
                },
                'network': {
                    'bytes_sent': net_io.bytes_sent if net_io else 0,
                    'bytes_recv': net_io.bytes_recv if net_io else 0
                },
                'system': {
                    'uptime': str(uptime).split('.')[0],
                    'boot_time': boot_time.isoformat(),
                    'load_avg': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
                },
                'timestamp': datetime.now().isoformat()
            }
            
            return health_data
            
        except Exception as e:
            return {'error': str(e)}
    
    # Utility functions
    def _bytes_to_gb(self, bytes):
        return round(bytes / (1024 ** 3), 2)
    
    def _bytes_to_mb(self, bytes):
        return round(bytes / (1024 ** 2), 2)
    
    def _bytes_to_human(self, bytes):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes < 1024.0:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024.0
        return f"{bytes:.2f} PB"

system_manager = ShellSystemManager()

# Routes
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

@app.route('/api/kill-process', methods=['POST'])
def api_kill_process():
    data = request.get_json()
    pid = data.get('pid')
    if not pid:
        return jsonify({'status': 'error', 'message': 'No PID specified'})
    result = system_manager.kill_process(pid)
    return jsonify(result)

@app.route('/api/disk-info')
def api_disk_info():
    data = system_manager.get_disk_info()
    return jsonify(data)

@app.route('/api/large-files')
def api_large_files():
    data = system_manager.get_large_files()
    return jsonify(data)

@app.route('/api/backups')
def api_backups():
    data = system_manager.list_backups()
    return jsonify(data)

@app.route('/api/create-backup', methods=['POST'])
def api_create_backup():
    result = system_manager.create_backup()
    return jsonify(result)

@app.route('/api/users')
def api_users():
    data = system_manager.get_users()
    return jsonify(data)

@app.route('/api/users/current')
def api_current_user():
    """Get current user information"""
    try:
        import getpass
        import pwd
        current_user = getpass.getuser()
        user_info = pwd.getpwnam(current_user)
        
        return jsonify({
            'username': current_user,
            'uid': user_info.pw_uid,
            'gid': user_info.pw_gid,
            'home': user_info.pw_dir,
            'shell': user_info.pw_shell
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/create-user', methods=['POST'])
def api_create_user():
    data = request.get_json()
    username = data.get('username')
    
    if not username:
        return jsonify({'status': 'error', 'message': 'No username specified'})
    
    # Validate username format
    if not re.match(r'^[a-z_][a-z0-9_-]*$', username):
        return jsonify({
            'status': 'error', 
            'message': 'Invalid username. Use only lowercase letters, numbers, underscores, and hyphens. Must start with a letter or underscore.'
        })
    
    # Check if user already exists
    try:
        import pwd
        pwd.getpwnam(username)
        return jsonify({'status': 'error', 'message': f'User {username} already exists'})
    except KeyError:
        pass  # User doesn't exist, good to proceed
    
    result = system_manager.create_user(username)
    return jsonify(result)

@app.route('/api/delete-user', methods=['POST'])
def api_delete_user():
    data = request.get_json()
    username = data.get('username')
    
    if not username:
        return jsonify({'status': 'error', 'message': 'No username specified'})
    
    # Prevent deletion of current user
    try:
        import getpass
        current_user = getpass.getuser()
        if username == current_user:
            return jsonify({'status': 'error', 'message': 'Cannot delete current user'})
    except:
        pass
    
    # Check if user exists
    try:
        import pwd
        pwd.getpwnam(username)
    except KeyError:
        return jsonify({'status': 'error', 'message': f'User {username} does not exist'})
    
    result = system_manager.delete_user(username)
    return jsonify(result)

@app.route('/api/system-health')
def api_system_health():
    """Get comprehensive system health information"""
    data = system_manager.get_system_health()
    return jsonify(data)

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("Starting LSMD Web Dashboard with Shell Modules...")
    print("Available at: http://localhost:5000")
    
    # Test if modules work
    print("Testing modules...")
    test_result = system_manager.run_module('processes', 'list')
    print(f"Processes test: {'Success' if 'error' not in test_result else 'Failed'}")
    
    # Test system info
    system_test = system_manager.get_system_info()
    print(f"System info test: {'Success' if 'error' not in system_test else 'Failed'}")
    
    # Test user module
    user_test = system_manager.run_module('users', 'list')
    print(f"Users test: {'Success' if 'error' not in user_test else 'Failed'}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)