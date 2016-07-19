# Home Assistant Component for Weather Underground

##Add file to:

```
<config_dir>/custom_components/sensor/wunderground.py
```

##Basic Config:

```yaml
- platform: wunderground
  api_key: <API_KEY>
```

This will use lat/long and create two sensors for Temperature and Conditions(icon).  

##Advanced Config:

```yaml
- platform: wunderground
  api_key: <API_KEY>
  default_sensors: True
  download_radar: True
```

Any configuration creates a (hidden) weather data entity that you can then use with templates.  Example:

```yaml
- platform: template
  sensors:
    feels_like_temp:
      value_template: '{{ states.sensor.weather_data.attributes.current_observation.feelslike_f }}'
      friendly_name: 'Feels Like'
      unit_of_measurement: '°F'
      entity_id: 
        - sensor.weather_data

    relative_humidity:
      value_template: '{{ states.sensor.weather_data.attributes.current_observation.relative_humidity|replace("%", "") }}'
      friendly_name: 'Relative Humidity'
      unit_of_measurement: '%'
      entity_id: 
        - sensor.weather_data

    uv:
      value_template: '{{ states.sensor.weather_data.attributes.current_observation.UV }}'
      friendly_name: 'UV'
      entity_id:
        - sensor.weather_data

    forecast_night:
      friendly_name: 'Night'
      value_template: >
        '{{ states.sensor.weather_data.attributes.forecast.txt_forecast.forecastday[1] .title + 
        ': ' +states.sensor.weather_data.attributes.forecast.txt_forecast.forecastday[1].fcttext }}'
      entity_id: 
        - sensor.weather_data

    forecast_tom_day:
      friendly_name: 'Forecast Tomorrow'
      value_template: >
          '{{ states.sensor.weather_data.attributes.forecast.txt_forecast.forecastday[2] .title + 
          ': ' +states.sensor.weather_data.attributes.forecast.txt_forecast.forecastday[2].fcttext }}'
      entity_id: 
        - sensor.weather_data
```

###Groups

You can make those too:

```yaml
Weather:
  name: Weather
  icon: mdi:umbrella
  entities:
    - sensor.condition 
    - sensor.feels_like_temp
    - sensor.temp
    - sensor.relative_humidity
    - sensor.uv
```


###Radar Image
If enabled, a radar image will be downloaded via the API and stored locally.  You can view it by:

```yaml
camera:
  platform: local_file
  name: radar
  file_path: /tmp/radar.gif
```
Would have rather used a template device for this radar image, but there is no display method I could find to do that. 

###Notes

- Weather updates every 15 mins