# signal-application-python-sdk

# Setup

### Add Signal-Application-SDK as a dependency to requirements.txt
```
signal-application-python-sdk==<latest>
```

### Install dependencies
```
python setup.py install
```

Entry point for Signal Application SDK
* Creates a bi-directional communication between device agent and application

### Initialize SDK
```
from signalsdk.signal_app import SignalApp
app = SignalApp()
app.initialize(onConfigUpdated, onEventReceived, onCommandReceived)
```

### Provide a callback method to get notified when a configuration change is requested
```
def onConfigUpdated(self, config):
```
* Will be triggered when a new configuration change requested from the cloud


### Provide a callback method to get notified when an event is received from event bus
```
def onEventReceived(self, event):
```
* Will be triggered when a new event received from application's subscribed topic

### Provide a callback method to get notified when an command is received from event bus
```
def onCommandReceived(self, command):
```
* Will be triggered when a new command received from device agent

### Call next to forward the event to the next edgesignal application which has sdk integrated, if next_app_id(optional) is specified, it forwards the event to the specified application
```
self.app.next(event: object, next_app_id)
```

### Call next to forward the event to the next node-red application running on node-red.
```
self.app.nextNode(event: object)
```


### Sample usage
Consider adding these two params to the application detail
![Settings](settings_list.png)
![Settings](settings.png)

config object will be reveived as below

```
{
    message: 'some text message',
    param2: 101
}
```

 