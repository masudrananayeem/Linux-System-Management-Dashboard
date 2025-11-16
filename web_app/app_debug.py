#!/usr/bin/env python3
"""
LSMD Debug Version - Simple and working
"""

from flask import Flask, render_template, jsonify, request
import subprocess
import json
import os
import psutil
from datetime import datetime

app = Flask(__name__)

def run_shell_command(cmd):
    """Run shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

@app.route('/')
def index():
    return '''
    <html>
    <head>
        <title>LSMD Debug</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-4">
            <h1>LSMD Debug Dashboard</h1>
            
            <div class="row mt-4">
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-header">System Info</div>
                        <div class="card-body" id="system-info">
                            Loading...
                        </div>
                    </div>
                </div>
                
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-header">Processes</div>
                        <div class="card-body" id="process-list">
                            Loading...
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">Debug Info</div>
                        <div class="card-body" id="debug-info">
                            Loading...
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            async function loadSystemInfo() {
                const response = await fetch('/api/system-info');
                const data = await response.json();
                document.getElementById('system-info').innerHTML = `
                    <strong>CPU:</strong> ${data.cpu_percent}%<br>
                    <strong>Memory:</strong> ${data.memory_percent}%<br>
                    <strong>Disk:</strong> ${data.disk_usage}%<br>
                    <strong>Uptime:</strong> ${data.uptime}
                `;
            }
            
            async function loadProcesses() {
                const response = await fetch('/api/processes');
                const data = await response.json();
                
                let html = '<table class="table table-sm"><tr><th>PID</th><th>Name</th><th>CPU%</th><th>Memory%</th></tr>';
                data.forEach(proc => {
                    html += `<tr><td>${proc.pid}</td><td>${proc.name}</td><td>${proc.cpu_percent}</td><td>${proc.memory_percent}</td></tr>`;
                });
                html += '</table>';
                document.getElementById('process-list').innerHTML = html;
            }
            
            async function loadDebugInfo() {
                const response = await fetch('/api/debug');
                const data = await response.json();
                document.getElementById('debug-info').innerHTML = `
                    <strong>Scripts Directory:</strong> ${data.scripts_dir}<br>
                    <strong>Processes Script:</strong> ${data.processes_script}<br>
                    <strong>Script Output:</strong> <pre>${data.script_output}</pre>
                `;
            }
            
            // Load all data
            loadSystemInfo();
            loadProcesses();
            loadDebugInfo();
            
            // Refresh every 5 seconds
            setInterval(loadSystemInfo, 5000);
            setInterval(loadProcesses, 5000);
        </script>
    </body>
    </html>
    '''

@app.route('/api/system-info')
def api_system_info():
    """Get system info using Python psutil"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        return jsonify({
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'disk_usage': disk.percent,
            'uptime': str(uptime).split('.')[0],
            'hostname': run_shell_command('hostname')
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/processes')
def api_processes():
    """Get processes - try shell script first, then fallback to Python"""
    try:
        # Try to use the shell script
        script_path = 'modules/processes.sh'
        if os.path.exists(script_path):
            result = subprocess.run([script_path, 'list'], capture_output=True, text=True)
            if result.returncode == 0:
                processes = json.loads(result.stdout)
                return jsonify(processes)
        
        # Fallback to Python implementation
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu_percent': proc.info['cpu_percent'] or 0.0,
                    'memory_percent': proc.info['memory_percent'] or 0.0
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Return top 20 by CPU usage
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        return jsonify(processes[:20])
        
    except Exception as e:
        return jsonify([{'error': str(e)}])

@app.route('/api/debug')
def api_debug():
    """Debug information"""
    scripts_dir = os.listdir('modules') if os.path.exists('modules') else 'No modules directory'
    processes_script = 'Exists' if os.path.exists('modules/processes.sh') else 'Missing'
    
    # Test the processes script
    script_output = "Not tested"
    if os.path.exists('modules/processes.sh'):
        try:
            result = subprocess.run(['./modules/processes.sh', 'list'], capture_output=True, text=True)
            script_output = f"Return code: {result.returncode}\nOutput: {result.stdout}\nError: {result.stderr}"
        except Exception as e:
            script_output = f"Error: {e}"
    
    return jsonify({
        'scripts_dir': str(scripts_dir),
        'processes_script': processes_script,
        'script_output': script_output
    })

if __name__ == '__main__':
    print("Starting LSMD Debug Dashboard...")
    print("Available at: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
