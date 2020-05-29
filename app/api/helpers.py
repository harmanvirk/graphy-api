from api.models import *
import json
from django.utils import timezone
import subprocess
from . import tasks
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

def create_story(data, file_name, logger):
    try:
        user_name = data.get('user_name', '')
        story_name = data.get('name', '')
        description = data.get('description', '')
        media_type = data.get('type', '')
        duration = data.get('duration', 0)
        longitude = data.get('longitude', 0)
        latitude = data.get('latitude', 0)

        if user_name:
            story_json = {
                'user_name': user_name,
                'name': story_name,
                'description': description,
                'timestamp': timezone.now(),
                'longitude': longitude,
                'latitude':  latitude
            }
            with transaction.atomic():
                story = Story.objects.create(**story_json)

                if file_name and media_type:
                    filepath = tasks.UNCOMPRESSED_FILE_PATH+str(story.id)+"_"+file_name.name
                    with open(filepath, 'wb+') as destination:
                        for chunk in file_name.chunks():
                            destination.write(chunk)

                    media_json = {
                            'media_type': media_type,
                            'duration': duration,
                            'original_file': filepath,
                            'compressed_file': None,
                            'story': story
                    }
                    media = Media.objects.create(**media_json)

                    if media_type == 'video':
                        tasks.video_compression.delay(file_name.name, media.id, media.story_id)
                    elif media_type == 'image':
                        tasks.image_compression.delay(file_name.name, media.id, media.story_id)

            return user_name 
        else:
            logger.error("User name is empty in create_story")
            return None

    except Exception as e:
        logger.error("Exception in create_story : {0}".format(e))
        return None 

def get_story_obj(story):
    temp = {}
    temp["user_name"] = story.user_name
    temp["name"] = story.name
    temp["description"] = story.description
    temp["longitude"] = str(story.longitude)
    temp["latitude"] = str(story.latitude)
    temp["timestamp"] = str(story.timestamp)
    try:
        m = story.media
        media = {
            "type" : m.media_type,
            "duration": m.duration,
            "file": m.compressed_file
        }
    except:
        media = None

    temp["media"] = media

    return temp

def fetch_stories(logger):
    try:
        stories = Story.objects.prefetch_related('media').all().order_by('-timestamp')

        nested_obj = []
        for story in stories:
            nested_obj.append(get_story_obj(story))

        return nested_obj

    except Exception as e:
        logger.error("Exception in fetch_stories : {0}".format(e))
        return None

def fetch_media(story_id, logger):
    try:
        try:
            comp_file = Media.objects.values('compressed_file').get(story_id=story_id)
        except ObjectDoesNotExist:
            comp_file = {'compressed_file':'DNE'}

        return comp_file
    except Exception as e:
        logger.error("Exception in fetch_media : {0}".format(e))
        return None


