import dbus
import asyncio

class MprisClient:
    def __init__(self):
        self.bus = dbus.SessionBus()
        self.active_player = None


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
            print(f"Error command: {e}")

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
                print(f"Error: {e}")

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


    # Fetch metadata
    def _get_current_info_sync(self):
        try:
            player_obj = self._get_player()

            if player_obj:
                player_props = dbus.Interface(player_obj, 'org.freedesktop.DBus.Properties')
                metadata = player_props.Get("org.mpris.MediaPlayer2.Player", "Metadata")
                play_status = player_props.Get("org.mpris.MediaPlayer2.Player", "PlaybackStatus")

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


                return {"title": title,
                        "artist": artist,
                        "status": status,
                        "position_str": self._format_time(position_raw),
                        "length_str": self._format_time(length_raw),
                        "position_sec": int(position_raw) // 1000000 if position_raw else 0,
                        "length_sec": int(length_raw) // 1000000 if length_raw else 0
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
                    "length_sec": 0
                    }
