"""
Main extension file for connecting to mysql database.
This is the file that Omniverse searchs for when launching the extension.
"""

import omni.ext
import omni.ui as ui
import carb
from omni.kit.viewport.utility import get_active_viewport_window

from .viewport_scene import ViewportScene


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class Connector(omni.ext.IExt):

    # Constructor
    def __init__(self):
        self._viewport_scene = None

    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):

        print("[lm.db.connector] MyExtension startup")

        # Get the active Viewport
        viewport_window = get_active_viewport_window()

        if not viewport_window:
            carb.log_error(f"No Viewport Window to add {ext_id} scene to")
            return

        # Build out the scene, passing the active viewport window to the scene object
        self._viewport_scene = ViewportScene(viewport_window, ext_id)

    def on_shutdown(self):
        print("[lm.db.connector] MyExtension shutdown")
