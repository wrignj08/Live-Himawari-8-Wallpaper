import rumps
import logic
import funcs

verbose = True

# will toggle the logic thread
def onoff(sender):
    sender.state = not sender.state
    if verbose:
        print(sender.state)
    if sender.state:
        start()
    else:
        stop()

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
        app.menu['Resolution'][res_string].state = 0
    # add check mark to new quality value
    res_int = funcs.get_settings()['quality']
    app.menu['Resolution'][res_options[res_int]].state = 1

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
app = rumps.App("H8WP",quit_button=None, title=funcs.get_settings()['icon'])

# starts logic thread at startup
start()

# will change menu icon and save to settings
def change_icon(icon_menu):
    icon = icon_menu.title
    if verbose:
        print(f'change to {icon}')
    app.title = icon
    settings = funcs.get_settings()
    settings['icon'] = icon
    funcs.write_settings(settings)

# build menu list for icon options
icon_menu = [rumps.MenuItem(icon,callback=change_icon) for icon in ['🌏','🌐','🛰','🔭','🖥️','💻','👩‍🚀','👨‍🚀']]

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
app.menu = [rumps.MenuItem("Active",callback=onoff),
            [rumps.MenuItem('Resolution'), res_menu],
            [rumps.MenuItem('Icon'), icon_menu],
            rumps.MenuItem("Refresh now",callback=refresh),
            None,
            rumps.MenuItem("Age"),
            rumps.MenuItem("State"),
            rumps.MenuItem("Quit",callback=clean_up_before_quit)]

# now that the menu is created add a check mark to Active and on the current resolution
app.menu["Active"].state = 1
set_res_check_mark()
# get things running
app.run()
