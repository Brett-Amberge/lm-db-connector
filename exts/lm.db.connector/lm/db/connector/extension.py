"""
    Main extension file for connecting to mysql database
"""

import omni.ext
import omni.ui as ui
import carb

from .db_model import DBModel
from .styles import lab_style, rect_style, btn_style, db_style

# Try to import the mysql library
try:
    import pymysql
except ImportError:
    carb.log_warn("[lm.db.connector] PyMysql not found, attempting to install")
    omni.kit.pipapi.install("pymysql")
    import pymysql


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class Connector(omni.ext.IExt):

    # Constructor
    def __init__(self):
        self._model = DBModel()
        self._window = None
        self.label_style = lab_style

    # Attempt to connect to the sql database with user provided username and password
    def connect(self, user, password):
        try:
            cnx = pymysql.connect(user=user, password=password, host='127.0.0.1', port=3306, database='sakila')
            with cnx:
                with cnx.cursor() as cursor:
                    sql = "SELECT * FROM actor"
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    return result
        except:
            # Alert the user if the connection fails
            carb.log_warn("Failed to connect to database")
            return False

    # Update the model when the text field is changed
    def on_changed(self, item, value):
        self._model.set_value(item, value)

    # Populate the UI with any information retrieved from the database
    def on_pressed(self):
        self._model.set_value(self._model.get_result(), self.connect(self._model.get_value(self._model.get_user()),
                              self._model.get_value(self._model.get_pass())))
        self.build_ui(self._model.get_result())

    # Build the window's UI based on information from the model
    def build_ui(self, result):
        with self._window.frame:
            with ui.VStack():
                with ui.HStack(height=0):
                    with ui.VStack():
                        ui.Label("Username:", style=lab_style)
                        uField = ui.StringField()
                        uField.model.add_end_edit_fn(lambda m, value=self._model.get_user():
                                                     self.on_changed(value, m.get_value_as_string()))

                    with ui.VStack():
                        ui.Label("Password:", style=lab_style)
                        pField = ui.StringField(password_mode=True)
                        pField.model.add_end_edit_fn(lambda m, value=self._model.get_pass():
                                                     self.on_changed(value, m.get_value_as_string()))

                result = self._model.get_value(self._model.get_result())
                if len(result) > 0:
                    with ui.ScrollingFrame(horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                                           vectrical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED):
                        with ui.VGrid():
                            for entry in result:
                                with ui.HStack():
                                    for i in range(len(entry)):
                                        with ui.ZStack():
                                            ui.Rectangle(style=rect_style)
                                            ui.Label(str(entry[i]), style=db_style)
                else:
                    ui.Button(text="Connect to a database", clicked_fn=lambda: self.on_pressed(),
                              style=btn_style)

    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):

        print("[lm.db.connector] MyExtension startup")
        self._window = ui.Window("Database Info", width=500, height=300)

        self.build_ui(self._model.get_result())

    def on_shutdown(self):
        print("[lm.db.connector] MyExtension shutdown")
