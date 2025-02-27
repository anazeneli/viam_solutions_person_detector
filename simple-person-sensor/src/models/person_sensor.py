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
        """This method allows you to validate the configuration object received from the machine,
        as well as to return any implicit dependencies based on that `config`.

        Args:
            config (ComponentConfig): The configuration for this resource

        Returns:
            Sequence[str]: A list of implicit dependencies
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
        """This method allows you to dynamically update your service when it receives a new `config` object.

        Args:
            config (ComponentConfig): The new configuration
            dependencies (Mapping[ResourceName, ResourceBase]): Any dependencies (both implicit and explicit)
        """
        # Get camera_name and vision_service_name from config
        camera_name = config.attributes.fields["camera_name"].string_value
        vision_service_name = config.attributes.fields["vision_service"].string_value

        # Get the vision_service from dependencies
        vision_service_resource = dependencies[Vision.get_resource_name(vision_service_name)]
        self.vision_service = cast(Vision, vision_service_resource)

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
        try:
            person_in_frame = 0

            # confidence threshold set by external vision service
            detections = await self.vision_service.get_detections_from_camera(self.camera_name)

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

