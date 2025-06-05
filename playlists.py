import zmq
import sqlite3
import json

# SQLite Database Setup
DB_FILE = "playlist_service.db"

def setup_database():
    """
    Initialize the SQLite database and create the necessary tables if they don't exist.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create playlists table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS playlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            playlist_name TEXT NOT NULL,
            song TEXT,
            UNIQUE(username, playlist_name, song)
        )
    """)

    conn.commit()
    conn.close()

def create_playlist(data):
    """
    Create a new playlist for the user.
    """
    username = data.get("username")
    playlist_name = data.get("playlist_name")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO playlists (username, playlist_name)
            VALUES (?, ?)
        """, (username, playlist_name))
        conn.commit()
        return {"success": True, "message": f"Playlist '{playlist_name}' created successfully."}
    except sqlite3.IntegrityError:
        return {"success": False, "message": "Playlist already exists."}
    finally:
        conn.close()

def add_song(data):
    """
    Add a song to a playlist.
    """
    username = data.get("username")
    playlist_name = data.get("playlist_name")
    song = data.get("song")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO playlists (username, playlist_name, song)
            VALUES (?, ?, ?)
        """, (username, playlist_name, song))
        conn.commit()
        return {"success": True, "message": f"Song '{song}' added to playlist '{playlist_name}'."}
    except sqlite3.IntegrityError:
        return {"success": False, "message": "Song already exists in the playlist."}
    finally:
        conn.close()

def remove_song(data):
    """
    Remove a song from a playlist.
    """
    username = data.get("username")
    playlist_name = data.get("playlist_name")
    song = data.get("song")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM playlists
        WHERE username = ? AND playlist_name = ? AND song = ?
    """, (username, playlist_name, song))
    conn.commit()
    conn.close()

    return {"success": True, "message": f"Song '{song}' removed from playlist '{playlist_name}'."}

def delete_playlist(data):
    """
    Delete an entire playlist.
    """
    username = data.get("username")
    playlist_name = data.get("playlist_name")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM playlists
        WHERE username = ? AND playlist_name = ?
    """, (username, playlist_name))
    conn.commit()
    conn.close()

    return {"success": True, "message": f"Playlist '{playlist_name}' deleted successfully."}

def view_playlists(data):
    """
    View all playlists and their songs for a user.
    """
    username = data.get("username")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT playlist_name, song FROM playlists
        WHERE username = ?
    """, (username,))
    rows = cursor.fetchall()
    conn.close()

    playlists = {}
    for playlist_name, song in rows:
        if playlist_name not in playlists:
            playlists[playlist_name] = []
        if song:
            playlists[playlist_name].append(song)

    return {"success": True, "playlists": playlists}

# ZeroMQ Setup
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5559")  # Playlist service port

# Initialize the database
setup_database()
print("Playlist service started. Listening for requests...")

while True:
    try:
        # Receive request
        message = socket.recv_json()
        print(f"Received request: {message}")

        # Handle request
        request_type = message.get("type")
        if request_type == "create_playlist":
            response = create_playlist(message)
        elif request_type == "add_song":
            response = add_song(message)
        elif request_type == "remove_song":
            response = remove_song(message)
        elif request_type == "delete_playlist":
            response = delete_playlist(message)
        elif request_type == "view_playlists":
            response = view_playlists(message)
        else:
            response = {"success": False, "message": "Invalid request type."}

        # Send response
        socket.send_json(response)
    except Exception as e:
        print(f"Error: {e}")
        socket.send_json({"success": False, "message": "Internal server error."})
