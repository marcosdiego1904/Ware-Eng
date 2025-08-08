#!/usr/bin/env python3
"""
Check user password hash
"""

import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

def check_testuser():
    """Check testuser password"""
    
    conn = sqlite3.connect('instance/database.db')
    cursor = conn.cursor()
    
    # Get testuser info
    cursor.execute('SELECT id, username, password_hash FROM user WHERE username = ?', ('testuser',))
    result = cursor.fetchone()
    
    if result:
        user_id, username, password_hash = result
        print(f"User found: ID={user_id}, username={username}")
        print(f"Password hash exists: {bool(password_hash)}")
        
        if password_hash:
            # Test password
            is_valid = check_password_hash(password_hash, 'testpass123')
            print(f"Password 'testpass123' is valid: {is_valid}")
            
            if not is_valid:
                print("Updating password...")
                new_hash = generate_password_hash('testpass123')
                cursor.execute('UPDATE user SET password_hash = ? WHERE username = ?', (new_hash, 'testuser'))
                conn.commit()
                print("Password updated successfully")
        else:
            print("No password hash found, setting password...")
            new_hash = generate_password_hash('testpass123')
            cursor.execute('UPDATE user SET password_hash = ? WHERE username = ?', (new_hash, 'testuser'))
            conn.commit()
            print("Password set successfully")
    else:
        print("testuser not found")
    
    conn.close()

if __name__ == "__main__":
    check_testuser()