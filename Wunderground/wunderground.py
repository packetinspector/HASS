"""Wunderground Sensor """
from datetime import timedelta
import logging
import requests
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import DOMAIN
from homeassistant.util import Throttle
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE, TEMP_FAHRENHEIT

_LOGGER = logging.getLogger(__name__)

#Using Lat/Long, this could be pws or name if you wanted... 
_wu_start_url = 'https://api.wunderground.com/api/'
_wu_query_url = '/radar/conditions/forecast/q/'
_wu_query_format = '.json'
_wu_full_url = _wu_start_url + '{}' + _wu_query_url + '{},{}' + _wu_query_format

#Throttle
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=15)


def setup_platform(hass, config, add_devices, discovery_info=None):
    #Grab config vars
    api_key = config.get(CONF_API_KEY, None)
    latitude = config.get(CONF_LATITUDE, hass.config.latitude)
    longitude = config.get(CONF_LONGITUDE, hass.config.longitude)

    #Validate Config
    if None in (latitude, longitude):
        _LOGGER.error("Lat/Long Missing from Config")
        return False
    if api_key is None:
        _LOGGER.error("API Key Missing")
        return False
    #Download Radar?
    download_radar = config.get('download_radar', False)

    #Lets get the data going
    wu_url = _wu_full_url.format(api_key, latitude, longitude)
    weather_data = WUndergroundData(wu_url, download_radar)

    #Update data
    weather_data.update()

    #Add basic config or do we?
    add_basic = config.get('default_sensors', True)
    sensors_add = []
    if add_basic:
        sensors_add.append(WUndergroundSensor(weather_data, 'temperature'))
        sensors_add.append(WUndergroundSensor(weather_data, 'icon'))

    #Add a device just for templating
    sensors_add.append(WUndergroundSensor(weather_data, 'template'))
    #Actually add devices
    add_devices(sensors_add)

    #Add a service update call
    def update(call=None):
        weather_data.update(no_throttle=True)
        for sensor in sensors_add:
            sensor.update()

    hass.services.register(DOMAIN, 'update_weather', update)


class WUndergroundSensor(Entity):

    def __init__(self, weather, data_type, radar=False):
        """Initialize the sensor."""
        self._weather = weather
        self._data_type = data_type
        self._radar = radar

    @property
    def name(self):
        """Return the name. Goes under sensor name"""
        if self._data_type == 'temperature':
            return 'Temp'
        elif self._data_type == 'icon':
            return 'Condition'
        else:
            #Template
            return 'weather_data'

    @property
    def unit_of_measurement(self):
        """Return the units of measurement."""
        if self._data_type == 'temperature':
            return TEMP_FAHRENHEIT
        else:
            return None

    def update(self):
        self._weather.update()

    @property
    def state(self):
        """Return the state of the sensor."""
        try:
            if self._data_type == 'temperature':
                return self._weather._weather_data['current_observation']['temp_f']
            elif self._data_type == 'icon':
                return self._weather._weather_data['current_observation']['weather']
            else:
                return None
        except:
            return None

    @property
    def entity_picture(self):
        """Return the entity picture."""
        try:
            if self._data_type == 'icon':
                return self._weather._weather_data['current_observation']['icon_url']
            return None
        except:
            return None

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        if self._data_type == 'template':
                return self._weather._weather_data
        else:
            return None

    @property
    def hidden(self):
        """Return True if the entity should be hidden from UIs."""
        if self._data_type == 'template':
            return True
        else:
            return False


class WUndergroundData(object):
    """Get data from Wundeground."""
    def __init__(self, url, radar=False):
        """Initialize the data object."""
        self._url = url
        self._weather_data = None
        self._radar = radar

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Get the latest data from wunderground"""
        try:
            self._weather_data = requests.get(self._url).json()
            _LOGGER.info("Fetching Weather Data")
        except Exception as e:
            _LOGGER.error("Error Connecting to Wundergound: {}".format(str(e)))
            self._weather_data = None

        if self._radar:
            #Grab radar to local disk
            _LOGGER.info("Downloading radar image")
            try:
                url = self._weather_data['radar']['image_url']
                i = requests.get(url, stream=True)
                with open('/tmp/radar.gif', 'wb') as fd:
                    for chunk in i.iter_content(256):
                        fd.write(chunk)
            except:
                _LOGGER.error("Error downloading radar image")
