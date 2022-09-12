""" Manipulator for getting data from selected object in scene.
    Displays information retrieved from database via USD object's metadata.
"""

from omni.ui import scene as sc
from omni.ui import color as cl
import omni.ui as ui
import omni.kit
import carb

# Attempt to import the mysql package
try:
    import pymysql
except ImportError:
    carb.log_warn("[lm.db.connector] pymysql not found, attempting to install")
    omni.kit.pipapi.install("pymysql")
    import pymysql


class SceneSelector(sc.Manipulator):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._cnx = None
        self._connected = False
        self._window = ui.Window("Database UI", width=200, height=200)

        self.build_ui()

    # Rebuild when the model is changed
    def on_build(self):
        if not self.model:
            return

        if self.model.get_item("name") == "":
            return

        self.connect()

        query = "SELECT meta FROM omnitest WHERE pth=" + "\"" + self.model.get_item('name') + "\""
        res = self.query(query)
        carb.log_warn(res[0])
        self.model.set_value(self.model.get_item("result"), res)

        position = self.model.get_value(self.model.get_item("position"))

        # Move everything to where the selected object is
        with sc.Transform(transform=sc.Matrix44.get_translation_matrix(*position)):
            # Rotate everything to look at the camera
            with sc.Transform(look_at=sc.Transform.LookAt.CAMERA):
                sc.Label(f"Prim: {self.model.get_item('name')}", alignment=ui.Alignment.LEFT_BOTTOM)

        self.build_ui()

    # Regenerates the manipulator
    def on_model_updated(self, item):
        self.invalidate()

    # Attempt to connect to the sql database with user provided username and password
    def connect(self):
        try:
            self._cnx = pymysql.connect(user='root', password='', host='127.0.0.1', port=3306,
                                        database='sakila')
            self._connected = True
        except:
            # Alert the user if the connection fails
            carb.log_warn("Failed to connect to database")
            return False

    def query(self, query=False):
        if self._connected:
            with self._cnx:
                with self._cnx.cursor() as cursor:
                    cursor.execute(query)
                    result = cursor.fetchone()
                    return result
        else:
            carb.log_warn("[lm.db.connector] Connection error")

    # Build UI elements based on data stored in model
    def build_ui(self):
        with self._window.frame:
            ui.Label(f"Query result: {self.model.get_value(self.model.get_item('result'))}")
