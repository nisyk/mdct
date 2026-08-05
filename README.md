# mediacontrol-tui
A Textual-based Media Control with integration of MPRIS.

![Demo](assets/screenshot1.png)

![Demo Full Screen](assets/screenshot2.png)

## Overview 
This project is based from Python with Textual TUI API to synchronize song metadatas from music player (such as: YouTube Music, Spotify, VLC, etc.) with integration of MPRIS dbus in Linux.

## Features
- Real-time sync: Sync metadatas such as artist, song title, album art, progress bar.
- Album art: Gives rendered album art with PIL and TGP/Sixel protocols. (needs Terminal which supported one of both protocols, like Kitty, Konsole).
- Lightweight: Use fewer resources than Electron UI.
- Interactive buttons: Play, seek, skip, and prev buttons to gave command to music player.
