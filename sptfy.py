import spotipy
from spotipy.oauth2 import SpotifyOAuth
import py_cui
import datetime
import requests
from PIL import Image
import pylast

scope = "user-modify-playback-state user-follow-modify user-read-recently-played user-read-playback-position playlist-read-collaborative user-read-playback-state user-top-read playlist-modify-public user-library-modify user-follow-read user-read-currently-playing user-library-read playlist-modify-private"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=[CLIENT_ID], client_secret=[CLIENT_SECRET], redirect_uri=[REDIRECT_URI], scope=scope))

lastfm_api_key = [LASTFM_API_KEY]
lastfm_api_secret = [LASTFM_API_SECRET]
network = pylast.LastFMNetwork(
    api_key=lastfm_api_key, api_secret=lastfm_api_secret)




class MainWindow:
    ############################
    ############################
    # INIT FUNCTION
    def __init__(self, root: py_cui.PyCUI):
        self.shuffle_bool = True
        sp.shuffle(self.shuffle_bool)

        self.repeat_bool = True
        sp.repeat("context")

        # Root PyCUI window
        self.root = root
        # Making main widget set
        self.main_widget_set = self.root.create_new_widget_set(10,10)
        
        #0
        self.main_widget_set.add_button('Play', 7, 9, command = self.start_playback)
        #1
        self.main_widget_set.add_button('Pause', 8, 9, command = self.pause)
        #2
        self.main_widget_set.add_button(f'Shuffle: {self.shuffle_bool}', 9, 9, command=self.shuffle)
        self.main_widget_set.get_widgets()[2].set_color(py_cui.GREEN_ON_BLACK)
        #3
        self.prog_bar = self.main_widget_set.add_slider(f'{str(datetime.timedelta(milliseconds=sp.current_playback()["progress_ms"]))[:-7]}/{str(datetime.timedelta(milliseconds=sp.current_playback()["item"]["duration_ms"]))[:-7]}', 
            9, 2, 1, 6, max_val=sp.current_playback()['item']['duration_ms']/1000, init_val=sp.current_playback()['progress_ms']/1000)
        self.prog_bar.add_key_command(py_cui.keys.KEY_ENTER, self.prog_change)
        self.main_widget_set.get_widgets()[3].toggle_value()
        #4
        self.main_widget_set.add_label(f"\"{sp.current_playback()['item']['name']}\" By {sp.current_playback()['item']['artists'][0]['name']} from the album \"{sp.current_playback()['item']['album']['name']}\" (track #{sp.current_playback()['item']['track_number']})", 8, 2, 1, 6)
        #5
        self.main_widget_set.add_button(f"Skip >>", 9, 8, command=self.skip)
        #6
        self.main_widget_set.add_button(f"<< Previous", 9, 1, command=self.previous)
        #7
        self.search_bar = self.main_widget_set.add_text_box("Search", 0, 8, 1, 2)
        self.search_bar.add_key_command(py_cui.keys.KEY_ENTER, self.search)
        #8
        self.main_widget_set.add_button("Repeat: True", 9, 0, command=self.repeat)
        self.main_widget_set.get_widgets()[8].set_color(py_cui.GREEN_ON_BLACK)
        #9
        self.volume_slider = self.main_widget_set.add_slider("Volume", 6, 8, 1, 2, init_val=60)
        self.volume_slider.add_key_command(py_cui.keys.KEY_ENTER, self.volume)
        #10
        self.main_widget_set.add_button("User profile", 8, 0)
        #11
        try:
            self.main_widget_set.add_block_label(f"{self.asciify(sp.current_playback()['item']['album']['images'][0]['url'], 141, 47)}", 0, 2, 8, 6)
        except IndexError:
            pass
        
        
        #Making search widget set for searching
        self.search_widget_set = self.root.create_new_widget_set(8, 8)
        
        #0
        self.search_widget_set.add_label(f"Search results", 0, 1, 1, 6)
        #1
        self.track_list = self.search_widget_set.add_scroll_menu("Tracks", 1, 1, 7)
        self.track_list.add_key_command(py_cui.keys.KEY_ENTER, self.popup_search_select_track)
        #2
        self.artist_list = self.search_widget_set.add_scroll_menu("Artists", 1, 2, 7)
        #3
        self.album_list = self.search_widget_set.add_scroll_menu("Albums", 1, 3, 7)
        #4
        self.playlist_list = self.search_widget_set.add_scroll_menu("Playlists", 1, 4, 7)
        #5
        self.episode_list = self.search_widget_set.add_scroll_menu("Episodes", 1, 5, 7)
        #6
        self.show_list = self.search_widget_set.add_scroll_menu("Shows", 1, 6, 7)
        #8
        self.search_widget_set.add_button("Back", 1, 0, command=self.back)
        #9
        self.search_widget_set.add_text_box("Search", 1, 7)
        


        # Making a track info widget
        self.track_info_widget_set = self.root.create_new_widget_set(10, 10)

        #0
        self.track_info_widget_set.add_button("Back", 0, 0, command=self.back)
        #1
        self.track_info_widget_set.add_block_label("Track name", 0, 2, 1, 2)
        #2
        self.track_info_widget_set.add_block_label("Track artist", 0, 4, 1, 2)
        #3
        self.track_info_widget_set.add_block_label("Track album", 0, 6, 1, 2)
        #4
        self.track_info_widget_set.add_block_label("Track tags", 1, 2, 1, 6)
        #5
        self.track_info_widget_set.add_block_label("Cover", 2, 2, 8, 6)
        #6
        self.track_info_widget_set.add_block_label("Analysis", 2, 9, 2, 1).toggle_border()
        #7
        self.track_info_widget_set.add_button("Play", 2, 0, command=self.start_track_info)
        #8
        self.track_info_widget_set.add_button("Add to queue", 2, 1, command=self.add_to_queue_info)
        #9
        self.info_add_to_playlist = self.track_info_widget_set.add_scroll_menu("Add to playlist", 3, 0, 4, 2)
        self.info_add_to_playlist.add_key_command(py_cui.keys.KEY_ENTER, self.info_add_to_playlist_command)
        


        # apply the initial widget set
        self.root.apply_widget_set(self.main_widget_set)

    ############################
    ############################

    # Function for updating things i guess
    def update_track(self):
        self.main_widget_set.get_widgets()[3].update_slider_value(-self.main_widget_set.get_widgets()[3].get_slider_value())
        self.main_widget_set.get_widgets()[3].update_slider_value(sp.current_playback()['progress_ms']/1000)

        self.main_widget_set.get_widgets()[3].set_title(f'{str(datetime.timedelta(milliseconds=sp.current_playback()["progress_ms"]))[:-7]}/{str(datetime.timedelta(milliseconds=sp.current_playback()["item"]["duration_ms"]))[:-7]}')

        try:
            self.main_widget_set.get_widgets()[11].set_title(f"{self.asciify(sp.current_playback()['item']['album']['images'][0]['url'], 141, 47)}")
        except:
            pass

        self.main_widget_set.get_widgets()[4].set_title(f"\"{sp.current_playback()['item']['name']}\" By {sp.current_playback()['item']['artists'][0]['name']} from the album \"{sp.current_playback()['item']['album']['name']}\" (track #{sp.current_playback()['item']['track_number']})") 

    #Start playback
    def start_playback(self):
        try:
            sp.start_playback()
        except spotipy.exceptions.SpotifyException:
            pass

        self.update_track()

    # Pause playback
    def pause(self):
        try:
            sp.pause_playback()
        except spotipy.exceptions.SpotifyException:
            pass
    
    # Shuffle toggle
    def shuffle(self):
        self.shuffle_bool = not self.shuffle_bool
        sp.shuffle(self.shuffle_bool)
        color = py_cui.RED_ON_BLACK
        if self.shuffle_bool:
            color = py_cui.GREEN_ON_BLACK
            
        self.main_widget_set.get_widgets()[2].set_color(color)
        self.main_widget_set.get_widgets()[2].set_title(f"Shuffle: {self.shuffle_bool}")

    def repeat(self):
        self.repeat_bool = not self.repeat_bool
        color = py_cui.RED_ON_BLACK
        state = "off"
        if self.repeat_bool:
            color = py_cui.GREEN_ON_BLACK
            state = "context"
        
        sp.repeat(state)
        self.main_widget_set.get_widgets()[8].set_color(color)
        self.main_widget_set.get_widgets()[8].set_title(f"Repeat: {self.repeat_bool}")


    # Next track/skip track
    def skip(self):
        sp.next_track()
        self.update_track()
    
    # Previous track
    def previous(self):
        sp.previous_track()
        self.update_track()
    
    # Change volume
    def volume(self):
        sp.volume(self.main_widget_set.get_widgets()[9].get_slider_value())
    
    # Change progression on track
    def prog_change(self):
        sp.seek_track(int(self.main_widget_set.get_widgets()[3].get_slider_value())*1000)

        self.main_widget_set.get_widgets()[3].set_title(f'{str(datetime.timedelta(milliseconds=sp.current_playback()["progress_ms"]))[:-7]}/{str(datetime.timedelta(milliseconds=sp.current_playback()["item"]["duration_ms"]))[:-7]}')
    
    # Search bar functionality
    def search(self):
        self.root.apply_widget_set(self.search_widget_set)
        try:
            tracks = sp.search(q=f"{self.search_bar.get()}", limit=50, type="track")
        except spotipy.exceptions.SpotifyException:
            self.update_track()
            self.root.apply_widget_set(self.main_widget_set)
            return
        albums = sp.search(q=f"{self.search_bar.get()}", limit=50, type="album")
        artists = sp.search(q=f"{self.search_bar.get()}", limit=50, type="artist")
        playlists = sp.search(q=f"{self.search_bar.get()}", limit=50, type="playlist")
        shows = sp.search(q=f"{self.search_bar.get()}", limit=50, type="show")
        episodes = sp.search(q=f"{self.search_bar.get()}", limit=50, type="episode")

        for i, x in enumerate(tracks['tracks']['items'], start=0):
            self.track_list.add_item(f"{tracks['tracks']['items'][i]['name']}                        URI: {tracks['tracks']['items'][i]['uri']}")

        for i, x in enumerate(albums['albums']['items'], start=0):
            self.album_list.add_item(f"{albums['albums']['items'][i]['name']}")

        for i, x in enumerate(artists['artists']['items'], start=0):
            self.artist_list.add_item(f"{artists['artists']['items'][i]['name']}")
        
        self.search_widget_set.get_widgets()[0].set_title(f"Search results for \"{self.search_bar.get()}\"")
    
    

    ##############################
    ##############################
    # TRACK INFO SCREEN FROM SEARCH
   
    # Start specific track from info widget set
    def start_track_info(self):
        sp.add_to_queue(str(self.track_list.get()).split("URI: ", 1)[1])
        sp.next_track()

    # Add track to queue from info widget set
    def add_to_queue_info(self):
        sp.add_to_queue(str(self.track_list.get()).split("URI: ", 1)[1])
    
    def info_add_to_playlist_command(self):
        sp.playlist_add_items(str(self.info_add_to_playlist.get()).split("id: ", 1)[1], [str(self.track_list.get()).split("URI: ", 1)[1]])
        self.root.show_message_popup(f"Sucess!", f"Track \"{str(self.track_list.get()).split('     ')[0]}\" has successfully been added to playlist \"{str(self.info_add_to_playlist.get()).split('   -   ', 1)[0]}\"")

    # Add to playlist
    def popup_add_to_playlist(self, choice):
        for x in sp.user_playlists(user=sp.current_user()['id'])['items']:
            if choice == f"{x['name']} - id: {x['id']}":
                sp.playlist_add_items(x['id'], [str(self.track_list.get()).split("URI: ", 1)[1]])
                self.root.show_message_popup(f"Success!", f"Track \"{str(self.track_list.get()).split('     ')[0]}\" has successfully been added to playlist \"{x['name']}\"")
                break
    
    # Go to track info from search
    def go_to_track_info(self):
        track = sp.track(str(self.track_list.get()).split('URI: ', 1)[1])

        self.track_info_widget_set.get_widgets()[1].set_title(f"Track: {track['name']}")
        
        artists = ""
        for i, x in enumerate(track['artists'], start=0):
            if i == 0:
                artists = f"{track['artists'][i]['name']}"
            else:
                artists = f"{artists}, {track['artists'][i]['name']}"
        self.track_info_widget_set.get_widgets()[2].set_title(f"Artists: {artists}")
        
        self.track_info_widget_set.get_widgets()[3].set_title(f"Album: {track['album']['name']} (track #{track['track_number']})")
        
        top_tags = ""
        for tag in network.get_track(track['artists'][0]['name'], track['name']).get_top_tags(limit=10):
            top_tags = (f"{top_tags} | {tag[0]}")
        self.track_info_widget_set.get_widgets()[4].set_title(f"Tags: {top_tags}")
        
        self.track_info_widget_set.get_widgets()[5].set_title(f"{self.asciify(track['album']['images'][0]['url'], 141, 47)}")
        
        track_analysis = sp.audio_analysis(str(self.track_list.get()).split('URI: ', 1)[1])
        keys = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        self.track_info_widget_set.get_widgets()[6].set_title(f"TRACK ANALYSIS \n\n Duration: {str(datetime.timedelta(seconds=track_analysis['track']['duration']))} \n\nBPM: {track_analysis['track']['tempo']} \nConf.: {track_analysis['track']['tempo_confidence']}/1 \n\ndB: {track_analysis['track']['loudness']} \n\nKey: {keys[track_analysis['track']['key']]} \nConf.: {track_analysis['track']['key_confidence']}/1")

        for playlist in sp.user_playlists(user=sp.current_user()['id'])['items']:
            self.info_add_to_playlist.add_item(f"{playlist['name']}   -   id: {playlist['id']}")
        

        # Change widget set to track info
        self.root.apply_widget_set(self.track_info_widget_set)
    
    ##############################
    ##############################




    ##############################
    ##############################
    # INTERACT WITH SEARCH RESULTS

    # Choices for search item
    def popup_search_select_choice_track(self, choice):
        if choice == "Add to queue":
            sp.add_to_queue(str(self.track_list.get()).split("URI: ", 1)[1])

        if choice == "Add to playlist":
            menu_choices = []
            for playlist in sp.user_playlists(user=sp.current_user()['id'])['items']:
                menu_choices.append(f"{playlist['name']} - id: {playlist['id']}")
            self.root.show_menu_popup(f"Chose a playlist", menu_choices, self.popup_add_to_playlist)

        if choice == "Go to track":
            self.go_to_track_info()

        if choice == "Go to artist":
            print("Go to artist")

        if choice == "Go to album":
            print("Go to album")
        
        if choice == "Cancel":
            pass

    # Popup on search item interact
    def popup_search_select_track(self):
        menu_choices = ["Add to queue", "Add to playlist", "Go to track", "Go to artist", "Go to album", "Cancel"]
        self.root.show_menu_popup(f"{str(self.track_list.get()).split('      ', 1)[0]}", menu_choices, self.popup_search_select_choice_track)
    
    ##############################
    ##############################
    


    def back(self):
        self.update_track()
        self.root.apply_widget_set(self.main_widget_set)
        self.track_list.clear()
        self.album_list.clear()
        self.artist_list.clear()
        self.playlist_list.clear()
        self.episode_list.clear()
        self.show_list.clear()
        self.search_bar.clear()
        self.info_add_to_playlist.clear()
    
    def asciify(self, img, width, height):
        try:
            r = requests.get(img, stream=True)
            if r.status_code != 200:
                raise
            img = Image.open(r.raw)
        except:
            print("Image could not be loaded")

        img = img.resize((width, height))

        img = img.convert("L")
        pixels = img.getdata()
        imgchars = ["$", "@", "B", "%", "8", "&", "W", "M", "#", "*", "o", "a", "h", "k", "b", "d", "p", "q", "w", "m", "Z", "O", "0", "Q", "L", "C", "J", "U", "Y", "X", "z", "c", "v", "u", "n", "x", "r", "j", "f", "t", "/", "\\", "|", "(", ")", "1", "{", "}", "[", "]", "?", "-", "_", "+", "~", "<", ">", "i", "!", "l", "I", ";", ":", "\"", "^", "`", "'", ".", " "][::-1]
        ascii_img = ""

        for i, pixel in enumerate(pixels):
            if i%width == 0:
                ascii_img += "\n"
            ascii_img += imgchars[int(pixel/256*len(imgchars))]
        return ascii_img
    
        


# Create CUI object, pass to wrapper class, and start the CUI
root = py_cui.PyCUI(3, 3)
wrapper = MainWindow(root)
root.start()
