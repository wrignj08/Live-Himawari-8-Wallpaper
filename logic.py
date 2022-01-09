
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

def main_thread():
    thread = threading.Thread(target=lambda: threading.Thread(target=main()))
    thread.start()
    return thread

def main():


    while True:

        settings, _ = funcs.get_settings()

        quality = int(settings['quality'])
        thread_count = int(settings['dl_threads'])
        live = bool(settings['live'])

        if not live:
            print('stopped')
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
        working_path = os.path.expanduser("~/Documents/Live Himawari 8 Wallpaper/images")
        pathlib.Path(working_path).mkdir(parents=True, exist_ok=True)

        # url format for downlading images
        url_template = 'https://himawari8.nict.go.jp/img/D531106/{}d/550/{}/{}_{}_{}.png'

        # check every x secs if there is a new image to download
        found_new = False

        latest_date,latest_time = funcs.get_latest_time()
    #     check if this image is already made
        final_output = os.path.join(working_path,(latest_date+latest_time).replace('/','_')+'_h8wp.png')

        print(final_output)
        if not os.path.isfile(final_output):

            args = []
            for coords in tile_list:
                args.append([coords,image_size,quality,latest_date,latest_time,working_path])

            # downlaod multible images at one to speed up the process
            print('downloading tiles')
            with ThreadPool(thread_count) as tp:
                files = list(tp.imap(funcs.prep_download,args))

            # mosaic all images
            print('making mosaic')
            mosaiced_array = funcs.mosaic(files,array_px)

            # grab a list of any old mosaics so we can remove them later
            old_h8wb_files = glob(working_path+'/*h8wp.png')

            # save master array as image
            print('saving wallpaper')
            mosaiced_image = Image.fromarray(mosaiced_array).convert('RGB')
            mosaiced_image.save(final_output)

            print('setting wallpaper')
            funcs.set_wallpaper(final_output)

            # remove old images
            print('Removing wallpaper')
            for old_file in old_h8wb_files:
                os.remove(old_file)
            print('done')

            # grab the current settings and add the new wp path
            settings,settings_path = funcs.get_settings()
            settings['wp_path'] = final_output
            with open(settings_path, 'w') as json_file:
                json.dump(settings, json_file)

        else:
            print(f'nothing new, sleeping for 10 minutes')
            for i in range(0,600):
                settings, _ = funcs.get_settings()
                live = bool(settings['live'])
                if not live:
                    break
                else:
                    time.sleep(1)
