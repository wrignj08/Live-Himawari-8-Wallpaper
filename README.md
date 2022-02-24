# Live Himawari
Live Himawari is a macOS menu bar application which sets your desktop wallpaper to the real time view from the Himawari 8 satellite. The imagery comes courtesy of <a href="https://himawari8.nict.go.jp">Himawari-8 Real-time</a>.

<a href="https://github.com/wrignj08/Live_Himawari/raw/main/Live%20Himawari.zip" download>Download Live Himawari 🌏</a>

This app is unsigned, so to open it the first time you will need to right click on it and select 'Open'.

<img src="https://raw.githubusercontent.com/wrignj08/Live_Himawari/main/images/menu.jpg" alt="menu" style="width:400px;">

<img src="https://raw.githubusercontent.com/wrignj08/Live_Himawari/main/images/full%20screen.jpg" alt="full screen view" style="width:800px;">

This app was written in Python 3, the menu bar functionality is provided via <a href="https://rumps.readthedocs.io">rumps</a>.
The image handling is provided via <a href="https://pillow.readthedocs.io">Pillow</a>.
The wallpaper setting logic uses the AppKit Python library, helpfully demonstrated in this <a href="https://stackoverflow.com/a/65947716">answer by Ted Wrigley</a>.
The app packaging is done with <a href="https://pyinstaller.readthedocs.io">PyInstaller</a>.
