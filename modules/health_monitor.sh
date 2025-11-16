#!/bin/bash

ACTION="$1"

case "$ACTION" in
    "info")
        # Get comprehensive system information
        CPU_USAGE=$(mpstat 1 1 | awk 'NR==4 {printf "%.1f", 100 - $12}')
        MEMORY_INFO=$(free | awk 'NR==2 {printf "{\"total\": %d, \"used\": %d, \"free\": %d, \"percent\": %.1f}", $2, $3, $4, $3*100/$2}')
        DISK_INFO=$(df / | awk 'NR==2 {printf "{\"total\": \"%s\", \"used\": \"%s\", \"free\": \"%s\", \"percent\": \"%s\"}", $2, $3, $4, $5}')
        UPTIME=$(uptime -p | sed 's/up //')
        LOAD_AVG=$(uptime | awk -F'load average:' '{print $2}' | sed 's/^ *//')
        
        echo "{
          \"cpu_usage\": $CPU_USAGE,
          \"memory\": $MEMORY_INFO,
          \"disk\": $DISK_INFO,
          \"uptime\": \"$UPTIME\",
          \"load_avg\": \"$LOAD_AVG\",
          \"hostname\": \"$(hostname)\",
          \"users\": $(who | wc -l),
          \"timestamp\": \"$(date '+%Y-%m-%d %H:%M:%S')\"
        }"
        ;;
    "detailed")
        # More detailed system information
        echo "{
          \"cpu_cores\": $(nproc),
          \"cpu_model\": \"$(grep 'model name' /proc/cpuinfo | head -1 | cut -d: -f2 | sed 's/^ *//')\",
          \"memory_total\": $(free -b | awk 'NR==2 {print $2}'),
          \"disk_total\": $(df -B1 / | awk 'NR==2 {print $2}'),
          \"os\": \"$(lsb_release -d | cut -f2)\",
          \"kernel\": \"$(uname -r)\",
          \"architecture\": \"$(uname -m)\"
        }"
        ;;
    "services")
        # List running services (if systemd is available)
        if command -v systemctl >/dev/null 2>&1; then
            systemctl list-units --type=service --state=running --no-legend | head -10 | awk '
            BEGIN {print "["; first=1}
            {
                if(!first) printf ",\n"
                first=0
                printf "  {\"name\": \"%s\", \"status\": \"%s\"}", $1, $3
            }
            END {print "\n]"}'
        else
            echo "[]"
        fi
        ;;
    *)
        echo "{\"status\": \"error\", \"message\": \"Unknown action: $ACTION\"}"
        ;;
esac