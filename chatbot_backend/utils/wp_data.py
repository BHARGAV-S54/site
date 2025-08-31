import mysql.connector
import os

def get_user_context(user_id: int):
    if not user_id:
        return {}

    # Load environment variables with fallback
    db_config = {
        "host": os.getenv("WP_DB_HOST", "localhost"),
        "user": os.getenv("WP_DB_USER", "root"),
        "password": os.getenv("WP_DB_PASS", ""),
        "database": os.getenv("WP_DB_NAME", "wordpress")
    }

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Get display name
        cursor.execute("SELECT display_name FROM wp_users WHERE ID = %s", (user_id,))
        name_row = cursor.fetchone()
        name = name_row['display_name'] if name_row else "Unknown"

        # Count unread messages
        cursor.execute("""
            SELECT SUM(unread_count) as unread_count
            FROM wp_bp_messages_recipients
            WHERE user_id = %s
        """, (user_id,))
        unread_count_row = cursor.fetchone()
        unread_count = unread_count_row['unread_count'] or 0

        # Get group names
        cursor.execute("""
            SELECT g.name
            FROM wp_bp_groups_members gm
            JOIN wp_bp_groups g ON gm.group_id = g.id
            WHERE gm.user_id = %s
        """, (user_id,))
        groups = [row['name'] for row in cursor.fetchall()]

        conn.close()
        return {
            "name": name,
            "unread_messages": unread_count,
            "groups": groups
        }

    except mysql.connector.Error as err:
        print("DB error in get_user_context:", err)
        return {
            "name": "Unknown",
            "unread_messages": 0,
            "groups": []
        }
