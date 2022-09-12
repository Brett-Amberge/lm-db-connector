""" Stores user information and query data """

from omni.ui import scene as sc
from pxr import Tf, Usd, UsdGeom
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
        def __init__(self):
            super().__init__()
            self.value = [0, 0, 0]

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
            self._on_stage_event, name="Scene Selection Update"
        )

        # Database information
        self._result = DBModel.ListItem()

    # Get the current UsdContext we are attached to
    def _get_context(self) -> Usd.Stage:
        return omni.usd.get_context()

    # Listen for a SELECTION_CHANGED event
    def _on_stage_event(self, event):
        if event.type == int(omni.usd.StageEventType.SELECTION_CHANGED):
            self._on_kit_selection_changed()

    # Called by Tf.Notice when the currently selected object changes in some way
    def _notice_changed(self, notice: Usd.Notice, stage: Usd.Stage) -> None:
        for p in notice.GetChangedInfoOnlyPaths():
            if self._current_path in str(p.GetPrimPath()):
                self._item_changed(self.position)

    # Update the model when a selection has changed
    def _on_kit_selection_changed(self):
        # Selection changed, reset it for now
        self._current_path = ""
        usd_context = self._get_context()
        stage = usd_context.get_stage()
        if not stage:
            return

        prim_paths = usd_context.get_selection().get_selected_prim_paths()
        if not prim_paths:
            # Turn the manipulator off if nothing is selected
            self._item_changed(self.position)
            return

        prim = stage.GetPrimAtPath(prim_paths[0])
        if not prim.IsA(UsdGeom.Imageable):
            self._prim = None

            if self._stage_listener:
                self._stage_listener.Revoke()
                self._stage_listener = None
            return

        if not self._stage_listener:
            # This handles camera movement
            self._stage_listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._notice_changed, stage)

        self._prim = prim
        self._current_path = prim_paths[0]

        # Position is changed, tell the manipulator to update
        self._item_changed(self.position)

    # Accessor methods
    def get_item(self, id):
        if id == "position":
            return self.position
        if id == "result":
            return self._result
        if id == "name":
            return self._current_path

    def get_value(self, item):
        if item == self.position:
            return self._get_position()

        if item:
            return item.value
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
        if item == self._result:
            self._result.value = changed
        return self.get_value(item)
