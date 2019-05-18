import appdaemon.plugins.hass.hassapi as hass


class StateRestore(hass.Hass):

    def initialize(self):
        # Init the dictionary to hold state info
        self.entities = {}
        # Listen for the event and route based on it
        self.listen_event(self.router, "staterestore")

    def router(self, event_name, data, whatever):
        # self.log(data)
        # Can't do anything without this
        if "entity_id" not in data:
            self.log("No Entity Specified. Doing Nothing")
            return
        # Check if entity_id is the only key. If so restore state
        if ("entity_id" in data) and (len(data) == 1):
            self.dorestore(data)
        else:
            e = data["entity_id"]
            # Start a listener to look for changes
            # If the state changes before a restore, this will cancel the restore
            self.startlisten(e, True)
            # Do what was asked in the event
            self.doaction(data)
            # Set a timeout in case you change to the same state and the action doesn't trigger the listener
            self.run_in(self.dotimeout, 5, e=e)

    def startlisten(self, e, force=False):
        self.log("Stopping any other listeners")
        self.stoplisten(e, force=True)
        self.log("Listening for: {}".format(e))
        # Check for an existing listener
        if e not in self.entities:
            self.entities[e] = {}
        self.entities[e]['first'] = True
        self.entities[e]['handle'] = self.listen_state(self.stoplisten, e, force=False)

    def stoplisten(self, e, attribute=None, old=None, new=None, kwargs=None, force=False):
        if e not in self.entities:
            # Nothing to do
            return
        # try:
        #     force = kwargs['force']
        # except KeyError:
        #     force = False
        self.log("Force: {}".format(force))
        if self.entities[e]['first'] is True and not force:
            # The first state change may occur from this script. Ignore it
            self.log("Ignoring first state change of {}".format(e))
            self.entities[e]['first'] = False
        else:
            self.log("Canceling listener for: {}".format(e))
            try:
                self.cancel_listen_state(self.entities[e]['handle'])
                # Remove data from app
                self.entities.pop(e, None)
            except KeyError:
                self.log("Unable to cancel listener. May not have existed")
        return

    def dotimeout(self, kwargs):
        # After waiting remove the first check
        self.log('Removing first state check for {}'.format(kwargs['e']))
        try:
            self.entities[kwargs['e']]['first'] = False
        except KeyError:
            self.log('Error Setting Status. Restore may have been removed')
        return

    def doaction(self, data):
        # Capture entity data
        e = data["entity_id"]
        current_state = self.get_state(entity=e, attribute="all")
        # Odd?
        if current_state is None:
            self.log("Exiting action. No state found for data: {}".format(data))
            return
        # Okay check if we know about it
        if e not in self.entities:
            self.entities[e] = {}
        self.log(current_state)
        # Check the current state to decide what to do
        if current_state['state'] == 'on':
            # It May have attributes we want
            # Take the things you are applying and store their current state in prep for kwargs
            store = {k: current_state['attributes'][k] for (k, v) in data.items() if k not in ['entity_id', 'state']}
            self.log('Captured State: {}'.format(store))
            self.entities[e]['data'] = store
        else:
            # Turn off
            self.entities[e]['data'] = {}
        self.entities[e]['state'] = current_state['state']

        # Seems the yaml sometimes returns on as True, just test for either..
        if data["state"] is True or data["state"] == 'on':
            # Turn something on
            self.log("Turning {} on".format(e))
            self.turn_on(e, **{k: v for (k, v) in data.items() if k not in ['entity_id', 'state']})
        else:
            # Turn something off
            self.log("Turning {} off".format(e))
            self.turn_off(e)

    def dorestore(self, data):
        e = data["entity_id"]
        self.log("Restoring state of {}".format(e))
        if e not in self.entities:
            self.log("No restore for: {}".format(e))
            return
        # Check the state we need to move to
        if self.entities[e]['state'] == 'on':
            self.turn_on(e, **self.entities[e]['data'])
        else:
            self.turn_off(e)
        # Cancel the listener just in case
        self.stoplisten(e, force=True)
