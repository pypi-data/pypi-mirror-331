from . import Labware

class WellPlate(Labware):
    def __init__(self, id: str, labware_name: str, slot: int, definition: dict, context: 'Context'):
        super().__init__(id, labware_name, slot, definition, context)
    
    def _get_default_mag_height(self):
        return self._get_definition()['parameters'].get('magneticModuleEngageHeight', None)