"""Send notifications to Kodi(xbmc)"""

import logging
from homeassistant.components.notify import (ATTR_TITLE, DOMAIN, BaseNotificationService)
from homeassistant.const import (CONF_HOST, CONF_PORT, CONF_NAME)
#Logger
_LOGGER = logging.getLogger(__name__)


def get_service(hass, config):

    #name = config.get(CONF_NAME, 'Kodi')
    host = config.get(CONF_HOST)
    port = config.get(CONF_PORT, '8080')

    if host is None:
        return

    return KodiNotificationService(host, port)


class KodiNotificationService(BaseNotificationService):

    def __init__(self, host, port):
        self._kodi = host
        self._port = port

    def send_message(self, message="", **kwargs):
        #Send message
        title = kwargs.get(ATTR_TITLE)
        if title is None:
            title = 'Home Assistant'
        to_post = {"id": 1, "jsonrpc": "2.0", "method": "GUI.ShowNotification", "params": {"title": title, "message": message}}
        try:
            import requests
            r = requests.post('http://{}:{}/jsonrpc'.format(self._kodi, self._port), json=to_post, timeout=2)
            if r.status_code == requests.codes.ok:
                _LOGGER.info('Kodi Message Sent')
            else:
                _LOGGER.info(r.text)
        except Exception as e:
            _LOGGER.error(str(e))
