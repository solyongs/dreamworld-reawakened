# Pokemon Dream World - Reawakened

## Tutorial

### Windows

For the Game Sync server (for connecting your DS to the Dream World server, must be done first):
- Install the newest version of Python
- Download the latest release from this link here
- Extract the folder into any directory
- Navigate into the extracted `dreamworld-reawakened/game_sync_server` folder
- Hold down shift and right-click in the folder (the empty space, not on a file/folder) and select "open PowerShell window here"
- In the PowerShell window, run the command `pip install -r requirements.txt`
- Run `python server.py` to start the server
- The server will give you a DNS, which you can change from the "Nintendo WFC Settings" menu located on the save file select screen of the Gen5 game.
- Connect to the Game Sync in-game and tuck in a Pokémon.

For the Dream World server (the Pokémon Global Link site):
- Navigate into the `dreamworld-reawakened` folder
- Open a new PowerShell window here
- In the PowerShell window, run the command `pip install -r requirements.txt`
- Run `python main.py` to start the server

### Linux
- Same as above, but the Game Sync server must be run as root, as one of the ports used (53) is privileged and cannot be opened by a non-root user.

## Flash browser setup

**Ruffle will not work.**
Ruffle currently cannot emulate the Dream World correctly.

### Windows

- Install [Basilisk](https://www.basilisk-browser.org/), a browser which still supports NPAPI based plugins.

- Download and install the archived version of [Flash Player 32.0.0.371](https://web.archive.org/web/20200609220527/https://fpdownload.macromedia.com/pub/flashplayer/installers/archive/fp_32.0.0.371_archive.zip) for Windows.

- Navigate to http://127.0.0.1:8080/ in Basilisk.

### Linux

- Install and extract [Basilisk](https://www.basilisk-browser.org/), a browser which still supports NPAPI based plugins.

- Download the archived version of [Flash Player 32.0.0.371](https://web.archive.org/web/20200530062840if_/https://fpdownload.adobe.com/get/flashplayer/pdc/32.0.0.371/flash_player_npapi_linux.x86_64.tar.gz) for Linux.

- Place `libflashplayer.so` into `/usr/lib64/mozilla/plugins`. You may have to create this directory.

- Place the contents of the `usr` folder into `/usr/`.

- Run Basilisk with proper environment variable like so: `MOZ_PLUGIN_PATH=/usr/lib64/mozilla/plugins ./basilisk`

- Navigate to http://127.0.0.1:8080/ in Basilisk.

## Standalone startup
- Load http://127.0.0.1:8080/DreamWorld_data/src/swf/theme/assets/common/main.swf with the standalone Adobe Flash Player (download: [Windows](https://archive.org/download/standaloneflashplayers/fp/fp_32/32.0.0.465/flashplayer32_0r0_465_win_sa.exe), [Mac](https://archive.org/download/standaloneflashplayers/fp/fp_32/32.0.0.465/flashplayer32_0r0_465_mac_sa.dmg), [Linux](https://archive.org/download/standaloneflashplayers/fp/fp_32/32.0.0.465/flashplayer32_0r0_465_linux_sa.x86_64.tar.gz))

# Things that are not working

- Making a wish at the Tree of Dreams
- Sending back Pokémon through the Entralink
- Dream Catalogue
- Share Shelf