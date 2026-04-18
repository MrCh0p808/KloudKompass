from textual.app import App
from kloudkompass.dashboard.widgets.settings_modal import SettingsModal

class TestApp(App):
    def on_mount(self):
        self.push_screen(SettingsModal())

if __name__ == '__main__':
    app = TestApp()
    print('Testing...')
