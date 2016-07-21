# Home Assistant Stuff

##Random Tidbits

####Internet Up?
```yaml
- platform: command_line
  command: 'ping -qc3 8.8.8.8 > /dev/null;echo $?'
  name: 'Internet'
  sensor_class: moving
  payload_on: "0"
  payload_off: "1"
  scan_interval: 1800
```
