import appdaemon.plugins.hass.hassapi as hass
from operator import itemgetter, attrgetter
import random
# this not present in container...
# from homeassistant.components.media_player.kodi import (EVENT_KODI_CALL_METHOD_RESULT)
EVENT_KODI_CALL_METHOD_RESULT = 'kodi_call_method_result'

# Call this as a service with the data below
# Basic search
# { "entity_id": "media_player.htpc", "search_string": "show title"}
# Full search
# { "entity_id": "media_player.htpc", "search_string": "show title", "play_watched": "False", "play_oldest": "True", "play_random": False}
# or via form from front end

# input_boolean:
#   kodi_play_watched:
#     name: Play Watched
#     initial: off
# input_text:
#   kodi_search:
#     name: Kodi Search
#     min: 3
# input_select:
#   kodi_search_type:
#     name: Kodi Type
#     options:
#       - Recordings
#       - Episodes
#   kodi_players:
#     name: Kodi Player
#     options:
#       - media_player.player1
#       - media_player.player2
#   kodi_play_mode:
#     name: Kodi Play Mode
#     options:
#       - Newest
#       - Oldest
#       - Random
# Groups
# KodiPlayer:
#   name: Kodi Player
#   entities:
#     - input_text.kodi_search
#     - input_select.kodi_search_type
#     - input_select.kodi_play_mode
#     - input_select.kodi_players
#     - input_boolean.kodi_play_watched
#     - script.kodiplaysearch
# Script
# kodiplaysearch:
#   alias: Play Search
#   sequence:
#   - event: searchplaykodi
#     event_data: {}


