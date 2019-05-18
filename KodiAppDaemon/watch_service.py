payload = { "entity_id": data.get('player', "media_player.theater"), "search_type": data.get('search_type',"Episodes"), "search_string": data.get('show_name',"Simpsons"), "play_watched": data.get('play_watched',"True"), "play_oldest": data.get('play_oldest',"False"), "play_random": data.get('play_random',"True")}
hass.bus.fire("searchplaykodi",payload)
