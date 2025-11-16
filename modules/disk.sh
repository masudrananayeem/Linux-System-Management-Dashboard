#!/bin/bash

ACTION="$1"

case "$ACTION" in
    "usage")
        # Get disk usage in proper JSON format
        echo "["
        first=true
        df -h | awk '
        NR==1 {next}
        /^\/dev\// {
            if (!first) printf ",\n"
            first=false
            gsub(/%/, "", $5)
            printf "  {\"filesystem\": \"%s\", \"size\": \"%s\", \"used\": \"%s\", \"available\": \"%s\", \"use_percent\": \"%s\", \"mounted\": \"%s\"}", $1, $2, $3, $4, $5, $6
        }
        END {print "\n]"}'
        ;;
    "large_files")
        # Find large files in home directory
        find ~ -type f -size +100M -exec ls -lh {} \; 2>/dev/null | head -10 | awk '
        BEGIN {print "["; first=1}
        {
            if(!first) printf ",\n"
            first=0
            printf "  {\"size\": \"%s\", \"file\": \"%s\"}", $5, $9
        }
        END {print "\n]"}'
        ;;
    "details")
        lsblk -J 2>/dev/null || echo "{\"status\": \"error\", \"message\": \"lsblk not available\"}"
        ;;
    *)
        echo "{\"status\": \"error\", \"message\": \"Unknown action: $ACTION\"}"
        ;;
esac