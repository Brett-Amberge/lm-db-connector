""" Manipulator for getting data from selected object in scene.
    Displays information retrieved from database via USD object's metadata.
"""

from omni.ui import scene as sc
from omni.ui import color as cl
import omni.ui as ui


class SceneSelector(sc.Manipulator):

    # Rebuild when the model is changed
    def on_build(self):
        if not self.model:
            return

        if self.model.get_item("name") == "":
            return

        position = self.model._get_postion()

        # Move everything to where the selected object is
        with sc.Transform(transform=sc.Matrix44.get_translation_matrix(*position)):
            # Rotate everything to look at the camera
            with sc.Transform(look_at=sc.Transform.LookAt.CAMERA):
                sc.Label(f"Prim: {self.model.get_item('name')}", alignment=ui.Alignment.LEFT_BOTTOM)

    # Regenerates the manipulator
    def on_model_updated(self):
        self.invalidate()
