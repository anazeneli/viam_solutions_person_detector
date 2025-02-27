# Module simple-person-sensor 

The simple-person-sensor is a basic virtual sensor designed to detect whether 
a person is present in a camera frame. 
The simple-person-sensor retrieves detection data from a vision service
and outputs a simple boolean value (1 if a person is detected, 0 otherwise). 
This module is intended as a simple example for building more complex 
robotic systems, acting as an intermediate for more advanced sensor designs.


## Model anazen:simple-person-sensor:person-sensor

This model represents a sensor that interacts with a vision service to detect 
people in a camera's field of view. It is used to gather data on human
presence, which can be leveraged in larger systems for tasks like human-robot 
interaction, monitoring, or triggering events based on human detection.

"person_detected" indicates whether a person is present in the frame:
 - 1 means a person is detected.
 - 0 means no person is detected.

The results per frame are logged. 

### Configuration
The following attribute template can be used to configure this model:

```json
{
  "camera_name": "<string>",
  "vision_service": "<string>"
}

```

#### Attributes

The following attributes are available for this model:

| Name          | Type   | Inclusion | Description                |
|---------------|--------|-----------|----------------------------|
| `camera_name`    | string  | Required  | The name of the camera to be used for detection.|
| `vision_service` | string  | Required  | The name of the vision service to query for detections. |

#### Example Configuration

```json
{
  "camera_name": "webcam",
  "vision_service": "object_detection_service"
}

```

### GetReadings

The simple-person-sensor module provides a get_readings method to retrieve sensor data. 
This method communicates with the configured vision service to detect whether a person 
is present in the camera frame. It returns a mapping where the key "person_detected" 
is set to either 0 or 1 based on whether a person is in the frame.


#### Example GetReadings Response

```json
{
  "person_detected": 1
}

```
