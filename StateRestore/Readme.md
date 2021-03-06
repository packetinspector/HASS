### Purpose
Set the state of something and when ready return that entity to its original state. 
e.g.  Turn a light a particular color when motion detected, return when motion is clear



### Directions
This should work with most entity types

* Fire an event called "staterestore"
* entity_id is required for all invocations
* An event call with solely entity_id will restore the original state
* You must include state "on" or "off" for non restore invocations
* Other event_data will be provisioned to the device and the original attributes stored
* On restore the original attributes and state will be provisioned
* A listener is added to the invoked entity_id and on change will clear the stored attributes
 * (Script turns light off, someone turns it on, on script's restore it will stay on)

### AppDaemon Setup
```yaml
staterestore:
  module: staterestore
  class: StateRestore
```

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
      white_value: 0
      rgb_color:
      - 22
      - 165
      - 0
testrestorereturn:
  alias: Test Restore Return
  sequence:
  - event: staterestore
    event_data:
      entity_id: light.light01
```
