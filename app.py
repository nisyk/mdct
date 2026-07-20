import argparse
from textual.app import App, ComposeResult
from textual.widgets import Button, ProgressBar, Label, Footer
from textual.containers import Horizontal, Vertical
from textual_image.widget import Image
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


    # Initialize Widgets
    def __init__(self, fullscreen: bool = False):
        super().__init__()
        self.client = MprisClient()
        self.theme = 'gruvbox'
        self.is_fullscreen = fullscreen

        self.song_info = Label("Loading...", id='track-info')
        self.artist_info = Label(" ", id='artist-info')
        self.track_progress = Label("00:00 / 00:00", id='track-progress')
        self.progressbar = ProgressBar(total=100, show_percentage=False, show_eta=False)
        self.btn_prev = Button("|<", id="btn-prev")
        self.btn_play = Button("⏯", id="btn-play", variant="primary")
        self.btn_next = Button(">|", id="btn-next")
        self.btn_seek_prev = Button("<<", id="btn-seek-prev")
        self.btn_seek_next = Button(">>", id="btn-seek-next")

        if self.is_fullscreen:
            self.album_art = Image(id='album_art')
            self.last_art_url = None




    # Compose All Widgets
    def compose(self) -> ComposeResult:
        with Vertical(id='main_panel'):
            if self.is_fullscreen:
                with Horizontal(id='art-container'):
                    yield self.album_art
                yield Footer()

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


    # Update the UI for 1 Hz
    async def on_mount(self):
        await self.update_ui()

        self.set_interval(1, self.update_ui)

    # Give the UI info from mpris.py backend
    async def update_ui(self):
        info = await self.client.get_current_info()

        if info['status'] == "Offline":
            self.song_info.update("There's no currently running...")
            self.artist_info.update(" ")
            self.progressbar.update(total=100, progress=0)
            self.btn_play.label = "▶"
            if self.is_fullscreen:
                self.album_art.image = None
                self.last_art_url = None
        else:
            self.song_info.update(f"{info['title']}")
            self.artist_info.update(f"{info['artist']}")

            if self.is_fullscreen:
                art_url = info.get('art_url')

                if art_url and art_url != self.last_art_url:
                    pil_image = await self.client.get_album_art(art_url)

                    if pil_image:
                        self.album_art.image = pil_image
                        self.last_art_url = art_url
                    else:
                        self.album_art.image = None
                        self.last_art_url = None
                elif not art_url:
                    self.album_art.image = None
                    self.last_art_url = None

        if info['length_sec'] > 0:
            self.progressbar.update(total=info['length_sec'], progress=info['position_sec'])
            self.track_progress.update(f"{info['position_str']} / {info['length_str']}")
        else:
            self.progressbar.update(total=100, progress=0)
        if info['status'] == "Playing":
            self.btn_play.label = "||"
        else:
            self.btn_play.label = "▶"

    # Events Handler
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
    parser = argparse.ArgumentParser(description='TUI Media Control')
    parser.add_argument("-f", "--full", action="store_true", help="show full screen")
    args = parser.parse_args()

    app = MprisApp(fullscreen=args.full)
    app.run(inline=not args.full)

