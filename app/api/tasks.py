from celery.decorators import task
import subprocess
from api.models import *
import json
import logging
logger = logging.getLogger(__name__)

BASE_DIR = '/home/ved/'
UNCOMPRESSED_FILE_PATH = BASE_DIR+'uncompressed_media/'
COMPRESSED_FILE_PATH = BASE_DIR+'compressed_media/'

@task(name="video_compression")
def video_compression(file_name, media_id, story_id):

    filepath = UNCOMPRESSED_FILE_PATH+str(story_id)+"_"+file_name
    new_file = COMPRESSED_FILE_PATH+str(story_id)+"_"+file_name

    compressed_file = filepath
    w, h = get_media_dimensions(filepath)
    if w != 640 or h != 480:
        result = subprocess.run(['ffmpeg', '-i', filepath, '-s', '640x480', '-strict', '-2', new_file],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)

        if result.returncode == 0:
            compressed_file = new_file


    m = Media.objects.get(id=media_id)
    m.compressed_file = compressed_file
    m.save()
    logger.info("updated media compressed file")

@task(name="image_compression")
def image_compression(file_name, media_id, story_id):

    filepath = UNCOMPRESSED_FILE_PATH+str(story_id)+"_"+file_name
    new_file = COMPRESSED_FILE_PATH+str(story_id)+"_"+file_name

    compressed_file = filepath
    w, h = calculate_image_size(filepath)
    if w != 0 or h != 0:
        scale = 'scale='+str(w)+':'+str(h)
        result = subprocess.run(['ffmpeg', '-i', filepath, '-vf', scale, new_file],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)

        if result.returncode == 0:
            compressed_file = new_file

    m = Media.objects.get(id=media_id)
    m.compressed_file = compressed_file
    m.save()
    logger.info("updated media compressed file")

def get_media_dimensions(filepath):
    height = 0
    width = 0
    try:
        result = subprocess.run(['ffprobe', '-v', 'quiet', '-print_format',
                        'json', '-show_format', '-show_streams', filepath],
                        stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        if result.returncode == 0:
            media_info = json.loads(result.stdout)['streams']
            for info in media_info:
                if info['codec_type'] == 'video':
                    height = info['height']
                    width = info['width']
        return width, height
    except Exception as e:
        logger.error("Exception in get_media_dimensions : {0}".format(e))
        return height, width

def calculate_video_resolution(filepath):
    w = 0
    try:
        weight, height = get_media_dimensions(filepath)
        if height != 0 and width != 0:
            if height != 480:
                w = round((height/width)*480)
        return w
    except Exception as e:
        logger.error("Exception in calculate_video_resolution : {0}".format(e))
        return w

def calculate_image_size(filepath):
    h = 0
    w = 0
    try:
        width, height = get_media_dimensions(filepath)
        if height != 0 and width != 0:
            if height > 1200 and width > 600:
                w = round((1200*width)/height)
                if w <= 600:
                   h = 1200
                else:
                   h = round((height/width)*600)
                   w = 600
            elif height > 1200:
                w = round((1200*width)/height)
                h = 1200
            elif width > 600:
                h = round((height/width)*600)
                w = 600

        return w, h

    except Exception as e:
        logger.error("Exception in calculate_image_size : {0}".format(e))
        return w, h
