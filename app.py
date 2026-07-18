from textual.app import App, ComposeResult
from textual.widgets import Button, ProgressBar, Label
from textual.containers import Horizontal, Vertical
from textual import on

from mpris import MprisClient

class MprisApp(App):

    BINDINGS = [
        ("space", "bind_play_pause", "Play/Pause"),
        ("n", "bind_next", "Next"),
        ("b", "bind_prev", "Previous"),
        ("q", "quit", "Quit"),
    ]

    CSS_PATH = 'style.tcss'



    def __init__(self):
        super().__init__()
        self.client = MprisClient()
        self.theme = 'gruvbox'

        self.song_info = Label("Loading...", id='track-info')
        self.artist_info = Label(" ", id='artist-info')
        self.track_progress = Label("00:00 / 00:00", id='track-progress')
        self.progressbar = ProgressBar(total=100, show_percentage=False, show_eta=False)
        self.btn_prev = Button("|<", id="btn-prev")
        self.btn_play = Button("⏯", id="btn-play", variant="primary")
        self.btn_next = Button(">|", id="btn-next")
        self.btn_seek_prev = Button("<<", id="btn-seek-prev")
        self.btn_seek_next = Button(">>", id="btn-seek-next")





    def compose(self) -> ComposeResult:
        with Vertical(id='main_panel'):
            yield self.song_info
            yield self.artist_info
            with Vertical(id='progress'):
                yield self.progressbar
                yield self.track_progress
            with Horizontal(id='media-control'):
                yield self.btn_prev
                yield self.btn_seek_prev
                yield self.btn_play
                yield self.btn_seek_next
                yield self.btn_next



    async def on_mount(self):
        await self.update_ui()

        self.set_interval(1, self.update_ui)

    async def update_ui(self):
        info = await self.client.get_current_info()

        if info['status'] == "Offline":
            self.song_info.update("There's no currently running...")
            self.artist_info.update(" ")
            self.progressbar.update(total=100, progress=0)
            self.btn_play.label = "▶"
        else:
            self.song_info.update(f"{info['title']}")
            self.artist_info.update(f"{info['artist']}")

        if info['length_sec'] > 0:
            self.progressbar.update(total=info['length_sec'], progress=info['position_sec'])
            self.track_progress.update(f"{info['position_str']} / {info['length_str']}")
        else:
            self.progressbar.update(total=100, progress=0)
        if info['status'] == "Playing":
            self.btn_play.label = "||"
        else:
            self.btn_play.label = "▶"

    @on(Button.Pressed, "#btn-prev")
    async def btn_prev(self):
        await self.client.receive_command('b')
        await self.update_ui()

    @on(Button.Pressed, "#btn-play")
    async def btn_play(self):
        await self.client.receive_command('p')
        await self.update_ui()

    @on(Button.Pressed, "#btn-next")
    async def btn_next(self):
        await self.client.receive_command('n')
        await self.update_ui()

    @on(Button.Pressed, "#btn-seek-prev")
    async def btn_seek_prev(self):
        await self.client.seek_relative(-10)
        await self.update_ui()

    @on(Button.Pressed, "#btn-seek-next")
    async def btn_seek_next(self):
        await self.client.seek_relative(10)
        await self.update_ui()

    async def action_bind_prev(self) -> None:
        await self.client.receive_command('b')
        await self.update_ui()

    async def action_bind_play_pause(self) -> None:
        await self.client.receive_command('p')
        await self.update_ui()

    async def action_bind_next(self) -> None:
        await self.client.receive_command('n')
        await self.update_ui()

    async def action_quit(self) -> None:
        self.exit()




if __name__ == "__main__":
    app = MprisApp()
    app.run(inline=True)
