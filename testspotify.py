import spotipy
from spotipy.oauth2 import SpotifyClientCredentials 



def get_music(sp, genre, prev_list):
    unique_rec = []
    count = 0
    for i in range(10):
        recommendations = sp.recommendations(seed_genres=[genre], limit = 20)
        for idx, track in enumerate(recommendations['tracks']):
            if track['id'] not in prev_list:
                unique_rec.append(track)
                count += 1
            if count >= 5:
                break
        if count >= 5:
            break

    return unique_rec

def print_recommendations(recommendations):
    for idx, track in enumerate(recommendations):
        song_name = track['name']
        artist_name = track['artists'][0]['name']
        print(f"{idx + 1}. {song_name} by {artist_name}")

def main():
    #connect to spotify
    client_id = "6af3e520436c4d759bfa6cfa6e7860ad"
    client_secret = "52710e687f3943e3a2a5e05a62662a40"
    redirect_url = "http://localhost:8080/callback"
    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(auth_manager=auth_manager)
    genre = "pop"
    prev_tracks = []
    recommendations = get_music(sp, genre, prev_tracks)
    prev_tracks = [track['id'] for track in recommendations]
    print_recommendations(recommendations)
    recommendations2 = get_music(sp, genre, prev_tracks)
    print_recommendations(recommendations2)


    

if __name__ == '__main__':
    main()