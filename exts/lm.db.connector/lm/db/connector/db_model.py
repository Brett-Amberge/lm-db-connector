from omni.ui import scene as sc


"""
    Stores user information and query data
"""


class DBModel():

    # Abstract classes to store model data
    class StringItem(sc.AbstractManipulatorItem):
        def __init__(self, value=""):
            self.value = value

    class ListItem(sc.AbstractManipulatorItem):
        def __init__(self, value=[]):
            self.value = value

    def __init__(self):
        self._user = DBModel.StringItem()
        self._pass = DBModel.StringItem()
        self._result = DBModel.ListItem()

    # Accessor methods
    def get_user(self):
        return self._user

    def get_pass(self):
        return self._pass

    def get_result(self):
        return self._result

    def get_value(self, item):
        if item == self._user:
            return self._user.value
        if item == self._pass:
            return self._pass.value
        if item == self._result:
            return self._result.value
        return False

    # Update methods
    def set_value(self, item, changed):
        if item == self._user:
            self._user.value = changed
        if item == self._pass:
            self._pass.value = changed
        if item == self._result:
            self._result.value = changed
        return self.get_value(item)
