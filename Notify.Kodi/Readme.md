# Home Assistant Component for Kodi Notifications

##Add file to:

```
<config_dir>/custom_components/notify/kodi.py
```

##Basic Config:

```yaml
notify:
  - platform: kodi
    name: message_kodi_j
    port: 8080
    host: <IP.ADDRESS>

  - platform: kodi
    name: message_kodi_k
    port: 80
    host: <HOSTNAME>
```

##Notes

- This is alpha
- Better way to do this with media player component?