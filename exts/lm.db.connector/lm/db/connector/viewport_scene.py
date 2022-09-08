""" Adds the manipulator and model to the viewport scene
"""

from omni.ui import scene as sc
import omni.ui as ui

from .db_model import DBModel
from .scene_selector import SceneSelector


class ViewportScene():
    # The Scene Selector Manipulator, placed in a viewport

    def __init__(self, viewport_window: ui.Window, ext_id: str) -> None:
        self._scene_view = None
        self._viewport_window = viewport_window

        # Create a unique frame for the scene view
        with self._viewport_window.get_frame(ext_id):

            self._scene_view = sc.SceneView()
            # Add the manipulator into the scene
            with self._scene_view.scene:
                SceneSelector(model=DBModel())

            # Register the SceneView with the Viewport to get projection and view updates
            self._viewport_window.viewport_api.add_scene_view(self._scene_view)

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self._scene_view:
            # Empty the SceneView
            self._scene_view.scene.clear()
            # Unregister the SceneView from the Viewport updates
            if self._viewport_window:
                self._viewport_window.viewport_api.remove_scene_view(self._scene_view)
            # Remove references to these objects
            self._viewport_window = None
            self._scene_view = None
