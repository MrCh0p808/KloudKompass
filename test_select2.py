from kloudkompass.dashboard.widgets.settings_modal import REGION_OPTIONS, SettingsModal
from textual.app import App
class TestApp(App):
    async def on_mount(self):
        modal = SettingsModal()
        await self.push_screen(modal)
        select = modal.query_one('#select_region')
        print('REGION_OPTIONS length:', len(REGION_OPTIONS))
        print('Select widget options length:', len(select._options))
        self.exit()
if __name__ == '__main__':
    TestApp().run()
