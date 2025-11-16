#!/bin/bash

ACTION="$1"
PARAM="$2"

case "$ACTION" in
    "list")
        # List all users in JSON format
        getent passwd | awk -F: '
        BEGIN {print "["; first=1}
        $3 >= 1000 && $3 < 65534 {
            if(!first) printf ",\n"
            first=0
            printf "  {\"username\": \"%s\", \"uid\": %d, \"gid\": %d, \"home\": \"%s\", \"shell\": \"%s\", \"gecos\": \"%s\"}", $1, $3, $4, $6, $7, $5
        }
        END {print "\n]"}'
        ;;
    "add")
        if [ -n "$PARAM" ]; then
            # Check if user already exists
            if id "$PARAM" &>/dev/null; then
                echo "{\"status\": \"error\", \"message\": \"User $PARAM already exists\"}"
                exit 1
            fi
            
            # Create user with home directory and default shell
            if sudo useradd -m -s /bin/bash -c "LSMD User" "$PARAM" 2>/dev/null; then
                # Set a default password
                echo "$PARAM:temppass123" | sudo chpasswd 2>/dev/null
                echo "{\"status\": \"success\", \"message\": \"User $PARAM created successfully with default password: temppass123\"}"
            else
                echo "{\"status\": \"error\", \"message\": \"Failed to create user $PARAM. Check if you have sudo permissions.\"}"
            fi
        else
            echo "{\"status\": \"error\", \"message\": \"No username specified\"}"
        fi
        ;;
    "delete")
        if [ -n "$PARAM" ]; then
            # Check if user exists
            if ! id "$PARAM" &>/dev/null; then
                echo "{\"status\": \"error\", \"message\": \"User $PARAM does not exist\"}"
                exit 1
            fi
            
            # Prevent deletion of current user
            CURRENT_USER=$(whoami)
            if [ "$PARAM" = "$CURRENT_USER" ]; then
                echo "{\"status\": \"error\", \"message\": \"Cannot delete current user $PARAM\"}"
                exit 1
            fi
            
            # Delete user with home directory
            if sudo userdel -r "$PARAM" 2>/dev/null; then
                echo "{\"status\": \"success\", \"message\": \"User $PARAM deleted successfully\"}"
            else
                echo "{\"status\": \"error\", \"message\": \"Failed to delete user $PARAM. Check if you have sudo permissions.\"}"
            fi
        else
            echo "{\"status\": \"error\", \"message\": \"No username specified\"}"
        fi
        ;;
    "current")
        # Information about current user
        echo "{
          \"username\": \"$(whoami)\",
          \"uid\": $(id -u),
          \"gid\": $(id -g),
          \"groups\": \"$(id -Gn)\"
        }"
        ;;
    *)
        echo "{\"status\": \"error\", \"message\": \"Unknown action: $ACTION\"}"
        ;;
esac