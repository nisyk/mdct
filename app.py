import argparse
import asyncio
from rich.text import Text

from textual.app import App, ComposeResult
from textual.widgets import Button, ProgressBar, Label, Footer, Select
from textual.reactive import reactive
from textual.widget import Widget
from textual.containers import Horizontal, Vertical
from textual.events import MouseScrollDown, MouseScrollUp
from textual import on

from textual_image.widget import Image

from mpris import MprisClient

__version__ = "0.2.0"

class VolumeWidget(Widget):

    """Volume Display Widget:
        Change the volume between 0 and 100% with MouseScroll"""


    DEFAULT_CSS = """
    VolumeWidget {
        height: 1;
        width: auto;
        min-width: 8;
        padding: 0 1;
        color: $text-muted;
    }
    VolumeWidget:hover {
        color: $text;
    }
    """

    volume: reactive[int] = reactive(0)

    def render(self) -> Text:
        if self.volume == 0:
            return Text(f"🔇 {self.volume:>3}%")
        return Text(f"🔊 {self.volume:>3}%")

    async def on_mouse_scroll_up(self, event: MouseScrollUp) -> None:
        event.stop()
        await self.app.volume_change(+5)

    async def on_mouse_scroll_down(self, event: MouseScrollDown) -> None:
        event.stop()
        await self.app.volume_change(-5)


class MDCT(App):

    # Frontend App for MDCT

    BINDINGS = [
        ("space", "bind_play_pause", "Play/Pause"),
        ("n", "bind_next", "Next"),
        ("b", "bind_prev", "Previous"),
        ("l", "bind_seek_plus", "Seek+"),
        ("h", "bind_seek_min", "Seek-"),
        ("m", "bind_mute", "Mute"),
        ("q", "quit", "Quit"),
    ]

    CSS = """

    Screen {
        align: center middle;
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
        max-width: 22;
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


    #volume-display {
        width: auto;
        height: 1;
        padding: 0 1;
        margin-left: 1;
        color: $text-muted;
    }
    
    #volume-display:hover {
        color: $text;
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
    

    /* ---- wide layout ---- */
    #wide-root {
        width: 100%;
        height: 100%;
        overflow: hidden;
        align: center middle;
    }

    #wide-left,
    #wide-right {
        max-width: 54;               /* real width → inner centering rules work */
        height: 100%;
        align: center middle;     /* vertical centering of the stack */
        overflow: hidden;
    }

    #wide-left #album_art {
        width: 31;
        height: auto;
        max-height: 100%;
    }

    """


    # Initialize Widgets and Condition
    def __init__(self, fullscreen: bool = False, wide: bool = False):
        super().__init__()
        self.client = MprisClient()
        self.is_fullscreen = fullscreen
        self.is_wide = wide
        self.player_selector = Select([], id='select-player', allow_blank=True, prompt="Media Source", compact=True)
        self.song_info = Label("Loading...", id='track-info')
        self.artist_info = Label(" ", id='artist-info')
        self.volume_display = VolumeWidget(id="volume-display")
        self.track_progress = Label("00:00 / 00:00", id='track-progress')
        self.progressbar = ProgressBar(total=100, show_percentage=False, show_eta=False)
        self.btn_prev = Button("|<", id="btn-prev")
        self.btn_play = Button("⏯", id="btn-play", variant="primary")
        self.btn_next = Button(">|", id="btn-next")
        self.btn_seek_prev = Button("<<", id="btn-seek-prev")
        self.btn_seek_next = Button(">>", id="btn-seek-next")

        if self.is_fullscreen or self.is_wide:
            self.album_art = Image(id='album_art')
            self.last_art_url = None

    # Player Header: Compose Player Selector and Volume
    def _player_header(self):
        with Horizontal(id='select-player-wrapper'):
            yield self.player_selector
            yield self.volume_display

    # Playback Panel: Compose Playback Controls
    def _playback_panel(self):
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

    # Compose all widgets in both default, full, and wide version
    def compose(self) -> ComposeResult:

        if not self.is_wide:
            with Vertical(id='main_panel'):
                yield from self._player_header()
                if self.is_fullscreen:
                    with Horizontal(id='art-container'):
                        yield self.album_art
                    yield Footer()
                yield from self._playback_panel()
        else:
            with Horizontal(id='wide-root'):
                with Vertical(id='wide-left'):
                    yield from self._player_header()
                    with Horizontal(id='art-container'):
                        yield self.album_art
                with Vertical(id='wide-right'):
                    yield from self._playback_panel()
            yield Footer()




    async def on_mount(self):

        if self.is_wide:
            self.screen.add_class("wide")

        await self.update_ui()
        await self._refresh_player_list()
        self.set_interval(1, self.update_ui) # Update UI/sec
        self.set_interval(5, self._refresh_player_list) # Update Player List/5 secs



    async def update_ui(self):
        info = await self.client.get_current_info()

        # Offline condition
        if info['status'] == "Offline":

            self.song_info.update("There's no currently running...")
            self.volume_display.volume = 0
            self.artist_info.update(" ")
            self.progressbar.update(total=100, progress=0)
            self.btn_play.label = "▶"
            self.player_selector.disabled = True

            if self.is_fullscreen or self.is_wide:
                self.album_art.image = None
                self.last_art_url = None

        # Online condition
        else:

            self.song_info.update(f"{info['title']}")
            self.artist_info.update(f"{info['artist']}")

            self.player_selector.disabled = False
            self.volume_display.volume = info['volume']

            if self.is_fullscreen or self.is_wide:
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
        # Online Condition
        if players:
            self.player_selector.set_options(players)
            self.player_selector.disabled = False
            if self.client.active_player_name:
                self.player_selector.value = self.client.active_player_name
        # Offline condition
        else:
            self.player_selector.clear()
            self.player_selector.disabled = True



    # Events Handler

    @on(Select.Changed, "#select-player")
    async def on_player_changed(self, event: Select.Changed):
        if event.value is None or event.value is Select.NULL:
            return
        await asyncio.to_thread(self.client.set_active_player, event.value)
        await self.update_ui()

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



    async def volume_change(self, delta: int):
        info = await self.client.get_current_info()
        new_vol = max(0, min(100, info["volume"] + delta))
        await self.client.set_volume(new_vol)
        self.volume_display.volume = new_vol  # reactive auto-render

    async def action_bind_prev(self) -> None:
        await self.client.receive_command('b')
        await self.update_ui()

    async def action_bind_mute(self) -> None:
        await self.client.toggle_mute()
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
    parser = argparse.ArgumentParser(prog="mdct", description=f"TUI Media Control {__version__}")
    parser.add_argument("-f", "--full", action="store_true", help="show full screen")
    parser.add_argument("-w", "--wide", action="store_true", help="side by side interface")
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")

    args = parser.parse_args()


    app = MDCT(fullscreen=args.full, wide=args.wide)
    app.run(inline=not (args.full or args.wide))
