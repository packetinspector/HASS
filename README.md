# Home Assistant Stuff

##Random Tidbits

####Internet Up?
```yaml
- platform: command_line
  command: 'ping -qc3 8.8.8.8 > /dev/null && echo "on" || echo "off"'
  name: 'Internet'
  sensor_class: moving
  payload_on: "on"
  payload_off: "off"
  scan_interval: 1800
```
