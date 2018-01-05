### AppDaemon Setup
```yaml
staterestore:
  module: staterestore
  class: StateRestore
```

### Directions
This should work with most entity types

Fire an event called "staterestore"
entity_id is required for data
The other data will be provisioned to the device and original state stored
An event call with solely entity_id will restore the original state

### Sample Usage 

```yaml
testrestore:
  alias: Test Restore
  sequence:
  - event: staterestore
    event_data:
      brightness: 50
      entity_id: light.light01
      state: on
testrestorereturn:
  alias: Test Restore Return
  sequence:
  - event: staterestore
    event_data:
      entity_id: light.htlight01
```