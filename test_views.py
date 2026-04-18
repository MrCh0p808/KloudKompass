import asyncio
from textual.app import App
from kloudkompass.dashboard.app import VIEW_REGISTRY

class TestApp(App):
    async def on_mount(self):
        for name, cls in VIEW_REGISTRY.items():
            print(f'Testing {name}...')
            try:
                view = cls()
                await self.mount(view)
                await view.remove()
                print(f'{name} OK')
            except Exception as e:
                print(f'{name} FAILED: {e}')
        self.exit()

if __name__ == '__main__':
    TestApp().run()
