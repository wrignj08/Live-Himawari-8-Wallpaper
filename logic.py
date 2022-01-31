
import os
import time
import json
import funcs
import pathlib
import itertools
import threading
from glob import glob
from PIL import Image
from datetime import datetime
from multiprocessing.pool import ThreadPool

verbose = True

def main_thread():
    thread = threading.Thread(target=lambda: threading.Thread(target=main()))
    thread.start()

def main():
    if verbose:
        print('started main')

    funcs.set_state('Starting')

    while True:

        settings = funcs.get_settings()
        quality = int(settings['quality'])
        thread_count = int(settings['dl_threads'])
        live = bool(settings['live'])

        if not live:
            if verbose:
                print('stopped')
            funcs.set_state('Stopped')

            break

        # tile row and col count
        image_size = [2,4,8,16,20]

        # set quality
        row_col_count = image_size[quality]

        # calc final output image size
        img_size = 550
        array_px = row_col_count*img_size

        # generate all row and col combination
        tile_list = list(itertools.product(range(0,row_col_count), range(0,row_col_count)))

        # set directory for images
        working_path = os.path.expanduser("~/Documents/Live-Himawari-8-Wallpaper/images")
        pathlib.Path(working_path).mkdir(parents=True, exist_ok=True)

        # url format for downlading images
        url_template = 'https://himawari8.nict.go.jp/img/D531106/{}d/550/{}/{}_{}_{}.png'

        # check every x secs if there is a new image to download
        found_new = False

        latest_date,latest_time = funcs.get_latest_time()

    #     check if this image is already made
        final_output = os.path.join(working_path,(latest_date+latest_time).replace('/','_')+f'_h8wp_{quality}.png')
        if verbose:
            print(final_output)
        # funcs.set_state(final_output)
        if not os.path.isfile(final_output):

            args = []
            for coords in tile_list:
                args.append([coords,image_size,quality,latest_date,latest_time,working_path])

            # downlaod multible images at one to speed up the process
            if verbose:
                print('downloading tiles')
            funcs.set_state('Downloading tiles')
            with ThreadPool(thread_count) as tp:
                files = list(tp.imap(funcs.prep_download,args))

            # files = []
            # for i in args:
            #     files.append(funcs.prep_download(i))

            # mosaic all images
            if verbose:
                print('making mosaic')
            funcs.set_state('Making mosaic')
            # mosaiced_array = funcs.mosaic(files,array_px)
            mosaiced_image = funcs.PIL_mosaic(files,array_px)

            # grab a list of any old mosaics so we can remove them later
            old_h8wb_files = glob(working_path+'/*.png')

            # save master array as image
            if verbose:
                print('saving wallpaper')
            # mosaiced_image = Image.fromarray(mosaiced_array).convert('RGB')
            mosaiced_image.save(final_output)
            if verbose:
                print('setting wallpaper')
            # funcs.set_wallpaper(final_output)
            threading.Thread(target=funcs.set_wallpaper(final_output))

            # remove old images
            if verbose:
                print('Removing wallpaper')
            for old_file in old_h8wb_files:
                os.remove(old_file)
            if verbose:
                print('done')

            # grab the current settings and add the new wp path
            settings = funcs.get_settings()
            settings['wp_path'] = final_output
            settings['date'] = latest_date
            settings['time'] = latest_time
            funcs.write_settings(settings)

        else:
            if verbose:
                print(f'nothing new, sleeping for 5 minutes')
            sleep_time  = 300
            for i in range(0,sleep_time):
                sleep_time_remaining = sleep_time-i
                if sleep_time_remaining > 60:
                    sleep_time_remaining_str = f'{round(sleep_time_remaining/60)} mins'
                else:
                    sleep_time_remaining_str = f'{sleep_time_remaining} secs'

                funcs.set_state(f'Next check {sleep_time_remaining_str}')

                settings = funcs.get_settings()
                # live = bool(settings['live'])
                if not bool(settings['live']):
                    break

                refresh = bool(settings['refresh'])
                if refresh:
                    funcs.set_state('Refreshing')
                    if os.path.isfile(final_output):
                        os.remove(final_output)

                    settings['refresh'] = False
                    funcs.write_settings(settings)
                    break

                else:
                    time.sleep(1)
