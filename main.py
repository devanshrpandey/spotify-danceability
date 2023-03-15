import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth


#sets environment variables and allows all permissions
os.environ["SPOTIPY_CLIENT_ID"] = "375c8e4a9f8d4243996d256ff41daa62"
os.environ["SPOTIPY_CLIENT_SECRET"] = "1472274bf789453bbd1ed42c9ee181da"
os.environ["SPOTIPY_REDIRECT_URI"] = "http://localhost:9090"
scope = "user-library-read user-read-playback-state user-modify-playback-state user-read-currently-playing app-remote-control streaming playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public user-read-playback-position user-top-read user-read-recently-played user-library-read user-library-modify"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
myID = sp.me()["id"]


def getsongIDs(numberOfPLstoSearch=50,user=myID):
    if numberOfPLstoSearch > 50:
        numberOfPLstoSearch = 50
        print("Number of playlists searched has been capped at 50 as that is the maximum the Spotify API allows.")
    pls = sp.user_playlists(user,limit=numberOfPLstoSearch)["items"]
    allPlaylists = []
    for pl in pls: 
        allPlaylists.append(pl["id"]) #create an array of all playlist ids

    songIDs = []
    for playlist in allPlaylists: 
        plTracks = sp.user_playlist_tracks(playlist_id=playlist) 
        for item in plTracks["items"]:
            try:
                songIDs.append(item["track"]["id"])
            except:
                continue

    return songIDs

def getSortedScores(ids,typeOfScore,maximum=True):
    idCopy = ids

    scoreIDmap = {} # creates a dictionary with scores as keys and IDs as values, to later sort
    features = [] 

    while len(ids) > 100:
        features.extend(sp.audio_features(ids[:100])) #getting around API limit of 100 tracks per "sp.audio_features"
        ids = ids[100:] # removing the first 100 tracks from the copy of "ids" and then looping
    features.extend(sp.audio_features(ids)) # pushing the final tracks into features


    for i in range(len(idCopy)):
        score = features[i][typeOfScore]
        scoreIDmap[score] = idCopy[i]
    #sorting the dictionary by score:
    keys = list(scoreIDmap.keys())
    keys.sort(reverse=maximum)
    sortedScores = {i: scoreIDmap[i] for i in keys}

    return sortedScores

def createFinalPlaylist(scores,playlistName,numberOfSongs=50):
    finalTracks = [] # final X tracks to be put into the playlist
    n = 0
    for score in scores:
        finalTracks.append(scores[score]) # gets the ID from the dictionary and puts it in finaltracks
        n += 1
        if n == numberOfSongs:
            break

    newPlaylist = (sp.user_playlist_create(myID,playlistName)) # creates a new playlist
    sp.playlist_add_items(newPlaylist["id"], finalTracks)
    return newPlaylist


songIDs = getsongIDs(numberOfPLstoSearch=50)
# searches last N playlists that are in Your Library (that you've created or liked). Maximum 50.

sortedScores = getSortedScores(songIDs,typeOfScore="danceability",maximum=True)
# type of score can be danceability, energy, speechiness, acousticness, instrumentalness, liveness, valence, tempo
# if "maximum" is set to True, then it'll find the songs w/ highest score in the category and vice versa (so "danceability" / True would get the most danceable songs)

createFinalPlaylist(sortedScores,playlistName="antidancer",numberOfSongs=50)

#set playlist name and number of songs for the final playlist