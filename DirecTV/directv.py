#Imports
import logging

from homeassistant.components.media_player import (
    SUPPORT_PAUSE, SUPPORT_PLAY_MEDIA, 
    SUPPORT_TURN_OFF, SUPPORT_TURN_ON, MediaPlayerDevice)
from homeassistant.const import (
    CONF_HOST, CONF_PORT, CONF_NAME, STATE_IDLE, STATE_OFF,
    STATE_PLAYING, STATE_UNKNOWN)

#Logging Def
logger = logging.getLogger(__name__)

SUPPORT_DTV = SUPPORT_PAUSE | SUPPORT_PLAY_MEDIA | SUPPORT_TURN_OFF | \
    SUPPORT_TURN_ON

#Setup Platform
def setup_platform(hass, config, add_devices, discovery_info=None):

    name = config.get(CONF_NAME, 'DirecTV')
    host = config.get(CONF_HOST)
    port = config.get(CONF_PORT, '8080')

    if host is None:
        return

    add_devices([DirecTV(host, name, port),])

    return True


#Create class for HA
class DirecTV(MediaPlayerDevice):

    def __init__(self, host, name, port):
        self._name = name
        self._host = host
        self._port = port
        self._state = STATE_UNKNOWN
        self._title = None
        self._duration = None
        self._base_url = 'http://%s:%s' % (self._host, self._port)  

    def _make_request(self, url):
        #
        import requests

        try:
            return requests.get(self._base_url + url).json()
        except Exception as e:  
            logger.error(e)
            self._state = STATE_OFF

    def _get_state(self):
        rstate = self._make_request('/info/mode')
        return rstate['mode']

    def _get_tuned(self):
        tuned = self._make_request('/tv/getTuned')
        #Does duration do anything?
        self._duration = tuned['duration']
        title = None

        try:
            title = tuned['title'] + ' : ' + tuned['episodeTitle']
        except:
            try:
                title = tuned['title']
            except:
                pass

        return title


    def _push_button(self, button):
        button = self._make_request('/remote/processKey?key=' + button)
        return True

    def update(self):
        self._state = self._get_state()
        self._title = self._get_tuned()
        return True

    def turn_on(self):
        self._push_button('poweron')

    def turn_off(self):
        self._push_button('poweroff')

    def media_play(self):
        self._push_button('play')

    def media_pause(self):
        self._push_button('pause')

    @property
    def media_duration(self):
        return self._duration


    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property 
    def state(self):
        """Return the state of the device."""
        if self._state is None:
            return STATE_OFF

        if self._state == 1:
            return STATE_IDLE
        else:
            return STATE_PLAYING

    @property
    def media_title(self):
        """Title of current playing media."""
        return self._title

    @property
    def supported_media_commands(self):
        """Flag of media commands that are supported."""
        supported_media_commands = SUPPORT_DTV

        return supported_media_commands
