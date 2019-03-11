from pywinauto.application import Application


class GuiControl:
    def __init__(self):
        self.visualizer = None
        self.visualizer_dlg = None

        self.recorder = None
        self.recorder_dlg = None

    def set_windows_record(self):
        self.visualizer = Application().start(r"C:\Program Files\Leap Motion\Core Services\Visualizer.exe")
        self.visualizer_dlg = self.visualizer.window()
        self.recorder = Application().connect(class_name="wxWindowNR")
        self.recorder_dlg = self.recorder.window()
        visualizer_dlg = self.visualizer_dlg
        recorder_dlg = self.recorder_dlg

        # toggle off the help menu
        visualizer_dlg.set_keyboard_focus().send_keystrokes("h")

        # get maximum screen size
        visualizer_dlg.maximize()
        max_size = visualizer_dlg.rectangle()
        visualizer_dlg.restore()

        size = GuiControl.position_record(max_size, main=True)
        visualizer_dlg.move_window(x=-size['x'], y=size['y'], width=size['width'], height=size['height'], repaint=True)
        # visualizer_dlg.set_transparency(alpha=120)

        size = GuiControl.position_record(max_size, main=False)
        recorder_dlg.set_focus()
        recorder_dlg.move_window(x=-size['x'], y=size['y'], width=size['width'], height=size['height'], repaint=True)

    def end_record(self):
        self.visualizer.kill()
        self.recorder_dlg.restore()
        self.recorder_dlg.maximize()

    @staticmethod
    def position_record(max_size, main):
        max_width = max_size.right - max_size.left - 20
        max_height = max_size.bottom - max_size.top - 20
        if main:
            return {'x': -int(max_width / 3),
                    'y': 0,
                    'width': int(max_width / 3 * 2),
                    'height': int(max_height)}
        return {'x': 0,
                'y': 0,
                'width': int(max_width / 3),
                'height': int(max_height)}
