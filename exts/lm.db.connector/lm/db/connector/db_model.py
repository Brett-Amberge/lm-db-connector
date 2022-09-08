""" Stores user information and query data """

from omni.ui import scene as sc
from pxr import Tf, Usd, UsdGeom, UsdShade
import omni.usd

# The distance to raise above the top of the object's bounding box
TOP_OFFSET = 5


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
    def get_item(self, id):
        if id == "position":
            return self.position
        if id == "user":
            return self._user
        if id == "pass":
            return self._pass
        if id == "result":
            return self._result

    def get_value(self, item):
        if item == self.position:
            return self._get_position()

        if item == self._user:
            item.value
        return False

    def _get_position(self):
        stage = self._get_context().get_stage()
        if not stage or not self._current_path:
            return [0, 0, 0]

        prim = stage.GetPrimAtPath(self._current_path)
        box_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), includedPurposes=[UsdGeom.Tokens.default_])
        bound = box_cache.ComputeWorldBound(prim)
        range = bound.ComputeAlignedBox()
        bboxMin = range.GetMin()
        bboxMax = range.GetMax()

        position = [(bboxMin[0] + bboxMax[0]) * 0.5, bboxMax[1] + TOP_OFFSET, (bboxMin[2] + bboxMax[2]) * 0.5]
        return position

    # Updater methods
    def set_value(self, item, changed):
        if item == self._user:
            self._user.value = changed
        if item == self._pass:
            self._pass.value = changed
        if item == self._result:
            self._result.value = changed
        return self.get_value(item)
