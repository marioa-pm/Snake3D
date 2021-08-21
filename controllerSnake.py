import glfw
import sys

class Controller:

    def __init__(self):
        self.camera = 1
        self.model = None

    def set_model(self, model):
        self.model = model

    def on_key(self, window, key, scancode, action, mods):

        if action != glfw.PRESS:
            return

        elif key == glfw.KEY_ESCAPE:
            sys.exit()

        elif self.model.state:

            if key == glfw.KEY_E:
                self.camera = 2

            elif key == glfw.KEY_R:
                self.camera = 1

            elif key == glfw.KEY_T:
                self.camera = 3
