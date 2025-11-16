#!/bin/bash

# Set window style and theme
export GTK_THEME="Adwaita"

# Function to display welcome message
show_welcome() {
    zenity --info \
        --title="🚀 Welcome to LSMD System Manager" \
        --text="<span font='12'><b>LSMD - Linux System Management Dashboard</b></span>\n\n\
A comprehensive system management tool with:\n\
• Process monitoring and management\n\
• Disk space and health analysis\n\
• Backup and restore operations\n\
• Real-time system health metrics\n\
• User account management\n\n\
<span font='10'>Select a module to begin...</span>" \
        --width=450 \
        --height=300 \
        --icon-name=system-run
}

# Function to show system info in header
get_system_status() {
    local cpu_usage=$(mpstat 1 1 | tail -1 | awk '{printf "%.1f%%", 100 - $12}')
    local memory_usage=$(free | awk 'NR==2{printf "%.1f%%", $3*100/$2}')
    local disk_usage=$(df / | awk 'NR==2{printf "%.1f%%", $5}')
    local uptime=$(uptime -p | sed 's/up //')
    
    echo "🖥️ CPU: $cpu_usage | 🧠 Memory: $memory_usage | 💾 Disk: $disk_usage | ⏰ Uptime: $uptime"
}

# Function to create main menu
show_main_menu() {
    while true; do
        choice=$(zenity --list \
            --title="🏠 LSMD - System Management Dashboard" \
            --text="<span font='11'><b>$(get_system_status)</b></span>\n\n\
<span font='10'>Select a management module:</span>" \
            --width=650 \
            --height=450 \
            --ok-label="Open Module" \
            --cancel-label="Exit System" \
            --column="Module" \
            --column="Description" \
            --column="Icon" \
            "📊 Process Manager" "Monitor and manage running processes" "system-run" \
            "💿 Disk Monitor" "Analyze disk usage and health" "drive-harddisk" \
            "💾 Backup Module" "Backup and restore files" "document-save" \
            "❤️ System Health" "Real-time system metrics" "computer" \
            "👥 User Management" "Manage user accounts" "system-users" \
            "🔧 System Info" "Detailed system information" "dialog-information" \
            "🔄 Refresh" "Update system status" "view-refresh")
        
        case $choice in
            "📊 Process Manager")
                zenity --info --title="Launching..." --text="Opening Process Manager..." --timeout=1 --width=200
                bash modules/process_manager.sh
                ;;
            "💿 Disk Monitor")
                zenity --info --title="Launching..." --text="Opening Disk Monitor..." --timeout=1 --width=200
                bash modules/disk_monitor.sh
                ;;
            "💾 Backup Module")
                zenity --info --title="Launching..." --text="Opening Backup Module..." --timeout=1 --width=200
                bash modules/backup_module.sh
                ;;
            "❤️ System Health")
                zenity --info --title="Launching..." --text="Opening System Health Monitor..." --timeout=1 --width=200
                bash modules/health_monitor.sh
                ;;
            "👥 User Management")
                zenity --info --title="Launching..." --text="Opening User Management..." --timeout=1 --width=200
                bash modules/user_management.sh
                ;;
            "🔧 System Info")
                show_system_info
                ;;
            "🔄 Refresh")
                # Just continue to refresh the menu
                continue
                ;;
            *)
                if zenity --question \
                    --title="Exit LSMD Dashboard" \
                    --text="Are you sure you want to exit the system manager?" \
                    --width=400 \
                    --ok-label="Exit" \
                    --cancel-label="Cancel"; then
                    zenity --info \
                        --title="Thank You" \
                        --text="Thank you for using LSMD System Manager! 👋" \
                        --width=300 \
                        --timeout=2
                    exit 0
                fi
                ;;
        esac
    done
}

# Function to show detailed system information
show_system_info() {
    local hostname=$(hostname)
    local os_info=$(lsb_release -d | cut -f2)
    local kernel=$(uname -r)
    local architecture=$(uname -m)
    local cpu_model=$(grep "model name" /proc/cpuinfo | head -1 | cut -d: -f2 | sed 's/^ *//')
    local cpu_cores=$(nproc)
    local total_memory=$(free -h | grep Mem | awk '{print $2}')
    local total_disk=$(df -h / | awk 'NR==2{print $2}')
    local users_logged_in=$(who | wc -l)
    local current_user=$(whoami)
    
    zenity --text-info \
        --title="🔧 System Information - $hostname" \
        --width=700 \
        --height=500 \
        --font="monospace 9" \
        --text="<b>=== SYSTEM INFORMATION ===</b>

<b>Operating System:</b>
• Distribution: $os_info
• Kernel Version: $kernel
• Architecture: $architecture

<b>Hardware Information:</b>
• CPU: $cpu_model
• Cores/Threads: $cpu_cores
• Total Memory: $total_memory
• Root Disk Size: $total_disk

<b>System Status:</b>
• Current User: $current_user
• Users Logged In: $users_logged_in
• System Uptime: $(uptime -p | sed 's/up //')
• Load Average: $(uptime | awk -F'load average:' '{print $2}')

<b>Network Information:</b>
• Hostname: $hostname
• IP Address: $(hostname -I | awk '{print $1}')

<b>Storage Overview:</b>
$(df -h / /home /boot 2>/dev/null | awk 'NR==1 || /^\/dev/ {print "• " $1 ": " $3 " used of " $2 " (" $5 ")"}')

<b>Memory Usage:</b>
$(free -h | awk 'NR<=2 {print "• " $0}' | sed 's/Total/Total:/' | sed 's/Used/Used:/')"
}

# Function to check if required commands are available
check_dependencies() {
    local missing=()
    local commands=("zenity" "mpstat" "free" "df" "uptime")
    
    for cmd in "${commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            missing+=("$cmd")
        fi
    done
    
    if [ ${#missing[@]} -gt 0 ]; then
        zenity --warning \
            --title="Missing Dependencies" \
            --text="The following commands are missing:\n\n• ${missing[*]}\n\nSome features may not work properly." \
            --width=400
        return 1
    fi
    return 0
}

# Function to show about dialog
show_about() {
    zenity --info \
        --title="About LSMD Dashboard" \
        --text="<span font='13'><b>LSMD Dashboard</b></span>\n\n\
<span font='10'>Version 2.0 - Enhanced GUI Edition\n\n\
A comprehensive Linux system management tool\nwith modern graphical interface.\n\n\
Features:\n\
• Process monitoring and management\n\
• Disk space analysis and health checks\n\
• Backup and restore functionality\n\
• Real-time system metrics\n\
• User account administration\n\n\
</span><span font='9'>Built with Bash and Zenity</span>" \
        --width=450 \
        --height=350 \
        --icon-name=system-software-install
}

# Main execution flow
main() {
    # Check if we're in the right directory
    if [ ! -d "modules" ]; then
        zenity --error \
            --title="Directory Error" \
            --text="Please run this script from the main LSMD directory.\nThe 'modules' folder was not found." \
            --width=400
        exit 1
    fi
    
    # Check dependencies
    check_dependencies
    
    # Show welcome message on first run
    if [ ! -f "$HOME/.lsmd_welcome_shown" ]; then
        show_welcome
        touch "$HOME/.lsmd_welcome_shown"
    fi
    
    # Show about dialog occasionally (1 in 4 chance)
    if [ $((RANDOM % 4)) -eq 0 ]; then
        show_about
    fi
    
    # Start main menu loop
    show_main_menu
}

# Trap Ctrl+C to show nice exit message
trap 'zenity --info --text="👋 Goodbye!" --timeout=1 --width=200; exit 0' INT

# Start the application
main