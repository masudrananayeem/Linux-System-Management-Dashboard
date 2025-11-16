#!/bin/bash

ACTION="$1"
PARAM="$2"
BACKUP_DIR="$HOME/backups"

mkdir -p "$BACKUP_DIR"

case "$ACTION" in
    "create")
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.tar.gz"
        
        # Create backup of home directory, excluding large cache files
        tar --exclude='./.cache' --exclude='./.local/share/Trash' -czf "$BACKUP_FILE" -C ~ . 2>/dev/null
        
        if [ $? -eq 0 ]; then
            SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
            echo "{\"status\": \"success\", \"message\": \"Backup created\", \"file\": \"$BACKUP_FILE\", \"size\": \"$SIZE\", \"timestamp\": \"$TIMESTAMP\"}"
        else
            echo "{\"status\": \"error\", \"message\": \"Backup failed\"}"
        fi
        ;;
    "list")
        # List backups in JSON format
        ls -la "$BACKUP_DIR"/*.tar.gz 2>/dev/null | awk '
        BEGIN {print "["; first=1}
        {
            if(!first) printf ",\n"
            first=0
            split($6 " " $7 " " $8, date)
            printf "  {\"name\": \"%s\", \"size\": \"%s\", \"date\": \"%s %s %s\"}", $9, $5, date[1], date[2], date[3]
        }
        END {print "\n]"}'
        
        if [ $? -ne 0 ]; then
            echo "[]"
        fi
        ;;
    "restore")
        if [ -n "$PARAM" ] && [ -f "$PARAM" ]; then
            tar -xzf "$PARAM" -C / 2>/dev/null
            if [ $? -eq 0 ]; then
                echo "{\"status\": \"success\", \"message\": \"Backup restored\"}"
            else
                echo "{\"status\": \"error\", \"message\": \"Restore failed\"}"
            fi
        else
            echo "{\"status\": \"error\", \"message\": \"Backup file not found\"}"
        fi
        ;;
    *)
        echo "{\"status\": \"error\", \"message\": \"Unknown action: $ACTION\"}"
        ;;
esac