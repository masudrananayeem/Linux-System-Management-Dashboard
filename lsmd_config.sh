#!/bin/bash

# LSMD Dashboard Configuration
# This file contains styling and configuration options

# Color scheme
export GTK_THEME="Adwaita"

# Window settings
WINDOW_WIDTH=650
WINDOW_HEIGHT=450
TEXT_FONT="monospace 9"

# Module paths
MODULES_DIR="./modules"
BACKUP_DIR="$HOME/backups"

# UI Settings
SHOW_WELCOME=true
SHOW_SYSTEM_STATUS=true
AUTO_REFRESH_INTERVAL=30  # seconds

# Feature toggles
ENABLE_PROCESS_MONITOR=true
ENABLE_DISK_MONITOR=true
ENABLE_BACKUP_MODULE=true
ENABLE_HEALTH_MONITOR=true
ENABLE_USER_MANAGEMENT=true

# Notification settings
SHOW_SUCCESS_NOTIFICATIONS=true
SHOW_ERROR_NOTIFICATIONS=true
NOTIFICATION_TIMEOUT=3

# Function to apply styles
apply_styles() {
    echo "Applying LSMD styles..."
}

# Function to validate module existence
validate_modules() {
    local modules=("process_manager.sh" "disk_monitor.sh" "backup_module.sh" 
                   "health_monitor.sh" "user_management.sh")
    
    for module in "${modules[@]}"; do
        if [ ! -f "$MODULES_DIR/$module" ]; then
            zenity --warning \
                --title="Module Missing" \
                --text="Module $module not found in $MODULES_DIR"
            return 1
        fi
    done
    return 0
}
