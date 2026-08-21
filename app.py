import argparse
import asyncio
from textual.app import App, ComposeResult
from textual.widgets import Button, ProgressBar, Label, Footer, Select
from textual.containers import Horizontal, Vertical, Container
from textual import on

from textual_image.widget import Image

from mpris import MprisClient

__version__ = "0.1.1"

class MDCT(App):

    BINDINGS = [
        ("space", "bind_play_pause", "Play/Pause"),
        ("n", "bind_next", "Next"),
        ("b", "bind_prev", "Previous"),
        ("l", "bind_seek_plus", "Seek+"),
        ("h", "bind_seek_min", "Seek-"),
        ("q", "quit", "Quit"),
    ]

    CSS = """

    Screen {
        &:inline {
            border: none;
            height: 14;
        }
    }

    #main_panel {
        align: center middle;
        width: 100%;
    }
    
    #track-info, #artist-info {
        width: 100%;
        height: auto;
        text-align: center;
    }


    #track-info {
        margin-top: 1;
        color: $primary;
        text-style: bold;
    }
    
    #select-player-wrapper {
        width: 100%;
        height: auto;
        align: center middle;
        padding-bottom: 1;
            &:inline {
                padding-bottom: 0;
            }
    }
    
    #select-player {
        max-width: 31;
    }
    
    #select-player SelectCurrent {
        padding: 0 1;
    }
        
    #select-player SelectOverlay .option-list--option {
        padding: 0 2;
    }

    #select-player SelectOverlay .option-list--option-highlighted {
        background: $secondary;
    }
    



    #artist-info {
        margin-bottom: 1;
    }

    #art-container {
        width: 100%;
        height: auto;
        align: center middle;
        margin-bottom: 1;
    }


    #album_art {
        width: 31;
        height: auto;

    }


    #media-control {
        width: 100%;
        height: auto;
        align: center middle;
        margin: 1 2;
    }
    #media-control Button {
        width: auto;
        min-width: 6;
        margin-left: 1;
        margin-right: 1;

    }

    #media-control #btn-play {
        width: auto;
        min-width: 10;

    }

    #progress Bar > .bar--bar {
        color: $success;
        background: $success 30%;
    }
    #progress {
        width: 100%;
        height: auto;
        align: center middle;
    }

    #track-progress {
        opacity: 50%
    }
    


    """


    # Initialize Widgets
    def __init__(self, fullscreen: bool = False):
        super().__init__()
        self.client = MprisClient()
        self.is_fullscreen = fullscreen
        self.player_selector = Select([], id='select-player', allow_blank=True, prompt="Media Source", compact=True)
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
            with Container(id='select-player-wrapper'):
                yield self.player_selector
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
        await self._refresh_player_list()
        self.set_interval(1, self.update_ui)
        self.set_interval(5, self._refresh_player_list)

    # Give the UI info from mpris.py backend
    async def update_ui(self):
        info = await self.client.get_current_info()

        if info['status'] == "Offline":

            self.song_info.update("There's no currently running...")
            self.artist_info.update(" ")
            self.progressbar.update(total=100, progress=0)
            self.btn_play.label = "▶"
            self.player_selector.disabled = True
            if self.is_fullscreen:
                self.album_art.image = None
                self.last_art_url = None
        else:

            self.song_info.update(f"{info['title']}")
            self.artist_info.update(f"{info['artist']}")

            self.player_selector.disabled = False

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

    async def _refresh_player_list(self):
        players = await asyncio.to_thread(self.client.get_available_players)
        if players:
            self.player_selector.set_options(players)
            self.player_selector.disabled = False
            if self.client.active_player_name:
                self.player_selector.value = self.client.active_player_name
        else:
            self.player_selector.clear()
            self.player_selector.disabled = True

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

    @on(Select.Changed, "#select-player")
    async def on_player_changed(self, event: Select.Changed):
        if event.value is None or event.value is Select.NULL:
            return
        await asyncio.to_thread(self.client.set_active_player, event.value)
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

    async def action_bind_seek_min(self) -> None:
        await self.client.seek_relative(-10)
        await self.update_ui()

    async def action_bind_seek_plus(self) -> None:
        await self.client.seek_relative(10)
        await self.update_ui()

    async def action_quit(self) -> None:
        self.exit()




if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="mdct", description='TUI Media Control')
    parser.add_argument("-f", "--full", action="store_true", help="show full screen")
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")

    args = parser.parse_args()


    app = MDCT(fullscreen=args.full)
    app.run(inline=not args.full)
