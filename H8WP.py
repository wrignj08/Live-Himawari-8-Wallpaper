import rumps
import logic
import json
import os
import funcs
from rumps import *

verbose = True
icon_path = os.path.expanduser("~/Documents/Live-Himawari-8-Wallpaper/menu_icon.png")

def onoff(sender):
    sender.state = not sender.state
    if verbose:
        print(sender.state)
    if sender.state:
        start()
    else:
        stop()

def start():
    settings = funcs.get_settings()
    if verbose:
        print('setting json to True')
    settings['live'] = True

    funcs.write_settings(settings)
    if verbose:
        print('running thread' )
    logic.main_thread()


def stop():
    settings = funcs.get_settings()
    if verbose:
        print('setting json to False')
    settings['live'] = False
    funcs.write_settings(settings)

def refresh(sender):
    settings = funcs.get_settings()
    settings['refresh'] = True
    funcs.write_settings(settings)

def clean_up_before_quit(sender):
    stop()
    rumps.quit_application()

def set_res(sender):
    settings = funcs.get_settings()
    settings['quality'] = res_options.index(sender.title)
    settings['refresh'] = True
    funcs.write_settings(settings)
    if verbose:
        print(f'set res to {sender.title}')

    # for res_str,res_int in zip(res_options,range(0,5)):
    #     new_list = [s.replace("✓ ", "") for s in list_of_strings]
    #     res_menu.append(rumps.MenuItem(res_str,callback=set_res))

app = rumps.App("H8WP",quit_button=None, title=funcs.get_settings()['icon'])

# starts logic thread at startup
start()

def change_icon(icon_menu):
    icon = icon_menu.title
    print(f'change to {icon}')
    app.title = icon
    settings = funcs.get_settings()
    settings['icon'] = icon
    funcs.write_settings(settings)

icon_menu = []
for icon in ['🌏','🛰','🌐']:
    icon_menu.append(rumps.MenuItem(icon,callback=change_icon))

# recalc image age every 30 secs
@rumps.timer(30)
def update_age(_):
    # remove last image age
    try:
        del app.menu['image_age']
    except:
        print('no image age to remove')
        pass
    app.menu.setdefault('image_age', MenuItem(funcs.image_age_str()))

@rumps.timer(1)
def update_state(_):
    # remove last image age
    try:
        del app.menu['state']
    except:
        print('no state to remove')
        pass
    app.menu.setdefault('state', MenuItem(funcs.read_state()))


res_options = ('1100x1100', '2200x2200', '4400x4400', '8800x8800','16000x16000')
res_menu = []

for res_str,res_int in zip(res_options,range(0,5)):
    # new_list = [s.replace("✓ ", "") for s in list_of_strings]
    res_menu.append(rumps.MenuItem(res_str,callback=set_res))

Active = rumps.MenuItem("Active",callback=onoff)
Active.state = 1
app.menu = Active

app.menu = [[rumps.MenuItem('Quality'), res_menu],
            [rumps.MenuItem('Icon'), icon_menu],
            rumps.MenuItem("Refresh now",callback=refresh),
            None,
            rumps.MenuItem("Quit",callback=clean_up_before_quit)]


app.run()
