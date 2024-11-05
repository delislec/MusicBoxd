import random

# In-memory storage for user accounts and activity
users = {}
current_user = None
user_activity = {}
discovered_songs = {}  # Tracks discovered songs by user

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

def discover_new_music():
    favorite_genre = users[current_user]["favorite_genre"]
    recommended_songs = recommended_songs_by_genre.get(favorite_genre, [])
    
    # Ensure there is a discovered_songs entry for the current user
    if current_user not in discovered_songs:
        discovered_songs[current_user] = set()
    
    # Filter out songs already discovered by this user
    new_songs = [song for song in recommended_songs if song not in discovered_songs[current_user]]
    
    if new_songs:
        # Randomly select a new song that hasn't been recommended before
        new_song = random.choice(new_songs)
        print(f"\nDiscovering new music in your favorite genre ({favorite_genre}): {new_song}")
        
        # Add the discovered song to the user's discovered songs list
        discovered_songs[current_user].add(new_song)
        
        # Ask if the user wants to rate the discovered song
        rate_choice = input("Would you like to rate this song? (y/n): ")
        if rate_choice.lower() == 'y':
            while True:
                try:
                    rating = float(input("Enter your rating (1-5, decimals allowed): "))
                    if 1 <= rating <= 5:
                        user_activity.setdefault(current_user, []).append(f"Discovered and rated - {new_song} - {rating}/5")
                        print(f"You rated '{new_song}' with a {rating}/5.")
                        break
                    else:
                        print("Please enter a rating between 1 and 5.")
                except ValueError:
                    print("Invalid input. Please enter a number between 1 and 5.")
        else:
            # Log the discovered song without a rating
            user_activity.setdefault(current_user, []).append(f"Discovered new song - {new_song}")
            print("You chose not to rate the song.")
    else:
        print(f"\nNo new songs to discover in {favorite_genre}. You've discovered all available songs in this genre!")

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

def logged_in_menu():
    print("\nLogged-In Menu:")
    print("1. Play and Rate - play a song, rate it, or discover new songs based on your favorite genre")
    print("2. Change Favorite Genre - update your musical preferences")
    print("3. Show Recent Activity - review your recent actions and ratings")
    print("4. View Current Favorite Genre - check your current preferred genre")
    print("5. Logout")
    print("6. Exit")

def create_account():
    global users
    print("Creating an account will allow you to log in, rate songs, and customize your experience.")
    username = input("Enter a username: ")
    if username in users:
        print("Username already exists. Please choose a different username.")
        return
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
    
    users[username] = {"password": password, "favorite_genre": favorite_genre}
    print("Account created successfully! Log in to start exploring music.")

def login():
    global current_user, users
    print("Logging in lets you save preferences, see recent activity, and more.")
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    if username in users and users[username]["password"] == password:
        current_user = username
        display_welcome_back_message()
    else:
        print("Invalid username or password.")

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
                    user_activity.setdefault(current_user, []).append(f"Played and rated {song} with a {rating}/5")
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

def change_favorite_genre():
    print("\nAvailable Genres:")
    for index, genre in enumerate(genres, start=1):
        print(f"{index}. {genre}")
    
    while True:
        try:
            genre_choice = int(input("Enter the number of your new favorite genre: "))
            if 1 <= genre_choice <= len(genres):
                users[current_user]["favorite_genre"] = genres[genre_choice - 1]
                print(f"Favorite genre changed to {genres[genre_choice - 1]}.")
                break
            else:
                print("Invalid choice. Please choose a number from the list.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def show_recent_activity():
    print("\nRecent Activity:")
    activities = user_activity.get(current_user, [])
    
    # Check if there are activities to display
    if not activities:
        print("No recent activity.")
    else:
        # Display only the 5 most recent activities by default
        recent_activities = activities[-5:]  # Get the last 5 activities
        
        for index, activity in enumerate(recent_activities, start=1):
            print(f"{index}. {activity}")
        
        # Option to show all activities if there are more than 5
        if len(activities) > 5:
            show_all_choice = input("Would you like to see all recent activity? (y/n): ")
            if show_all_choice.lower() == 'y':
                print("\nAll Recent Activity:")
                for index, activity in enumerate(activities, start=1):
                    print(f"{index}. {activity}")
        
        # Option to delete a rating
        delete_choice = input("Would you like to delete a rating? (y/n): ")
        if delete_choice.lower() == 'y':
            try:
                delete_index = int(input("Enter the number of the activity you want to delete: ")) - 1
                
                # Adjust delete_index based on whether all or only 5 activities were shown
                if len(activities) > 5 and show_all_choice.lower() != 'y':
                    delete_index += len(activities) - 5
                
                # Check if the index is valid
                if 0 <= delete_index < len(activities):
                    deleted_activity = activities.pop(delete_index)
                    print(f"Deleted: {deleted_activity}")
                else:
                    print("Invalid choice. No activity deleted.")
            except ValueError:
                print("Invalid input. Please enter a number.")


def view_current_favorite_genre():
    print(f"\nYour current favorite genre is: {users[current_user]['favorite_genre']}")

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
                logout()
            elif choice == '6':
                print("Exiting the program. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
