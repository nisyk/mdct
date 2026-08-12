# mdct
A Textual-TUI-based Media Control with integration of MPRIS. Used in Terminal such as Kitty, KDE Konsole.

![Demo](assets/screenshot1.png)

![Demo Full Screen](assets/screenshot2.png)

## Overview 
mdct is based from Python with Textual TUI API to synchronize song metadatas from music player (such as: YouTube Music, Spotify, VLC, etc.) with integration of MPRIS dbus in Linux.

## Features
- Run on Terminal: Can run on anywhere, as long it has terminal (e.g. Visual Studio Code, PyCharm, Zed, etc.)
- Real-time sync: Sync metadatas such as artist, song title, album art, progress bar.
- Album art: Gives rendered album art with PIL and KGP/Sixel protocols. (needs Terminal which supported one of both protocols, like Kitty, Konsole).
- Lightweight: Use fewer resources than Electron UI.
- Interactive buttons: Play, seek, skip, and previous buttons to gave command to music player.

## Requirements
- A mainstream Linux distro (A distro with Cinnamon, GNOME, KDE, XFCE, Hyprland, Niri probably should work)
	e.g: Ubuntu, Linux Mint, Debian, Fedora, Bazzite, CachyOS, etc.
- Python 3.10 or later with python3-dbus.
- Terminal with mouse click support.
- Terminal with KGP/Sixel protocol if want `--full` interface with album art.

## Installation

Run this command:

```bash
chmod +x install.sh
./install.sh
```

After the installation completed, run this command:

```bash
mdct -v
```

## Usage

Run this command:

```bash
mdct
```


If you want with album art image content, run this command:

```bash
mdct -f
```
```bash
mdct --full
```

> Note: You need terminal with KGP (Kitty Graphics Protocol)/Sixel protocol support to make album art visible, TGP protocol is reccomended (kitty, Konsole). For more information, please check: https://github.com/lnqs/textual-image (in this repo, KGP mentioned as TGP).

## Keybindings

| Key     | Function          |
| ------- | ----------------- |
| SPACE   | Play/pause toggle |
| n       | Next song         |
| b       | Previous song     |
| h       | Seek prev 10 secs |
| l       | Seek next 10 secs |
| q       | Quit application  |
| SHIFT+p | Textual menu      |


---
Made with curious by 🌆 **NISY**
