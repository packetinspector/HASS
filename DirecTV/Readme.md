# Home Assistant Component for DirecTV

##Add file to:

```
<config_dir>/custom_components/media_player/directv.py
```

Media Player Component.  Add them like:

```yaml
media_player:
    platform: directv
    host: <IP-ADDRESS>
    name: <NAME>
```

Script will grab now playing info and status.  Play/Pause/PowerOnOff are supported.