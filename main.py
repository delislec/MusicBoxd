import zmq

# Global variables
current_user = None
current_user_genre = None
user_activity = {}

# Sample data for popular songs, albums, and genre-based recommendations
popular_songs = ["Love Somebody - Morgan Wallen", "A Bar Song(Tipsy) - Shaboozey", "Birds of a Feather - Billie Eilish", "Die With A Smile - Lady Gaga & Bruno Mars", "Espresso - Sabrina Carpenter"]
popular_albums = ["Lyfestyle - Yeat", "Short n' Sweet - Sabrina Carpenter", "Beatifully Broken - Jelly Roll", "Last Lap - Rod Wave", "One Thing at A Time - Morgan Wallen"]

# Recommended songs categorized by genre
recommended_songs_by_genre = {
    "EDM": ["Miles On It - Marshmello & Kane Brown", "Jumpstart Groove - Omari", "The Come Up - Blype"],
    "Jazz": ["History of the Vibraphone - Warren Wolf", "Crecent City Jewels - Delfeayo Marsalis", "Side Hustle - Thom Rotella"],
    "Gospel": ["Goodness of God - CeCe Winans", "Lord Do it For Me - Zacardi Cortez", "I Speak Jesus - Passion"],
    "Country": ["I Am Not Okay - Jelly Roll", "Lies Lies Lies - Morgan Wallen", "Austin(Boots Stop Workin') - Dasha"],
    "Alternative": ["That's How I'm Feeling - Jack White", "The Emptiness Machine - LINKIN PARK", "Dopamine - Sum 41"],
    "Rap": ["TGIF - Glorilla", "Kehlani - Jordan Adetunji", "Residuals - Chris Brown"],
    "Rock": ["Detroit - Bad Flower", "Mud - Dorothy", "Psycho - Hardy"],
    "R&B": ["Wildflower - Tyrese", "Ruined Me - Muni Long", "Good Good - Usher"],
    "Pop": ["I Can Do It With a Broken Heart - Taylor Swift", "Birds of A Feather - Billie Eilish", "Espresso - Sabrina Carpenter"]
}

# Predefined list of genres
genres = list(recommended_songs_by_genre.keys())

def send_request_to_login_service(request):
    """
    Send a request to the login service (auth_service_login.py).
    """
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5557")  # Login service port
    socket.send_json(request)
    response = socket.recv_json()
    return response

def send_request_to_activity_service(request):
    """
    Send a request to the activity service (auth_service_activity.py).
    """
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5558")  # Activity service port
    socket.send_json(request)
    response = socket.recv_json()
    return response

# Function for sending requests to the auth service
def send_auth_request(request):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5557")  # Port where auth_service is running

    socket.send_json(request)
    response = socket.recv_json()
    return response

def discover_new_music():
    global current_user, current_user_genre
    if not current_user:
        print("Log in to discover new music.")
        return

    if not current_user_genre:
        print("Favorite genre is not available. Please log in again.")
        return

    print(f"Debug: Current user: {current_user}, Favorite genre: {current_user_genre}")

    # Set up ZeroMQ REQ socket to send a request to the recommender microservice
    ctx = zmq.Context()
    socket = ctx.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")  # Port where the recommender service listens

    # Prepare the request
    request = {"type": "music", "genre": current_user_genre.lower()}
    print(f"Debug: Sending request: {request}")
    socket.send_json(request)

    # Wait for an immediate response (acknowledgment)
    try:
        response = socket.recv_json(flags=zmq.NOBLOCK)
        print(f"Debug: Immediate response received: {response}")
    except zmq.Again:
        print("Debug: No immediate response. Subscribing for updates.")

    # Set up a subscriber to listen for recommendations
    subscriber = ctx.socket(zmq.SUB)
    subscriber.connect("tcp://localhost:5556")  # Port where recommendations are broadcasted
    subscriber.setsockopt_string(zmq.SUBSCRIBE, "recommendation")

    print("Waiting for recommendations...")

    for _ in range(5):  # Attempt to retrieve recommendations 5 times
        if subscriber.poll(1000):  # Wait for a message for 1 second
            try:
                topic = subscriber.recv_string()
                response = subscriber.recv_json()
                print(f"Debug: Received topic: {topic}, Data: {response}")

                if topic == "recommendation":
                    titles = response.get("titles", [])
                    if titles:
                        print("\nDiscovered New Music Recommendations:")
                        for idx, title in enumerate(titles, start=1):
                            song_name = title.get('name', 'Unknown Song')
                            artist_name = title.get('artists', [{}])[0].get('name', 'Unknown Artist')
                            print(f"{idx}. {song_name} by {artist_name}")

                            # Log discovered songs in user activity
                            user_activity.setdefault(current_user, []).append(f"Discovered - {song_name} by {artist_name}")
                        return
                    else:
                        print("No recommendations found.")
                        return
            except Exception as e:
                print(f"Debug: Error receiving recommendation: {e}")
        else:
            print("Debug: No recommendations received yet...")

    print("Unable to discover new music. Please try again later.")


