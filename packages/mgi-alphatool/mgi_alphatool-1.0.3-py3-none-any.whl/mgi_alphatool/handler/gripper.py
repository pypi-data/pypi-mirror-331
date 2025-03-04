from . import Handler

from typing import Literal, Union
from ..labware import Column, Labware, Well
from ..module import Module
# from ..labware.trashbin import TrashBin
from ..commands.command import Location
from ..commands.labware import MoveLabwareParams, MoveLabwareCommand
# from ..commands.pipette import (MoveToCommand, MoveToParams,
#                                MoveToAreaCommand, MoveToAreaParams)

class Gripper(Handler):
    def __init__(self, id: str, name: str, mount: str, context: 'Context'):
        super().__init__(id, name, mount, context)

    def move_labware(self, labware: Labware, 
                     location: Union[int, Module, Labware]) -> 'Gripper':
        """Move labware to a new location using the gripper.

        Args:
            labware (Labware): The labware to move.
            location (Union[int, Module, Labware]): Target location (deck slot, module, or labware).
        """
        if isinstance(location, (Module, Labware)):
            new_loc = Location(moduleId=location.id()) if isinstance(location, Module) else Location(labwareId=location.id())
            labware._set_slot(location._get_slot())
        else:
            new_loc = Location(slotName=str(location))
            labware._set_slot(location)

        self.__context._append_command(MoveLabwareCommand(
            params=MoveLabwareParams(
                labwareId=labware.id(),
                strategy='usingGripper',
                newLocation=new_loc
            )
        ))
        return self
    
    # def move_to(self, location: Union[Well, Column, TrashBin],
    #             position: Literal['top', 'bottom'] = 'top',
    #             offset: int = 5) -> 'Gripper':
    #     """Move the gripper to a specified location. This method moves the gripper to the given well or column or trash bin location.

    #     Args:
    #         location (Union[Well, Column, TrashBin]): The target well or column to move to. Also support the moving to the trash bin.
    #         position (str, optional): The position within the well. Wether the 'top' of the well or 'bottom' of the well. Defaults to 'top'.
    #         offset (int, optional): The vertical offset in millimeters from the specified position. Positive values move up, negative values move down. Defaults to 5 mm.
        
    #     Returns:
    #         Gripper: The gripper instance after moving.
    #     """
    #     self.__validate_location(location)

    #     if isinstance(location, TrashBin):
    #         self._get_context()._append_command(MoveToAreaCommand(
    #             params=MoveToAreaParams(pipetteId=self.id(),
    #                                     addressableAreaName='fixedTrash',
    #                                     offset={'x':0,'y':0,'z':offset})))
    #     else:
    #         if isinstance(location, Well):
    #             well_name = location.id()
    #         elif isinstance(location, Column):
    #             well_name = location.wells()[0].id()

    #         self._get_context()._append_command(MoveToCommand(
    #             params=MoveToParams(pipetteId=self.id(),
    #                                 labwareId=location._get_parent().id(),
    #                                 wellName=well_name,
    #                                 wellLocation={"origin": position,
    #                                               "offset":{'x':0,
    #                                                         'y':0,
    #                                                         'z':offset}})))
        
    #     self._get_context()._set_arm_location(location)
    #     return self