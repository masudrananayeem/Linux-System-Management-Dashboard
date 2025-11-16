#!/bin/bash

ACTION="$1"
PARAM="$2"

case "$ACTION" in
    "list")
        # List all processes in JSON format
        echo "["
        ps -eo pid,user,%cpu,%mem,comm --sort=-%cpu | head -21 | tail -20 | awk '
        NR>1 {
            if(NR>2) printf ",\n"
            printf "  {\"pid\": %d, \"user\": \"%s\", \"cpu\": %.1f, \"memory\": %.1f, \"name\": \"%s\", \"status\": \"running\"}", $1, $2, $3, $4, $5
        }
        END {print "\n]"}'
        ;;
    "kill")
        if [ -n "$PARAM" ]; then
            if kill "$PARAM" 2>/dev/null; then
                echo "{\"status\": \"success\", \"message\": \"Process $PARAM killed\"}"
            else
                echo "{\"status\": \"error\", \"message\": \"Failed to kill process $PARAM\"}"
            fi
        else
            echo "{\"status\": \"error\", \"message\": \"No PID specified\"}"
        fi
        ;;
    "search")
        if [ -n "$PARAM" ]; then
            echo "["
            ps -eo pid,user,%cpu,%mem,comm | grep "$PARAM" | head -10 | awk '
            BEGIN {first=1}
            {
                if(!first) printf ",\n"
                first=0
                printf "  {\"pid\": %d, \"user\": \"%s\", \"cpu\": %.1f, \"memory\": %.1f, \"name\": \"%s\", \"status\": \"running\"}", $1, $2, $3, $4, $5
            }
            END {print "\n]"}'
        else
            echo "{\"status\": \"error\", \"message\": \"No search term specified\"}"
        fi
        ;;
    *)
        echo "{\"status\": \"error\", \"message\": \"Unknown action: $ACTION\"}"
        ;;
esac