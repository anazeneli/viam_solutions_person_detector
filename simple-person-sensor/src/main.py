import asyncio
from viam.module.module import Module
from .models.person_sensor import PersonSensor


if __name__ == '__main__':
    asyncio.run(Module.run_from_registry())

