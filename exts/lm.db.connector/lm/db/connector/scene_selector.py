"""
Manipulator for displaying data from selected object in scene.
Contols the user interface and displays information retrieved from database via USD object's metadata.
"""

from omni.ui import scene as sc
from omni.ui import color as cl
import omni.ui as ui
import omni.kit
import carb

from .styles import *


try:
    import pyodbc
except ImportError:
    carb.log_warn("pyodbc not found, attempting to install")
    omni.kit.pipapi.install("pyodbc")
    import pyodbc


class SceneSelector(sc.Manipulator):

    # Constructor, setting up some user data and building the ui
    def __init__(self, **kwargs):
        # The model is set when the manipulator is created in viewport_scene
        super().__init__(**kwargs)

        self._user = ""
        self._password = ""
        self._window = ui.Window("Database UI", width=300, height=200)

        self.build_ui()

    # Method is called when the manipulator is contructed or invalidated by the model.
    # Updates the UI based on information from the manipulator.
    def on_build(self):
        if not self.model:
            return

        if self.model.get_item("name") == "":
            return

        if self.model.get_value(self.model.get_item("connected")):
            query = "SELECT meta FROM omnitest WHERE pth=" + "\"" + self.model.get_item('name') + "\""
            res = self.query(query)
            self.model.set_value(self.model.get_item("result"), res)

        self.build_ui()

    # Method is called when a value in the model is changed and _item_changed is called.
    # Invalidates and rebuilds the manipulator based on the changes to the model.
    def on_model_updated(self, item):
        self.invalidate()

    # Attempt to connect to the sql database with user provided username and password.
    def connect(self, user, password):
        try:
            cnx = pymysql.connect(user=user, password=password, host='127.0.0.1', port=3306, database='sakila')
            # Update the model if the connection is successful
            self.model.set_value(self.model.get_item("cnx"), cnx)
            self.model.set_value(self.model.get_item("connected"), True)
        except:
            # Alert the user if the connection fails
            carb.log_warn("Failed to connect to database")
            return False

    # Attempt to perform a query on the database using the connection information stored in the model.
    def query(self, query=False):
        try:
            cnx = self.model.get_value(self.model.get_item("cnx"))
            with cnx:
                # Create a cursor on the database
                with cnx.cursor() as cursor:
                    # Execute the query and retrieve the result
                    cursor.execute(query)
                    result = cursor.fetchone()
                    return result
        except:
            carb.log_warn("Connection error")

    # UI element functions
    def on_changed(self, item, value):
        if item == 'user':
            self._user = value
        if item == 'pass':
            self._password = value

    # When the connection button is pressed, attempt to establish a database connection and reload the UI
    def on_pressed(self):
        self.connect(self._user, self._password)
        self.build_ui()

    # Build UI elements based on data stored in model
    def build_ui(self):
        with self._window.frame:
            # If a user is not connected to the database, accept login information and attempt to connect
            if not self.model.get_value(self.model.get_item("connected")):
                # Build the UI and add functions to the user input elements
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
            # Else display results of query on database if an object is selected in the scene
            else:
                result = self.model.get_value(self.model.get_item("result"))
                if len(result) > 0:
                    ui.Label(f"Result: {result[0]}", style=lab_style)
                else:
                    ui.Label("Select an object to see database information", style=lab_style)
