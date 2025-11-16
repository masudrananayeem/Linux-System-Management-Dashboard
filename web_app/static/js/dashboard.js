// Complete Dashboard JavaScript
class LSMDDashboard {
    constructor() {
        this.updateInterval = 2000;
        this.init();
    }

    init() {
        this.updateSystemInfo();
        this.loadProcesses();
        this.loadDiskInfo();
        this.loadBackups();
        this.loadUsers();
        this.loadLargeFiles();
        
        setInterval(() => this.updateSystemInfo(), this.updateInterval);
        setInterval(() => this.updateTime(), 1000);
        setInterval(() => this.loadProcesses(), 10000);
    }

    updateTime() {
        document.getElementById('current-time').textContent = new Date().toLocaleString();
    }

    async updateSystemInfo() {
        try {
            const response = await fetch('/api/system-info');
            const data = await response.json();
            
            if (data.error) {
                console.error('Error:', data.error);
                return;
            }

            document.getElementById('cpu-usage').textContent = data.cpu_percent.toFixed(1) + '%';
            document.getElementById('memory-usage').textContent = data.memory_percent.toFixed(1) + '%';
            document.getElementById('disk-usage').textContent = data.disk_usage.toFixed(1) + '%';
            document.getElementById('uptime').textContent = data.uptime;
            document.getElementById('load-avg').textContent = data.load_avg[0].toFixed(2);
            document.getElementById('hostname').textContent = data.hostname;
            document.getElementById('memory-used').textContent = data.memory_used_gb + ' GB / ' + data.memory_total_gb + ' GB';
            document.getElementById('disk-used').textContent = data.disk_used_gb + ' GB / ' + data.disk_total_gb + ' GB';

            this.updateGauge('cpu-usage', data.cpu_percent);
            this.updateGauge('memory-usage', data.memory_percent);
            this.updateGauge('disk-usage', data.disk_usage);

        } catch (error) {
            console.error('Failed to fetch system info:', error);
        }
    }

    updateGauge(elementId, value) {
        const element = document.getElementById(elementId);
        const card = element.closest('.card');
        
        card.classList.remove('bg-danger', 'bg-warning', 'bg-success');
        
        if (value > 80) {
            card.classList.add('bg-danger');
        } else if (value > 60) {
            card.classList.add('bg-warning');
        } else {
            card.classList.add('bg-success');
        }
    }

    async loadProcesses() {
        try {
            const response = await fetch('/api/processes');
            const processes = await response.json();
            
            const tbody = document.getElementById('process-list');
            tbody.innerHTML = '';

            if (processes.error) {
                tbody.innerHTML = `<tr><td colspan="8" class="text-center text-danger">${processes.error}</td></tr>`;
                return;
            }

            document.getElementById('process-count').textContent = processes.length;

            processes.forEach(proc => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${proc.pid}</td>
                    <td>${proc.name}</td>
                    <td>${proc.username}</td>
                    <td>${proc.cpu_percent.toFixed(1)}%</td>
                    <td>${proc.memory_percent.toFixed(1)}%</td>
                    <td>${proc.memory_mb ? proc.memory_mb.toFixed(1) : '0.0'} MB</td>
                    <td><span class="badge bg-success">${proc.status}</span></td>
                    <td>
                        <button class="btn btn-sm btn-danger" onclick="killProcess(${proc.pid})" title="Kill Process">
                            <i class="fas fa-skull"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(row);
            });

        } catch (error) {
            console.error('Failed to fetch processes:', error);
        }
    }

    async loadDiskInfo() {
        try {
            const response = await fetch('/api/disk-info');
            const disks = await response.json();
            
            const tbody = document.getElementById('disk-list');
            tbody.innerHTML = '';

            disks.forEach(disk => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${disk.device}</td>
                    <td>${disk.mountpoint}</td>
                    <td>${disk.fstype}</td>
                    <td>${disk.total}</td>
                    <td>${disk.used}</td>
                    <td>${disk.free}</td>
                    <td>
                        <div class="progress">
                            <div class="progress-bar ${disk.percent > 80 ? 'bg-danger' : disk.percent > 60 ? 'bg-warning' : ''}" 
                                 style="width: ${disk.percent}%">
                                ${disk.percent}%
                            </div>
                        </div>
                    </td>
                `;
                tbody.appendChild(row);
            });

        } catch (error) {
            console.error('Failed to fetch disk info:', error);
        }
    }

    async loadLargeFiles() {
        try {
            const response = await fetch('/api/large-files');
            const files = await response.json();
            
            const tbody = document.getElementById('large-files-list');
            tbody.innerHTML = '';

            if (files.error) {
                tbody.innerHTML = `<tr><td colspan="2" class="text-center text-danger">${files.error}</td></tr>`;
                return;
            }

            files.forEach(file => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${file.size}</td>
                    <td title="${file.path}">${file.path.length > 50 ? file.path.substring(0, 50) + '...' : file.path}</td>
                `;
                tbody.appendChild(row);
            });

        } catch (error) {
            console.error('Failed to fetch large files:', error);
        }
    }

    async loadBackups() {
        try {
            const response = await fetch('/api/backups');
            const backups = await response.json();
            
            const tbody = document.getElementById('backup-list');
            tbody.innerHTML = '';

            if (backups.error) {
                tbody.innerHTML = `<tr><td colspan="3" class="text-center text-danger">${backups.error}</td></tr>`;
                return;
            }

            backups.forEach(backup => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${backup.name}</td>
                    <td>${backup.size}</td>
                    <td>${backup.modified}</td>
                `;
                tbody.appendChild(row);
            });

        } catch (error) {
            console.error('Failed to fetch backups:', error);
        }
    }

    async loadUsers() {
        try {
            const response = await fetch('/api/users');
            const users = await response.json();
            
            const tbody = document.getElementById('user-list');
            tbody.innerHTML = '';

            if (users.error) {
                tbody.innerHTML = `<tr><td colspan="7" class="text-center text-danger">${users.error}</td></tr>`;
                return;
            }

            users.forEach(user => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${user.username}</td>
                    <td>${user.uid}</td>
                    <td>${user.gid}</td>
                    <td>${user.home}</td>
                    <td>${user.shell}</td>
                    <td>${user.gecos}</td>
                    <td>
                        <button class="btn btn-sm btn-danger" onclick="deleteUser('${user.username}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>