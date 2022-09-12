""" Manipulator for getting data from selected object in scene.
    Displays information retrieved from database via USD object's metadata.
"""

from omni.ui import scene as sc
from omni.ui import color as cl
import omni.ui as ui
import omni.kit
import carb

from .styles import *

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
        self._user = ""
        self._password = ""
        self._window = ui.Window("Database UI", width=300, height=200)

        self.build_ui()

    # Rebuild when the model is changed
    def on_build(self):
        if not self.model:
            return

        if self.model.get_item("name") == "":
            return

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
    def connect(self, user, password):
        try:
            self._cnx = pymysql.connect(user=user, password=password, host='127.0.0.1', port=3306, database='sakila')
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

    # UI element functions
    def on_changed(self, item, value):
        if item == 'user':
            self._user = value
        if item == 'pass':
            self._password = value

    def on_pressed(self):
        self.connect(self._user, self._password)
        self.build_ui()

    # Build UI elements based on data stored in model
    def build_ui(self):
        with self._window.frame:
            if not self._connected:
                with ui.VStack(height=0):
                    with ui.HStack():
                        ui.Label("User:", style=lab_style)
                        uField = ui.StringField()
                        uField.model.add_end_edit_fn(lambda m, item='user':
                                                    self.on_changed(item, m.get_value_as_string()))
                    with ui.HStack():
                        ui.Label("Password:", style=lab_style)
                        pField = ui.StringField(password_mode=True)
                        pField.model.add_end_edit_fn(lambda m, item='pass':
                                                    self.on_changed(item, m.get_value_as_string()))
                    ui.Button("Connect", style=btn_style, clicked_fn=lambda: self.on_pressed())
            else:
                ui.Label("Connection successful")