def display_startup_message():
    print("Welcome to MusicBoxd—your go-to platform for sharing opinions on songs, artists, and genres!")
    print("Discover new music tailored to your tastes, based on your ratings and preferences.")
    print("Dive in, explore, and let your voice be heard!")

def display_welcome_back_message():
    print("Welcome back to MusicBoxd! Ready to explore new tunes?")
    print("Share your thoughts on your favorite songs, artists, and genres, and get personalized music recommendations based on your latest ratings.")
    print("Let’s discover something amazing together!")

def main_menu():
    print("\nMain Menu:")
    print("1. Login")
    print("2. Create Account")
    print("3. View Most Popular Songs")
    print("4. View Most Popular Albums")
    print("5. Exit")
    print("\n* Choose an option to explore various features, like discovering music or viewing popular songs.")

def send_request_to_playlist_service(request):
    """
    Send a request to the playlist microservice.
    """
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5559")  # Playlist service port
    socket.send_json(request)
    response = socket.recv_json()
    return response

def manage_playlists():
    """
    Manage playlists by adding, viewing, or deleting playlists and songs.
    """
    while True:
        print("\nPlaylist Management:")
        print("1. View Playlists")
        print("2. Create a Playlist")
        print("3. Add Song to a Playlist")
        print("4. Remove Song from a Playlist")
        print("5. Delete a Playlist")
        print("6. Back to Main Menu")

        choice = input("Enter your choice: ")

        if choice == '1':
            request = {"type": "view_playlists", "username": current_user}
            response = send_request_to_playlist_service(request)
            if response["success"]:
                playlists = response.get("playlists", {})
                if playlists:
                    print("\nYour Playlists:")
                    for playlist, songs in playlists.items():
                        print(f"- {playlist}: {', '.join(songs) if songs else 'No songs'}")
                else:
                    print("You have no playlists.")
            else:
                print(response["message"])

        elif choice == '2':
            playlist_name = input("Enter the name of the new playlist: ")
            request = {"type": "create_playlist", "username": current_user, "playlist_name": playlist_name}
            response = send_request_to_playlist_service(request)
            print(response["message"])

        elif choice == '3':
            playlist_name = input("Enter the name of the playlist: ")
            song = input("Enter the name of the song to add: ")
            request = {"type": "add_song", "username": current_user, "playlist_name": playlist_name, "song": song}
            response = send_request_to_playlist_service(request)
            print(response["message"])

        elif choice == '4':
            playlist_name = input("Enter the name of the playlist: ")
            song = input("Enter the name of the song to remove: ")
            request = {"type": "remove_song", "username": current_user, "playlist_name": playlist_name, "song": song}
            response = send_request_to_playlist_service(request)
            print(response["message"])

        elif choice == '5':
            playlist_name = input("Enter the name of the playlist to delete: ")
            request = {"type": "delete_playlist", "username": current_user, "playlist_name": playlist_name}
            response = send_request_to_playlist_service(request)
            print(response["message"])

        elif choice == '6':
            break
        else:
            print("Invalid choice. Please try again.")

def logged_in_menu():
    print("\nLogged-In Menu:")
    print("1. Play and Rate - play a song, rate it, or discover new songs based on your favorite genre")
    print("2. Change Favorite Genre - update your musical preferences")
    print("3. Show Recent Activity - review your recent actions and ratings")
    print("4. View Current Favorite Genre - check your current preferred genre")
    print("5. Manage Playlists - create and manage playlists")
    print("6. Logout")
    print("7. Exit")

def create_account():
    username = input("Enter a username: ")
    password = input("Enter a password: ")
    
    print("\nAvailable Genres:")
    for index, genre in enumerate(genres, start=1):
        print(f"{index}. {genre}")

    while True:
        try:
            genre_choice = int(input("Enter the number of your favorite genre: "))
            if 1 <= genre_choice <= len(genres):
                favorite_genre = genres[genre_choice - 1]
                break
            else:
                print("Invalid choice. Please choose a number from the list.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    request = {
        "type": "register",
        "username": username,
        "password": password,
        "favorite_genre": favorite_genre
    }
    response = send_auth_request(request)
    print(response["message"])

