""" Stores user information and query data """

from omni.ui import scene as sc
from pxr import Tf, Usd, UsdGeom, UsdShade
import omni.usd


class DBModel(sc.AbstractManipulatorModel):

    # Abstract classes to store model data
    class StringItem(sc.AbstractManipulatorItem):
        def __init__(self, value=""):
            self.value = value

    class ListItem(sc.AbstractManipulatorItem):
        def __init__(self, value=[]):
            self.value = value

    class PositionItem(sc.AbstractManipulatorItem):
        def __init__(self, value=[0, 0, 0]):
            self.value = value

    def __init__(self):
        super().__init__()

        # Currently selected prim
        self._prim = None
        self._current_path = ""

        self._stage_listener = None
        self.position = DBModel.PositionItem()

        # Save the UsdContext
        usd_context = self._get_context()

        # Track Selection changes
        self._events = usd_context.get_stage_event_stream()
        self._stage_event_sub = self._events.create_subscription_to_pop(
            self._on_stage_event, name="Scene Selector Selection Update"
        )

        # Database information
        self._user = DBModel.StringItem()
        self._pass = DBModel.StringItem()
        self._result = DBModel.ListItem()

    # Get the current UsdContext we are attached to
    def _get_context(self) -> Usd.Stage:
        return omni.usd.get_context()

    # Listen for a SELECTION_CHANGED event
    def _on_stage_event(self, event):
        if event.type == int(omni.usd.StageEventType.SELECTION_CHANGED):
            self._on_kit_selection_changed()

    # Update the model when a selection has changed
    def _on_kit_selection_changed(self):
        pass

    # Accessor methods
    def get_user(self):
        return self._user

    def get_pass(self):
        return self._pass

    def get_result(self):
        return self._result

    def get_value(self, item):
        if item == self._user:
            return self._user.value
        if item == self._pass:
            return self._pass.value
        if item == self._result:
            return self._result.value
        return False

    # Updater methods
    def set_value(self, item, changed):
        if item == self._user:
            self._user.value = changed
        if item == self._pass:
            self._pass.value = changed
        if item == self._result:
            self._result.value = changed
        return self.get_value(item)
