"""
Model class that stores database connection information and metadata from selected object.
Sets up listeners for scene selections and updated based on the object that is selected.
"""

from omni.ui import scene as sc
from pxr import Tf, Usd, UsdGeom
import omni.usd
import carb


class DBModel(sc.AbstractManipulatorModel):

    # Abstract classes to store model data
    class StringItem(sc.AbstractManipulatorItem):
        def __init__(self, value=""):
            self.value = value

    class ListItem(sc.AbstractManipulatorItem):
        def __init__(self, value=[]):
            self.value = value

    class BoolItem(sc.AbstractManipulatorItem):
        def __init__(self, value=False):
            self.value = value

    class ConnectionItem(sc.AbstractManipulatorItem):
        def __init__(self, value=None):
            self.value = value

    # Constructor
    def __init__(self):
        super().__init__()

        # Currently selected prim
        self._prim = None
        self._current_path = ""

        self._stage_listener = None

        # Save the UsdContext
        usd_context = self._get_context()

        # Get the event stream from the current USD Stage.
        # Listen for any selection updates on the stream.
        self._events = usd_context.get_stage_event_stream()
        self._stage_event_sub = self._events.create_subscription_to_pop(
            self._on_stage_event, name="Scene Selection Update"
        )

        # Database information
        self._result = DBModel.ListItem()
        self._connected = DBModel.BoolItem()
        self._cnx = DBModel.ConnectionItem()

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
                self._item_changed(self._current_path)

    # Update the model when a selection has changed.
    # Called when a SELECTION_CHANGED event occurs on the current stage.
    def _on_kit_selection_changed(self):
        # Selection changed, reset it for now
        self._current_path = ""
        usd_context = self._get_context()
        stage = usd_context.get_stage()
        if not stage:
            return
        # Find the prim path of the current selection, if anything is selected
        prim_paths = usd_context.get_selection().get_selected_prim_paths()
        if not prim_paths:
            # Turn the manipulator off if nothing is selected
            self.set_value(self._result, [])
            self._item_changed(self._current_path)
            return
        # Retrieve the prim at the current path
        prim = stage.GetPrimAtPath(prim_paths[0])
        if not prim.IsA(UsdGeom.Imageable):
            self._prim = None
            # Return if the current prim is not a USD geomtry object
            if self._stage_listener:
                self._stage_listener.Revoke()
                self._stage_listener = None
            return

        # If the stage listener was cleared, recreate it and register object events
        if not self._stage_listener:
            # This handles camera movement
            self._stage_listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._notice_changed, stage)

        # Update the model
        self._prim = prim
        self._current_path = prim_paths[0]

        # Position is changed, tell the manipulator to update
        self._item_changed(self._current_path)

    # Accessor methods for retrieveing private values
    def get_item(self, id):
        if id == "result":
            return self._result
        if id == "name":
            return self._current_path
        if id == "connected":
            return self._connected
        if id == "cnx":
            return self._cnx

    def get_value(self, item):
        if item:
            return item.value
        return False

    # Updater methods for chaning private values
    def set_value(self, item, changed):
        if item == self._result:
            self._result.value = changed
        if item == self._connected:
            self._connected.value = changed
        if item == self._cnx:
            self._cnx.value = changed
        return self.get_value(item)
