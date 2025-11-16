#!/bin/bash

ACTION="$1"

case "$ACTION" in
    "info")
        # Get real system information
        CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}')
        MEMORY_TOTAL=$(free -b | awk 'NR==2 {print $2}')
        MEMORY_USED=$(free -b | awk 'NR==2 {print $3}')
        MEMORY_PERCENT=$(free | awk 'NR==2 {printf "%.1f", $3*100/$2}')
        
        # Get real disk information
        DISK_TOTAL=$(df -B1 / | awk 'NR==2 {print $2}')
        DISK_USED=$(df -B1 / | awk 'NR==2 {print $3}')
        DISK_PERCENT=$(df / | awk 'NR==2 {sub(/%/, "", $5); print $5}')
        
        UPTIME=$(uptime -p | sed 's/up //')
        LOAD_AVG=$(uptime | awk -F'load average:' '{print $2}' | sed 's/^ *//')
        HOSTNAME=$(hostname)
        USERS=$(who | wc -l)
        CPU_CORES=$(nproc)
        TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
        
        echo "{
          \"cpu_usage\": $CPU_USAGE,
          \"cpu_cores\": $CPU_CORES,
          \"memory\": {
            \"total\": $MEMORY_TOTAL,
            \"used\": $MEMORY_USED,
            \"free\": $(($MEMORY_TOTAL - $MEMORY_USED)),
            \"percent\": $MEMORY_PERCENT
          },
          \"disk\": {
            \"total\": $DISK_TOTAL,
            \"used\": $DISK_USED,
            \"free\": $(($DISK_TOTAL - $DISK_USED)),
            \"percent\": $DISK_PERCENT
          },
          \"uptime\": \"$UPTIME\",
          \"load_avg\": \"$LOAD_AVG\",
          \"hostname\": \"$HOSTNAME\",
          \"users\": $USERS,
          \"timestamp\": \"$TIMESTAMP\"
        }"
        ;;
    *)
        echo "{\"status\": \"error\", \"message\": \"Unknown action: $ACTION\"}"
        ;;
esac