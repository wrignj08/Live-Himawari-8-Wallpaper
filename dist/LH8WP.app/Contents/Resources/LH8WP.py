import rumps
import logic
import json
import os
import funcs
from glob import glob

settings,settings_path = funcs.get_settings()
print(settings)

icon_path = '/Users/nicholaswright/Documents/Live Himawari 8 Wallpaper/icon.png'

def start():
    print('setting json to True')
    settings['live'] = True
    with open(settings_path, 'w') as json_file:
        json.dump(settings, json_file)
    print('running thread')
    logic.main_thread()

start()

def stop():
    print('setting json to False')
    settings['live'] = False
    with open(settings_path, 'w') as json_file:
        json.dump(settings, json_file)

def onoff(sender):
    sender.state = not sender.state
    print(sender.state)
    if sender.state:
        start()
    else:
        stop()


def clean_up_before_quit(sender):
    stop()
    rumps.quit_application()

def set_res(sender):
    settings['quality'] = res_options.index(sender.title)
    with open(settings_path, 'w') as json_file:
        json.dump(settings, json_file)
    print(f'set res to {sender.title}')

app = rumps.App("H8WP",quit_button=None, icon=icon_path)

res_options = ('1100x1100', '2200x2200', '4400x4400', '8800x8800','16000x16000')
res_menu = []
for res_str,res_int in zip(res_options,range(0,5)):
    res_menu.append(rumps.MenuItem(res_str,callback=set_res))

Active = rumps.MenuItem("Active",callback=onoff)
Active.state = 1
app.menu = Active

app.menu = [rumps.MenuItem('Quality'), res_menu],

app.menu = rumps.MenuItem("Quit",callback=clean_up_before_quit)


app.run()
