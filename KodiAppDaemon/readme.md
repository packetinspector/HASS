### Kodi and AppDaemon
Use simple search via show name to play something on a Kodi machine.

Supports Recordings and TV Episodes currently. 

Uses:

* Appdaemon 3.x
* HA w/ Kodi media player component
* Kodi 17.x (no addons needed)

### AppDaemon Setup
```yaml
kodifunctions:
  module: kodifunctions
  class: SearchPlayKodi
```

###Sample Script
```yaml
playnewsfrompvr:
  alias: PlayTheNews
  sequence:
  - event: searchplaykodi
    event_data:
      entity_id: media_player.mb
      search_string: local news
```
> This will play the most recent recording of a show named: "local news" :sparkles:

This was designed to be called from an event or invoked via script(above), but you can make a simple frontend for it in HA

![screen1](https://github.com/packetinspector/HASS/raw/master/KodiAppDaemon/frontend.png)

####Configuration.yaml
```yaml
input_boolean:
  kodi_play_watched:
    name: Play Watched
    initial: off
input_text:
  kodi_search:
    name: Kodi Search
    min: 3
input_select:
  kodi_search_type:
    name: Kodi Type
    options:
      - Recordings
      - Episodes
  kodi_players:
    name: Kodi Player
    options:
      - media_player.player1
      - media_player.player2
  kodi_play_mode:
    name: Kodi Play Mode
    options:
      - Newest
      - Oldest
      - Random
```

####Groups.yaml
```yaml
KodiPlayer:
  name: Kodi Player
  entities:
    - input_text.kodi_search
    - input_select.kodi_search_type
    - input_select.kodi_play_mode
    - input_select.kodi_players
    - input_boolean.kodi_play_watched
    - script.kodiplaysearch
```

####scripts.yaml
```yaml
kodiplaysearch:
  alias: Play Search
  sequence:
  - event: searchplaykodi
    event_data: {}
```

For script invocation you can use these examples:

```json
# Basic search
# { "entity_id": "media_player.player1", "search_string": "show title"}
# Full search
# { "entity_id": "media_player.player1", "search_string": "show title", "play_watched": "False", "play_oldest": "True", "play_random": False}
```
