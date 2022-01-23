import os
import json
import subprocess
import numpy as np
import urllib.request
from PIL import Image
import datetime

def get_settings_path():
    return os.path.expanduser("~/Documents/Live-Himawari-8-Wallpaper/H8WP_settings.json")

# returns settings dict from json settings file, if no file exists create one
def get_settings():
    settings_path = get_settings_path()
    # check is settings file exists
    if os.path.isfile(settings_path):
        with open(settings_path) as json_file:
            settings = json.load(json_file)
    # if not found set it with defaults
    else:
        settings = {'quality' : 0,
        'dl_threads' : 4,
        'live' : False,
        'wp_path': '',
        'refresh': False,
        'state': 'Starting',
        'date': '',
        'time': ''}

        write_settings(settings)

    return settings

# write settings dict to json settings file
def write_settings(settings):
    settings_path = get_settings_path()
    with open(settings_path, 'w') as json_file:
        json.dump(settings, json_file)

# set text state in settings json file
def set_output_text(text):
    settings = get_settings()
    settings['state'] = text
    write_settings(settings)

def read_state():
    settings = get_settings()
    return settings['state']


# check this url to find the latest image
def get_latest_time():
    url = 'https://himawari8.nict.go.jp/img/D531106/latest.json'
    try:
        print('trying to downlaod latest.json')
        response = urllib.request.urlopen(url)
        encoding = response.info().get_content_charset('utf8')
        latest_date, latest_time = json.loads(response.read().decode(encoding))['date'].split(' ')
        latest_date = latest_date.replace('-','/')
        latest_time = latest_time.replace(':','')
        print(latest_time)
        return latest_date, latest_time
    except:
        print('download to download latest.json, retrying')
        get_latest_time()

def image_age_str():
    settings = get_settings()
    # "date": "2022/01/23080000"
    # "time": "080000"
    date = settings['date']
    time = settings['time']
    image_time = datetime.datetime.strptime(date+time,'%Y/%m/%d%H%M%S')
    utc_now = datetime.datetime.utcnow()
    image_age = (utc_now-image_time).total_seconds()

    friendly_age = f'{round(image_age/(60*60*24))} days'

    if image_age<(60*60*24):
        friendly_age = f'{round(image_age/(60*60))} hours'

    if image_age<(60*60):
        friendly_age = f'{round(image_age/60)} mins'
    # print(f'Image age {usefull_age}')
    return f'{friendly_age} old'


# open image with PIL and make sure it is valid
def verify_image(fn):
    try:
        im = Image.open(fn)
        im.draft(im.mode, (32,32))
        im.load()
        return True
    except:
        os.remove(fn)
        return False

# download image to file path, if failed retry, if image is broken retry
def download(download_url, full_path):
    try:
        # print(download_url)
        # print(full_path)
        urllib.request.urlretrieve(download_url, full_path)
        if not verify_image(full_path):
            download(download_url, full_path)
    except:
        print(f'failed to downlaod image {download_url}, retrying')
        download(download_url, full_path)


#  create download url and file path then pass to downlaod func
def prep_download(args):
    # unpack args
    coords,image_size,quality,latest_date,latest_time,working_path = args
# url format for downlading images
    url_template = 'https://himawari8.nict.go.jp/img/D531106/{}d/550/{}/{}_{}_{}.png'
    y,x = coords
    download_url = url_template.format(image_size[quality],latest_date,latest_time,y,x)
    file_name = download_url.split("/")[-1].replace('.png','_part.png')
    full_path = os.path.join(working_path,file_name)
    download(download_url, full_path)
#     return file path to so we can mosaic them
    return(full_path)


# open each image and place it into master array
def mosaic(files,array_px):
#     build empty array of correct shape to hold all images
    array = np.empty([array_px,array_px,3])
    for file in files:
#         open image and convert into array
        pic = Image.open(file)
        small_array = np.array(pic)
#         empty images only have one band so we can filter them out
        if len(small_array.shape)==3:
#             from image name derive placement
            tile_y,tile_x = os.path.basename(file).replace('.png','').split('_')[1:3]
            abs_y,abs_x = int(tile_y)*550,int(tile_x)*550
#             stuff the image into the master array
            array[abs_x:abs_x+550,abs_y:abs_y+550] = small_array
#     remove all temp files
    for file in files:
        os.remove(file)

    return array.astype(np.uint8)


def set_wallpaper(final_output):

    SCRIPT = """/usr/bin/osascript<<END
                    tell application "System Events"
                        tell every desktop
                            set picture to "%s"
                        end tell
                    end tell
                END"""

    subprocess.Popen(SCRIPT%final_output, shell=True)