def login():
    global current_user, current_user_genre
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    request = {
        "type": "login",
        "username": username,
        "password": password
    }
    response = send_request_to_login_service(request)  # Ensure this sends to login service

    if response["success"]:
        current_user = username
        current_user_genre = response["favorite_genre"]  # Store the favorite genre locally
        print("Login successful!")
        print(f"Welcome back! Your favorite genre is {current_user_genre}.")
    else:
        print(response["message"])


def logout():
    global current_user
    confirm = input("Are you sure you want to logout? (y/n): ")
    if confirm.lower() == 'y':
        current_user = None
        print("You have logged out.")
    else:
        print("Logout canceled.")

def view_popular_songs():
    print("\nTop 5 Songs of the Week:")
    for song in popular_songs:
        print(f"- {song}")

def view_popular_albums():
    print("\nTop 5 Albums of the Week:")
    for album in popular_albums:
        print(f"- {album}")

def play_and_rate():
    print("\nPlay and Rate Menu:")
    print("1. Play and Rate a Song")
    print("2. Discover New Music")
    choice = input("Enter your choice: ")

    if choice == '1':
        song = input("Enter the song you want to play and rate: ")
        
        # Rating input with validation for range 1 to 5, including decimals
        while True:
            try:
                rating = float(input("Enter your rating (1-5, decimals allowed): "))
                if 1 <= rating <= 5:
                    # Log the activity (played and rated the song)
                    activity = f"Played and rated {song} with a {rating}/5"
                    
                    # Send activity to auth_service.py for logging
                    request = {
                        "type": "add_activity",
                        "username": current_user,
                        "activity": activity
                    }
                    send_auth_request(request)  # Log activity in the auth service

                    # Store the activity in in-memory user_activity if needed
                    user_activity.setdefault(current_user, []).append(activity)
                    print(f"You played '{song}' and rated it {rating}/5.")
                    break
                else:
                    print("Please enter a rating between 1 and 5.")
            except ValueError:
                print("Invalid input. Please enter a number between 1 and 5.")

    elif choice == '2':
        discover_new_music()
    else:
        print("Invalid choice. Please try again.")

def show_recent_activity():
    print("\nRecent Activity:")
    request = {
        "type": "get_activity",
        "username": current_user
    }
    response = send_request_to_activity_service(request)

    if response["success"]:
        activities = response["activities"]
        for index, activity in enumerate(activities, start=1):
            print(f"{index}. {activity[0]} at {activity[1]}")
    else:
        print("No recent activity.")


def change_favorite_genre():
    print("\nAvailable Genres:")
    for index, genre in enumerate(genres, start=1):
        print(f"{index}. {genre}")
    
    while True:
        try:
            genre_choice = int(input("Enter the number of your new favorite genre: "))
            if 1 <= genre_choice <= len(genres):
                request = {
                    "type": "update_genre",
                    "username": current_user,
                    "new_genre": genres[genre_choice - 1]
                }
                response = send_auth_request(request)
                print(f"Favorite genre changed to {genres[genre_choice - 1]}.")
                break
            else:
                print("Invalid choice. Please choose a number from the list.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def view_current_favorite_genre():
    """
    Fetch and display the user's favorite genre using the activity service.
    """
    global current_user
    if not current_user:
        print("You need to log in to view your favorite genre.")
        return

    # Send request to the activity service
    request = {
        "type": "get_favorite_genre",
        "username": current_user
    }
    response = send_request_to_activity_service(request)

    if response["success"]:
        print(f"\nYour current favorite genre is: {response['favorite_genre']}")
    else:
        print(response["message"])

def main():
    global current_user
    display_startup_message()  # Show startup message at program start

    while True:
        if current_user is None:
            main_menu()
            choice = input("Enter your choice: ")

            if choice == '1':
                login()
            elif choice == '2':
                create_account()
            elif choice == '3':
                view_popular_songs()
            elif choice == '4':
                view_popular_albums()
            elif choice == '5':
                print("Exiting the program. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")
        else:
            # Once logged in, display the logged-in menu
            while current_user:
                logged_in_menu()
                choice = input("Enter your choice: ")

                if choice == '1':
                    play_and_rate()
                elif choice == '2':
                    change_favorite_genre()
                elif choice == '3':
                    show_recent_activity()
                elif choice == '4':
                    view_current_favorite_genre()
                elif choice == '5':
                    manage_playlists()
                elif choice == '6':
                    logout()
                    break  # Return to main menu after logout
                elif choice == '7':
                    print("Exiting the program. Goodbye!")
                    exit()  # Terminate the program
                else:
                    print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
