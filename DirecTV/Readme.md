# Home Assistant Component for DirecTV

Media Player Component.  Add them like:

```yaml
media_player:
    platform: directv
    host: <IP-ADDRESS>
    name: <NAME>
```

Script will grab now playing info and status.  Play/Pause/PowerOnOff are supported.