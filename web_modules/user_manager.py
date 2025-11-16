#!/usr/bin/env python3
"""
User management module for web dashboard
"""

import subprocess
import pwd
import grp

class UserManager:
    def list_users(self):
        """List all system users"""
        try:
            users = []
            for user in pwd.getpwall():
                if user.pw_uid >= 1000:  # Typically regular users
                    users.append({
                        'username': user.pw_name,
                        'uid': user.pw_uid,
                        'gid': user.pw_gid,
                        'home': user.pw_dir,
                        'shell': user.pw_shell,
                        'gecos': user.pw_gecos
                    })
            return users
        except Exception as e:
            return {'error': str(e)}
    
    def get_user_groups(self, username):
        """Get groups for a specific user"""
        try:
            groups = []
            for group in grp.getgrall():
                if username in group.gr_mem:
                    groups.append(group.gr_name)
            return groups
        except Exception as e:
            return {'error': str(e)}
