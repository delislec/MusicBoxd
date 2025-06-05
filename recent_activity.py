import zmq
import sqlite3
import json

# SQLite Database Setup
DB_FILE = "auth_service.db"

def setup_database():
    """
    Initialize the SQLite database and create the necessary tables if they don't exist.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create user_activity table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            activity TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    """)

    conn.commit()
    conn.close()

def add_user_activity(data):
    """
    Add a new activity for the user.
    """
    username = data.get("username")
    activity = data.get("activity")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_activity (username, activity)
        VALUES (?, ?)
    """, (username, activity))
    conn.commit()
    conn.close()

    return {"success": True, "message": "Activity recorded successfully."}

def get_user_activity(data):
    """
    Get recent activity for the user.
    """
    username = data.get("username")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT activity, timestamp FROM user_activity
        WHERE username = ?
        ORDER BY timestamp DESC
        LIMIT 5
    """, (username,))
    activities = cursor.fetchall()
    conn.close()

    if activities:
        return {"success": True, "activities": activities}
    else:
        return {"success": False, "message": "No activities found."}

def get_user_favorite_genre(data):
    """
    Fetch the user's favorite genre by communicating with the auth service.
    """
    username = data.get("username")

    # Communicate with auth_service
    context = zmq.Context()
    auth_socket = context.socket(zmq.REQ)
    auth_socket.connect("tcp://localhost:5557")  # Auth service port

    # Send request to auth_service
    request = {
        "type": "get_favorite_genre",
        "username": username
    }
    auth_socket.send_json(request)
    response = auth_socket.recv_json()
    return response


# ZeroMQ Setup
context = zmq.Context()
socket = context.socket(zmq.REP)  # Reply socket
socket.bind("tcp://*:5558")  # Change port if needed

# Initialize the database
setup_database()
print("Auth activity service started. Listening for requests...")

while True:
    try:
        # Receive request
        message = socket.recv_json()
        print(f"Received request: {message}")

        # Handle request
        request_type = message.get("type")
        if request_type == "add_activity":
            response = add_user_activity(message)  # Handle activity logging
        elif request_type == "get_activity":
            response = get_user_activity(message)  # Get user activity
        elif request_type == "get_favorite_genre":
            response = get_user_favorite_genre(message)  # Fetch favorite genre via auth service
        else:
            response = {"success": False, "message": "Invalid request type."}

        # Send response
        print(f"Sending response: {response}")
        socket.send_json(response)
    except Exception as e:
        print(f"Error: {e}")
        socket.send_json({"success": False, "message": "Internal server error."})