class SearchPlayKodi(hass.Hass):

    # "Global" variable for search
    current_search = {}
    # Functions of stuff

    def initialize(self):
        # Listen for API results
        self.listen_event(self.receive_kodi_result, EVENT_KODI_CALL_METHOD_RESULT)
        # Listen for our own service
        self.listen_event(self.router, "searchplaykodi")
        # Make sure dict is blank
        self.current_search = {}

    def router(self, event_name, data, whatever):
        if len(data) == 0:
            # Use form data from frontend
            e = self.get_state('input_select.kodi_players')
            t = self.get_state('input_select.kodi_search_type')
            s = self.get_state('input_text.kodi_search')
            ip = self.get_state('input_boolean.kodi_play_watched')
            po = self.get_state('input_select.kodi_play_mode')
            # Parse input select
            if po == 'Newest':
                po = False
                pr = False
            elif po == 'Oldest':
                po = True
                pr = False
            elif po == 'Random':
                pr = True
                po = False
            # Convert to Boolean
            ip = ip == 'on'
            # Populate optionals
            optionals = {"search_type": t, "play_oldest": po, "play_watched": ip, "resume": False, "play_random": pr}
        else:
            # Raw service call, check input
            if "entity_id" not in data:
                self.log("No Entity Specified. Doing Nothing")
                return
            if "search_string" not in data:
                self.log("Need a Search String.")
                return
            # Optional Arguments
            # Set initial
            optionals = {"search_type": 'Recordings', "play_oldest": False, "play_watched": True, "resume": False, "play_random": False}
            for (k,v) in optionals.items():
                if k in data:
                    if k == 'search_type':
                        # Catch string type
                        optionals['search_type'] = data[k]
                    else:
                        # Rest are booleans
                        optionals[k] = data[k] in ['True', 'on']

            e = data["entity_id"]
            s = data["search_string"]

        # Set global var
        self.current_search = {}
        self.current_search = {"search_string": s.lower(), "player": e, **optionals}
        # Check search string
        if len(self.current_search['search_string']) < 3:
            self.notify_kodi("Need a longer Search String")
            self.log("Need a longer Search String.")
            return
        # Log Attempt
        self.log(self.current_search)
        # Go for it
        self.search_kodi(e, s, self.current_search['search_type'])

    def receive_kodi_result(self, event_id, payload_event, *args):
        # This listener will end up listening for all requests, hopefully there's no conflicts?.....
        # Make sure this is our event...
        assert event_id == EVENT_KODI_CALL_METHOD_RESULT

        # Grab the data from the payload
        result = payload_event['result']
        method = payload_event['input']['method']

        if method == "PVR.GetRecordings":
            # self.log(result)
            # There isn't a search api for recordings? So this is just as easy. 
            matches = list(filter(lambda r: self.current_search['search_string'] in r['label'].lower(), result['recordings']))
            self.process_results(matches)

        elif method == "VideoLibrary.GetTVShows":
            # First get the tvshow id then search for episode
            matches = list(filter(lambda r: self.current_search['search_string'] in r['label'].lower(), result['tvshows']))
            if len(matches) == 1:
                self.log(matches)
                tvshowid = matches[0]['tvshowid']
                tvshowname = matches[0]['label']
                self.log("Found a match for show {} with id of {}".format(tvshowname, tvshowid))
                self.search_kodi(self.current_search['player'], tvshowid, 'RawEpisodes')
            else:
                self.log("No or too many matches for search: {}".format(self.current_search['search_string']))
                self.notify_kodi("No or too many matches for search: {}".format(self.current_search['search_string']))

        elif method == "VideoLibrary.GetEpisodes":
            self.process_results(result['episodes'])

    def search_kodi(self, entity_id, search_string=None, search_type='Recordings'):
        # Decide which API call to use
        if search_type == 'Recordings':
            self.call_service('media_player/kodi_call_method', entity_id=entity_id, method='PVR.GetRecordings', properties=["file", "playcount", "starttime"])
        elif search_type == 'Episodes':
            self.call_service('media_player/kodi_call_method', entity_id=entity_id, method='VideoLibrary.GetTVShows')
        elif search_type == 'RawEpisodes':
            self.call_service('media_player/kodi_call_method', entity_id=entity_id, method='VideoLibrary.GetEpisodes', tvshowid=search_string, properties=["file", "playcount", "season", "episode"])
        else:
            pass

    def process_results(self, results):
        # Process results of playable items and narrow down
        # Then Play
        if not self.current_search['play_watched']:
            # Only match elements that haven't been played
            matches = list(filter(lambda r: r['playcount'] == 0, results))
        else:
            matches = results
        if len(matches) < 1:
            # Nothing to do now
            self.notify_kodi('No Matches to Search {}'.format(self.current_search['search_string']))
            self.log('No Matches to Search {}'.format(self.current_search['search_string']))
            return
        # self.log(matches)
        # self.log(matches_sorted)
        if self.current_search['play_random']:
            # Pick one!
            to_play = random.choice(matches)
        else:
            # Sort the matches according to user
            if self.current_search['search_type'] == 'Episodes':
                matches_sorted = sorted(matches, key=itemgetter('season', 'episode'), reverse=self.current_search['play_oldest'])
            elif self.current_search['search_type'] == 'Recordings':
                matches_sorted = sorted(matches, key=itemgetter('starttime'), reverse=self.current_search['play_oldest'])

            if matches_sorted:
                # Play the last element
                to_play = matches_sorted.pop()
            else:
                self.notify_kodi('Sorting Error')
                self.log("Sorting Error")
                return
        # Should be good..but check again and then play
        if to_play is not None:
            self.log("I want to play!")
            self.log(to_play)
            self.play_kodi(to_play['file'])
            self.notify_kodi('Episode: {label} Playcount: {playcount}'.format(**to_play))
        else:
            self.notify_kodi('Unknown Error')
            self.log('Unknown Error')

    def notify_kodi(self, message, title='Ultrahouse KodiPlayer'):
        self.call_service('media_player/kodi_call_method', entity_id=self.current_search['player'], method='GUI.ShowNotification', title=title, message=message)

    def play_kodi(self, media_id=None, media_type='file', resume=None):
        self.call_service('media_player/play_media', entity_id=self.current_search['player'], media_content_type=media_type, media_content_id=media_id)
