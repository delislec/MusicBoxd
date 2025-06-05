import zmq
import requests
import random
import time
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials


def fetch_genre_seeds(client_id, client_secret):
    """
    Fetch available genres using a direct HTTP request to Spotify API.
    """
    try:
        # Request token from Spotify
        auth_url = "https://accounts.spotify.com/api/token"
        auth_response = requests.post(
            auth_url,
            {
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
            },
        )
        auth_data = auth_response.json()

        if "access_token" not in auth_data:
            raise ValueError(f"Failed to obtain access token: {auth_data}")

        access_token = auth_data["access_token"]
        print("Access token obtained successfully.")

        # Fetch available genre seeds
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(
            "https://api.spotify.com/v1/recommendations/available-genre-seeds", headers=headers
        )

        # Add detailed debugging information
        print(f"Debug: API URL: {response.url}")
        print(f"Debug: Response Status Code: {response.status_code}")
        print(f"Debug: Response Content: {response.text}")

        if response.status_code == 200:
            genres = response.json().get("genres", [])
            print("Available genres:", genres)
            return genres
        else:
            raise ValueError(f"Error fetching genres: {response.status_code} {response.text}")

    except Exception as e:
        print(f"Error in fetch_genre_seeds: {e}")
        return []



def get_music(sp, genre, prev_list):
    """
    Fetch music recommendations using Spotify API.
    """
    error_message = ""
    error_flag = False
    unique_rec = []

    # Fetch valid genres dynamically
    valid_genres = fetch_genre_seeds(
        client_id="ff43d3da2af2454ea869ddd34bde47c2",
        client_secret="768df85f0c5c41908a3304bf98f6ac4f",
    )

    if genre not in valid_genres:
        error_message = f"Invalid genre: {genre}. Valid genres: {valid_genres}"
        error_flag = True
        return unique_rec, error_flag, error_message

    try:
        print(f"Debug: Fetching recommendations for genre: {genre}")
        recommendations = sp.recommendations(seed_genres=[genre], limit=20)
        for track in recommendations['tracks']:
            if track['id'] not in prev_list:
                unique_rec.append(track)

            if len(unique_rec) >= 5:
                break
    except Exception as e:
        error_message = f"Spotify API error: {e} | Params: genre={genre}"
        error_flag = True

    return unique_rec, error_flag, error_message

def check_auth_token(client_id, client_secret):
    """
    Validate the Spotify auth token by making a test API request.
    """
    try:
        # Request a new token
        auth_url = "https://accounts.spotify.com/api/token"
        auth_response = requests.post(
            auth_url,
            {
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
            },
        )
        auth_data = auth_response.json()

        if "access_token" not in auth_data:
            print(f"Failed to obtain access token: {auth_data}")
            return False

        access_token = auth_data["access_token"]
        print("Access token obtained successfully.")

        # Test the token with a lightweight Spotify API endpoint
        headers = {"Authorization": f"Bearer {access_token}"}
        test_url = "https://api.spotify.com/v1/me"
        response = requests.get(test_url, headers=headers)

        if response.status_code == 200:
            print("Auth token is valid.")
            return True
        elif response.status_code == 401:
            print("Auth token is invalid or expired.")
            return False
        else:
            print(f"Unexpected status code: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error in check_auth_token: {e}")
        return False

def main():
    client_id = "ff43d3da2af2454ea869ddd34bde47c2"
    client_secret = "768df85f0c5c41908a3304bf98f6ac4f"

    # Authenticate with Spotify
    try:
        auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        sp = Spotify(auth_manager=auth_manager)
        print("Spotify API initialized successfully.")
    except Exception as e:
        print(f"Spotify API initialization failed: {e}")
        return

    # Set up ZeroMQ context and sockets
    ctx = zmq.Context.instance()

    # REP socket to handle client requests
    request_socket = ctx.socket(zmq.REP)
    request_socket.bind("tcp://*:5555")  # Listen for requests from client on port 5555

    # PUB socket to send recommendations
    publisher = ctx.socket(zmq.PUB)
    publisher.bind("tcp://*:5556")  # Broadcast recommendations on port 5556

    prev_list = []  # Store previously seen recommendations
    print("Recommender service started. Ready to receive requests.")

    while True:
        # Wait for a request from the client
        request = request_socket.recv_json()
        print(f"Debug: Received request: {request}")

        response, error_flag, error_message = [], False, ""
        if request["type"].lower() == "music":
            response, error_flag, error_message = get_music(sp, request["genre"], prev_list)
            prev_list = [track['id'] for track in response]

        # Prepare the response
        res = {
            "type": request["type"],
            "titles": response,
            "error_flag": error_flag,
            "error_message": error_message
        }

        # Send the response back to the client
        print(f"Debug: Sending response: {res}")
        request_socket.send_json(res)

        # Broadcast the response to all subscribers
        publisher.send_string("recommendation", zmq.SNDMORE)
        publisher.send_json(res)
        print("Debug: Recommendation broadcasted.")


if __name__ == "__main__":
    main()
