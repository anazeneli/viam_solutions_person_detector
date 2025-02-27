from typing import (Any, ClassVar, Dict, Final,
                    cast, List, Mapping, Optional,
                    Sequence)

from typing_extensions import Self
from viam.components.sensor import *
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import Geometry, ResourceName
from viam.resource.base import ResourceBase
from viam.resource.easy_resource import EasyResource
from viam.resource.types import Model, ModelFamily
from viam.utils import SensorReading, ValueTypes
from viam.services.vision import Vision
from viam.components.camera import Camera



class PersonSensor(Sensor, EasyResource):
    MODEL: ClassVar[Model] = Model(
        ModelFamily("anazen", "simple-person-sensor"), "person-sensor"
    )

    def __init__(self, name: str):
        super().__init__(name=name)
        self.camera_name = None
        self.vision_service = None

    @classmethod
    def new(
        cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ) -> Self:
        """This method creates a new instance of this Sensor component.
        The default implementation sets the name from the `config` parameter and then calls `reconfigure`.

        Args:
            config (ComponentConfig): The configuration for this resource
            dependencies (Mapping[ResourceName, ResourceBase]): The dependencies (both implicit and explicit)

        Returns:
            Self: The resource
        """
        return super().new(config, dependencies)

    @classmethod
    def validate_config(cls, config: ComponentConfig) -> Sequence[str]:
        """
        This method ensures that the required configuration fields (`camera_name` 
        and `vision_service`) are present and valid, and checks their data types 
        (string values). It will raise an exception if any required fields are missing 
        or if they are of an incorrect type. It returns a list of implicit dependencies 
        that are needed for the sensor component to function.

        Args:
            config (ComponentConfig): The configuration for this resource

        Returns:
            Sequence[str]: A list of implicit dependencies

        Raises:
            ValueError: If any required configuration fields are missing.
            TypeError: If any configuration fields have incorrect data types (e.g., 
                    non-string values for `camera_name` or `vision_service`).
            Exception: If any required configuration fields have empty values.            
        """
        # Validate required fields 
        required_fields = ["vision_service", "camera_name"]
        dependencies = []

        # Validate each required field and store values in dependencies
        for field in required_fields:
            field_value = config.attributes.fields.get(field)
            
            # Both expected values are strings 
            if not field_value or not field_value.HasField("string_value"):
                raise ValueError(f"'{field}' attribute is missing or not a valid string.")
            
            field_value = field_value.string_value
            
            if not field_value:
                raise ValueError(f"'{field}' attribute cannot be an empty string.")
            
            # Add to dependencies
            dependencies.append(field_value)

        # Now dependencies list contains both camera_name and vision_service
        return dependencies
    

    def reconfigure(
        self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ):
        """
            Dynamically updates the service configuration based on the provided `config` object.
            This method is used to reconfigure the sensor by retrieving a new camera name and 
            vision service, setting them as attributes for later use in detection and sensor readings.

            Args:
                config (ComponentConfig): The new configuration object containing attributes 
                                        such as camera name and vision service name.
                dependencies (Mapping[ResourceName, ResourceBase]): A mapping of dependencies, 
                                                                including the vision service 
                                                                resource, that are required 
                                                                for reconfiguration.
            
            Logs:
                - Logs an info message when the reconfiguration process starts.
        """

        # Get camera_name and vision_service_name from config
        camera_name = config.attributes.fields["camera_name"].string_value
        vision_service_name = config.attributes.fields["vision_service"].string_value

        # Get the vision_service from dependencies
        vision_service_resource = dependencies[Vision.get_resource_name(vision_service_name)]
        vision_service = cast(Vision, vision_service_resource)

        # Set dependencies 
        self.vision_service = vision_service

        # Set camera name for get_detections_from_camera later
        # This is how we retrieve the detections to set the sensor readings 
        self.camera_name = camera_name

        return super().reconfigure(config, dependencies)

    async def get_readings(
        self,
        *,
        extra: Optional[Mapping[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Mapping[str, SensorReading]:
        """
            Retrieves sensor readings by querying the vision service for detections from the 
            configured camera. The method checks if a person is detected in the camera frame 
            and returns a mapping with a boolean value indicating whether a person is present.

            The method communicates with the vision service to retrieve detection data, 
            processes it to identify a "person" class, and logs the results.

            Args:
                extra (Optional[Mapping[str, Any]]): Additional parameters that can be passed 
                                                    with the request. Defaults to None.
                timeout (Optional[float]): The maximum time, in seconds, to wait for the 
                                        detection request to complete. Defaults to None.
                **kwargs: Additional keyword arguments that may be passed to the method.

            Returns:
                Mapping[str, SensorReading]: A dictionary where the key `"person_detected"` 
                                            maps to an integer (0 or 1), indicating whether 
                                            a person was detected in the camera frame.

            Raises:
                Exception: If an error occurs while retrieving the detections or if the 
                        vision service does not support detection.

            Logs:
                - A debug message indicating whether a person was detected or not.
                - An error message if an exception occurs during the detection process.
        """
        
        try:
            person_in_frame = 0

            # confidence threshold set by external vision service
            try: 
                detections = await self.vision_service.get_detections_from_camera(self.camera_name)
            except: 
                # Check the properties of vision service if we fail for more thorough debugging 
                properties = await self.vision_service.get_properties()

                # Check if the vision service supports detection methods
                if not properties.detections_supported:
                    raise Exception(f"Vision service {self.vision_service} does not support detection. Vision service must support detection.")


            # a single instance of a person will trigger this sensor 
            person_in_frame = 1 if any(d.class_name.lower() == "person" for d in detections) else 0

            if person_in_frame:
                self.logger.debug("Person detected.")
    
            else:
                self.logger.debug("No person detected.")
    
        except Exception as e:
            self.logger.error(f"Error retrieving detections: {e}")

        return {
            "person_detected": person_in_frame
        }


    async def do_command(
        self,
        command: Mapping[str, ValueTypes],
        *,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Mapping[str, ValueTypes]:
        raise NotImplementedError()

    async def get_geometries(
        self, *, extra: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None
    ) -> List[Geometry]:
        raise NotImplementedError()

