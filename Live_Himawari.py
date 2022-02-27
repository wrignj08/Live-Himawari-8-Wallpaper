import rumps
import logic
import funcs
import pathlib

# make image and settings folder
print(funcs.get_image_dir())
pathlib.Path(funcs.get_image_dir()).mkdir(parents=True, exist_ok=True)

verbose = True

# will toggle the logic thread
def onoff(sender):
    sender.state = not sender.state
    if verbose:
        print(sender.state)
    if sender.state:
        start()
        sender.title = '👌 Running'
        app.title = funcs.get_settings()['icon']
    else:
        stop()
        sender.title = '🛑 Stopped'
        app.title = '🛑'

# will start the logic thread
def start():
    settings = funcs.get_settings()
    if verbose:
        print('setting json to True')
    settings['live'] = True
    funcs.write_settings(settings)
    if verbose:
        print('running thread' )
    logic.main_thread()

# will stop the current thread
def stop():
    settings = funcs.get_settings()
    if verbose:
        print('setting json to False')
    settings['live'] = False
    funcs.write_settings(settings)

# force a image refresh now
def refresh(_):
    if verbose:
        print('refresh')
    settings = funcs.get_settings()
    settings['refresh'] = True
    funcs.write_settings(settings)

# stop the logic thread and close menu bar app
def clean_up_before_quit(_):
    stop()
    rumps.quit_application()

# remove check marks from quality menu then add it to selection
def set_res_check_mark():
    # remove all check marks
    for res_string in res_options:
        app.menu['🖥️ Resolution'][res_string].state = 0
    # add check mark to new quality value
    res_int = funcs.get_settings()['quality']
    app.menu['🖥️ Resolution'][res_options[res_int]].state = 1


# set the new res to settings file, then force a reset
def set_res(sender):
    settings = funcs.get_settings()
    settings['quality'] = res_options.index(sender.title)
    settings['refresh'] = True
    funcs.write_settings(settings)
    if verbose:
        print(f'set res to {sender.title}')
    set_res_check_mark()

# setup rumps app
app = rumps.App("Live Himawari",quit_button=None, title=funcs.get_settings()['icon'])

# starts logic thread at startup
start()

icons = ['🌏','🌐','🛰','🔭','🚀','👩‍🚀','👨‍🚀']

# will change menu icon and save to settings
def change_icon(icon_menu):
    icon = icon_menu.title

    settings = funcs.get_settings()
    settings['icon'] = icon
    funcs.write_settings(settings)

    app.title = icon
    set_icon_check_mark()

# remove check marks from icon menu then add it to selection
def set_icon_check_mark():
    # remove all check marks
    for icon in icons:
        app.menu['😃 Icon'][icon].state = 0
    # add check mark to new quality value
    icon = funcs.get_settings()['icon']
    app.menu['😃 Icon'][icon].state = 1

# build menu list for icon options
icon_menu = [rumps.MenuItem(icon,callback=change_icon) for icon in icons]

def toggle_auto_start(sender):
    # toggle state
    sender.state = not sender.state
    # based on state add or more from login items
    if sender.state:
        funcs.add_to_login_items()
    else:
        funcs.remove_from_login_items()

# recalc image age every 30 secs
@rumps.timer(30)
def update_age(_):
    app.menu['Age'].title = funcs.image_age_str()

# check state every second
@rumps.timer(1)
def update_state(_):
    app.menu['State'].title = funcs.read_state()

#  setup resolution options
res_options = ('1100x1100', '2200x2200', '4400x4400', '8800x8800','16000x16000')

# build resolution menu
res_menu = [rumps.MenuItem(res_str,callback=set_res) for res_str,res_int in zip(res_options,range(0,5))]

# make menu item structure
app.menu = [rumps.MenuItem("👌 Running",callback=onoff),
            [rumps.MenuItem('🖥️ Resolution'), res_menu],
            [rumps.MenuItem('😃 Icon'), icon_menu],
            rumps.MenuItem('🚀 Launch at startup',callback=toggle_auto_start),
            rumps.MenuItem("↻ Refresh now",callback=refresh),
            None,
            rumps.MenuItem("Age"),
            rumps.MenuItem("State"),
            rumps.MenuItem("🧑‍💻 Version 1.1"),
            rumps.MenuItem("⎋ Quit",callback=clean_up_before_quit)]

# now that the menu is created add a check mark to Active and on the current resolution
app.menu["👌 Running"].state = 1

# set state of auto start toggle based on system prefs
app.menu["🚀 Launch at startup"].state = funcs.check_if_in_login_items()

set_res_check_mark()
set_icon_check_mark()
# get things running
app.run()
