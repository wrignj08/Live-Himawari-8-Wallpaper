import rumps
import logic
import funcs
# from rumps import *

verbose = True

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

def set_res_check_mark():
    for res_string in res_options:
        checked_res_str = '✓ '+res_string
        app.menu['Resolution'][res_string].title = res_string

    res_int= funcs.get_settings()['quality']
    app.menu['Resolution'][res_options[res_int]].title = '✓ '+res_options[res_int]

def set_res(sender):

    settings = funcs.get_settings()
    settings['quality'] = res_options.index(sender.title)
    settings['refresh'] = True
    funcs.write_settings(settings)
    if verbose:
        print(f'set res to {sender.title}')

    set_res_check_mark()


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
    app.menu['Age'].title = funcs.image_age_str()

# check state every second
@rumps.timer(1)
def update_state(_):
    app.menu['State'].title = funcs.read_state()

res_options = ('1100x1100', '2200x2200', '4400x4400', '8800x8800','16000x16000')
res_menu = []

for res_str,res_int in zip(res_options,range(0,5)):
    res_menu.append(rumps.MenuItem(res_str,callback=set_res))

Active = rumps.MenuItem("Active",callback=onoff)
Active.state = 1
app.menu = Active

app.menu = [[rumps.MenuItem('Resolution'), res_menu],
            [rumps.MenuItem('Icon'), icon_menu],
            rumps.MenuItem("Refresh now",callback=refresh),
            None,
            rumps.MenuItem("Age"),
            rumps.MenuItem("State"),
            rumps.MenuItem("Quit",callback=clean_up_before_quit)]

# now that the menu is created add the check mark on the current resolution
set_res_check_mark()
app.run()
