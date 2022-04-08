import rumps
import logic
import funcs
import pathlib

sf_play = '􀊄  '
sf_refresh = '􀅈 '
sf_gear = '􀍟 '
sf_info = '􀅴  '
sf_quit = '􀁠  '
sf_display = '􀢹 '
sf_display_center = '􀥝 '
sf_display_fill = '􀢿 '
sf_imac = '􀙗'
sf_laptop = '􀙗'
sf_globe_1 = '􀆪'
sf_globe_2 = '􀵵'
sf_globe_3 = '􀵶'
sf_login = '􀷀  '

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
        sender.title = sf_play+'Running'
        app.title = funcs.get_settings()['icon']
    else:
        stop()
        sender.title = '􀟋 Stopped'
        app.title = '􀟋'

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
        app.menu[sf_gear+'Settings'][sf_display+'Resolution'][res_string].state = 0
    # add check mark to new quality value
    res_int = funcs.get_settings()['quality']
    app.menu[sf_gear+'Settings'][sf_display+'Resolution'][res_options[res_int]].state = 1


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

icons = ['🌏','🌐','🛰','🔭','📡','🚀','👩‍🚀','👨‍🚀',sf_display,sf_imac,sf_laptop,sf_globe_1,sf_globe_2,sf_globe_3]

# will change menu icon and save to settings
def change_icon(icon_menu):
    icon = icon_menu.title
    settings = funcs.get_settings()
    settings['icon'] = icon
    funcs.write_settings(settings)
    # app.title = icon
    set_icon()
    set_icon_check_mark()

def set_icon():
    settings = funcs.get_settings()
    icon = settings['icon']
    app.title = icon

# remove check marks from icon menu then add it to selection
def set_icon_check_mark():
    # remove all check marks
    for icon in icons:
        app.menu[sf_gear+'Settings']['😃 Icon'][icon].state = 0
    # add check mark to new quality value
    icon = funcs.get_settings()['icon']
    app.menu[sf_gear+'Settings']['😃 Icon'][icon].state = 1
    app.menu[sf_gear+'Settings']['😃 Icon'].title = icon+' Icon'

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

# will change menu icon and save to settings
def set_fit(fit_menu):
    fit = fit_menu.title
    print(fit)
    settings = funcs.get_settings()
    settings['fit'] = fit.split(' ')[1]
    funcs.write_settings(settings)
    set_fit_check_mark()
    funcs.set_wallpaper(funcs.get_settings()['wp_path'])

# remove check marks from icon menu then add it to selection
def set_fit_check_mark():
    # remove all check marks
    for fit in fit_options:
        app.menu[sf_gear+'Settings'][sf_display_fill+'Fit'][fit].state = 0
    # add check mark to new quality value
    fit = funcs.get_settings()['fit']
    if 'Fill' in fit:
        fit = sf_display_fill+'Fill'
        app.menu[sf_gear+'Settings'][sf_display_fill+'Fit'].title = sf_display_fill+'Fit'
    else:
        fit = sf_display_center+'Center'
        app.menu[sf_gear+'Settings'][sf_display_fill+'Fit'].title = sf_display_center+'Fit'
    app.menu[sf_gear+'Settings'][sf_display_fill+'Fit'][fit].state = 1

fit_options = [sf_display_fill+'Fill',sf_display_center+'Center']

# fit_menu = [rumps.MenuItem(fit_options[0],callback=set_fit),
            # rumps.MenuItem(fit_options[1],callback=set_fit)]

fit_menu = [rumps.MenuItem(fil,callback=set_fit) for fil in fit_options]


# about window
def configuration_window(sender):
    window = rumps.Window(
        title='Live Himawari',
        message=f'Version 1.3\n https://github.com/wrignj08/Live_Himawari',
        dimensions=(120, 0),
        ok='Close',
    )
    response = window.run()


# make menu item structure
app.menu = [rumps.MenuItem(sf_play+"Running",callback=onoff),
            rumps.MenuItem(sf_refresh+"Refresh now",callback=refresh),
            [rumps.MenuItem(sf_gear+'Settings'),[
            [rumps.MenuItem(sf_display+"Resolution"), res_menu],
            [rumps.MenuItem(sf_display_fill+"Fit"), fit_menu],
            [rumps.MenuItem("😃 Icon"), icon_menu],
            rumps.MenuItem(sf_login+"Launch at startup",callback=toggle_auto_start)
            ]],
            rumps.MenuItem(sf_info+"About",callback=configuration_window),
            None,
            rumps.MenuItem("Age"),
            rumps.MenuItem("State"),
            rumps.MenuItem(sf_quit+"Quit",callback=clean_up_before_quit)]

# now that the menu is created add a check mark to Active and on the current resolution
app.menu[sf_play+"Running"].state = 1

# set state of auto start toggle based on system prefs
app.menu[sf_gear+'Settings'][sf_login+"Launch at startup"].state = funcs.check_if_in_login_items()

set_res_check_mark()
set_icon_check_mark()
set_fit_check_mark()
set_icon()
# get things running
app.run()
