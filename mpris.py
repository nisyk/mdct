import dbus
import logging
import asyncio
import urllib.request
from urllib.parse import urlparse
from io import BytesIO
from PIL import Image

class MprisClient:
    def __init__(self):
        self.bus = dbus.SessionBus()
        self.active_player = None
        self._art_cache = {}


    # Fetch Media Player session
    def _get_player(self):

        if self.active_player is not None:
            return self.active_player
        try:

            for name in self.bus.list_names():
                if name.startswith('org.mpris.MediaPlayer2.'):
                    self.active_player = self.bus.get_object(name, '/org/mpris/MediaPlayer2')
                    return self.active_player
        except dbus.exceptions.DBusException:
            self._reset_player()

        self.active_player = None
        return None

    # Clear the Cache (avoid iterations)
    def _reset_player(self):
        self.active_player = None

    # Command Control
    async def receive_command(self, command):
        await asyncio.to_thread(self._receive_command_sync, command)

    def _receive_command_sync(self, command):
        try:
            player_obj = self._get_player()
            if player_obj:
                player_ctrl = dbus.Interface(player_obj, 'org.mpris.MediaPlayer2.Player')
                if command == 'n':
                    player_ctrl.Next()
                elif command == 'b':
                    player_ctrl.Previous()
                elif command == 'p':
                    player_ctrl.PlayPause()
        except dbus.exceptions.DBusException:
            self._reset_player()
        except Exception as e:
            logging.error(f"Error command: {e}")

    # Seek Control
    async def seek_relative(self, offset_seconds):
        offset_microseconds = int(offset_seconds * 1000000)
        await asyncio.to_thread(self._seek_relative_sync, offset_microseconds)

    def _seek_relative_sync(self, offset_microseconds):
        try:
            player_obj = self._get_player()
            if player_obj:
                seek_ctrl = dbus.Interface(player_obj, 'org.mpris.MediaPlayer2.Player')
                seek_ctrl.Seek(offset_microseconds)

        except dbus.exceptions.DBusException:
                self._reset_player()
        except Exception as e:
                logging.error(f"Error: {e}")

    # Format Time
    @staticmethod
    def _format_time(microseconds):
        if not microseconds:
            return "00:00"
        total_seconds = microseconds // 1000000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return "{:02}:{:02}".format(minutes, seconds)

    async def get_current_info(self):
        return await asyncio.to_thread(self._get_current_info_sync)

    # Fetch Album Art

    @staticmethod
    def _parse_art_url(metadata):
        art_url_raw = metadata.get('mpris:artUrl', '')

        art_url_str = str(art_url_raw)
        if art_url_str.startswith('http') or art_url_str.startswith('file'):
            return art_url_str

        return None

    async def get_album_art(self, url):

        if not url:
            return None
        if url in self._art_cache:
            return self._art_cache[url]

        try:
            pil_image = await asyncio.to_thread(self._fetch_image_sync, url)
            if pil_image:
                if len(self._art_cache) >= 24:
                    self._art_cache.clear()
            return pil_image
        except Exception as e:
            logging.error(f"Error fetching album: {e}")
            return None

    @staticmethod
    def _fetch_image_sync(url):
        try:
            if url.startswith('file'):
                local_path = urllib.request.url2pathname(urlparse(url).path)
                with open(local_path, 'rb') as f:
                    return Image.open(BytesIO(f.read()))

            else:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    return Image.open(BytesIO(response.read()))
        except Exception as e:
            logging.error(f"Error requesting image: {e} | {url}")

    # Fetch metadata
    def _get_current_info_sync(self):
        try:
            player_obj = self._get_player()

            if player_obj:
                player_props = dbus.Interface(player_obj, 'org.freedesktop.DBus.Properties')
                metadata = player_props.Get("org.mpris.MediaPlayer2.Player", "Metadata")
                play_status = player_props.Get("org.mpris.MediaPlayer2.Player", "PlaybackStatus")
                player_id = player_props.Get("org.mpris.MediaPlayer2", "Identity")

                artist_raw = metadata.get('xesam:artist', [])
                if isinstance(artist_raw, (list, dbus.Array)) and len(artist_raw) > 0:
                    artist = str(artist_raw[0])
                elif isinstance(artist_raw, str):
                    artist = artist_raw
                else:
                    artist = "Unknown Artist"

                try:
                    position_raw = player_props.Get("org.mpris.MediaPlayer2.Player", "Position")
                except dbus.exceptions.DBusException:
                    position_raw = 0

                title = str(metadata.get('xesam:title', 'Unknown Title'))
                status = str(play_status)
                length_raw = metadata.get('mpris:length', 0)
                art_url = self._parse_art_url(metadata)


                return {"title": title,
                        "artist": artist,
                        "status": status,
                        "position_str": self._format_time(position_raw),
                        "length_str": self._format_time(length_raw),
                        "position_sec": int(position_raw) // 1000000 if position_raw else 0,
                        "length_sec": int(length_raw) // 1000000 if length_raw else 0,
                        "art_url": art_url,
                        "player_id": player_id,
                        }

            else:
                return self._get_default_info()

        except dbus.exceptions.DBusException:
            self._reset_player()
            return self._get_default_info()


    # Default Info
    @staticmethod
    def _get_default_info():
        return {
                    "title": "Unknown Title",
                    "artist": "Unknown Artist",
                    "status": "Offline",
                    "position_str": "00:00",
                    "length_str": "00:00",
                    "position_sec": 0,
                    "length_sec": 0,
                    "art_url": None,
                    "player_id": None
                    }
