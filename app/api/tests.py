from django.test import TestCase, Client
from api.models import Story, Media
from django.utils import timezone
from django.urls import reverse
from django.urls import resolve
from urllib.parse import urlencode
from . import views, tasks
import json
MEDIA_PATH = '/home/ved/uncompressed_media/'

client = Client()
class IndexTest(TestCase):

    def setUp(self):
        story1 = Story.objects.create(name="Test Story 1", user_name="User 1",
                                      description="Graphy Test Story 1",
                                      timestamp=timezone.now(), longitude=23.456,
                                      latitude=54.232)
        Media.objects.create(media_type="image", duration=0, original_file="image1.png",
                             compressed_file="{}_image.png".format(story1.id),
                             story_id=story1.id)

        story2 = Story.objects.create(name="Test Story 2", user_name="User 2",
                                      description="Graphy Test Story 2",
                                      timestamp=timezone.now(), longitude=25.129,
                                      latitude=74.611)
        Media.objects.create(media_type="image", duration=0, original_file="image2.png",
                             compressed_file="{}_image.png".format(story2.id),
                             story_id=story2.id)


    def test_fetch_all(self):
        response = client.get(reverse('fetch_all'))
        stories = Story.objects.prefetch_related('media').all().order_by('-timestamp')

        self.assertEqual(len(json.loads(response.content)['data']), len(stories))
        self.assertEqual(response.status_code, 200)

class CreateTest(TestCase):
    def setUp(self):
        self.valid_story = urlencode({
            'user_name': 'Muffin',
            'name': 'Muffin video',
            'description': 'video about muffin',
            'longitude': 24.56,
            'latitude': 45.56,
            'file_name': '/home/ved/Task.mp4',
            'type': 'video',
            'duration': 30
        })
        self.valid_missing_file_story = urlencode({
            'user_name': 'Muffin',
            'name': 'Muffin',
            'description': 'Only test about muffin',
            'longitude': 24.56,
            'latitude': 45.56,
            'file_name': '',
            'type': '',
            'duration': None
        })
        self.invalid_story = urlencode({
            'user_name': '',
            'name': 'Muffin video',
            'description': 'hello',
            'longitude': 24.56,
            'latitude': 45.56,
            'file_name': '/home/ved/Task.mp4',
            'type': 'video',
            'duration': 30
        })

    def test_create_valid_story(self):
        response = client.post(
            reverse('create'),
            data=self.valid_story,
            content_type='application/x-www-form-urlencoded'
        )
        self.assertEqual(response.status_code, 200)

    def test_create_invalid_story(self):
        response = client.post(
            reverse('create'),
            data=self.invalid_story,
            content_type='application/x-www-form-urlencoded'
        )
        self.assertEqual(response.status_code, 500)

    def test_create_valid_missing_file_story(self):
        response = client.post(
            reverse('create'),
            data=self.valid_missing_file_story,
            content_type='application/x-www-form-urlencoded'
        )
        self.assertEqual(response.status_code, 200)


class FetchMediaTest(TestCase):
    def setUp(self):
        self.story = Story.objects.create(name="Test Story 1", user_name="User 1",
                                      description="Graphy Test Story 1",
                                      timestamp=timezone.now(), longitude=23.456,
                                      latitude=54.232)
        Media.objects.create(media_type="image", duration=0, original_file="image1.png",
                             compressed_file="{}_image.png".format(self.story.id),
                             story_id=self.story.id)

        self.story_no_media = Story.objects.create(name="Test Story 1", user_name="User 1",
                                      description="Graphy Test Story 1",
                                      timestamp=timezone.now(), longitude=23.456,
                                      latitude=54.232)

        self.story_no_compressed = Story.objects.create(name="Test Story 1",
                                      user_name="User 1", description="Graphy Test Story 1",
                                      timestamp=timezone.now(), longitude=23.456,
                                      latitude=54.232)
        Media.objects.create(media_type="image", duration=0, original_file="image1.png",
                             compressed_file=None, story_id=self.story_no_compressed.id)

        self.comp_file = Media.objects.values('compressed_file').get(story_id=self.story.id)
        self.comp_no_media_file = {'compressed_file':'DNE'}

        try:
            self.comp_no_compressed_file = \
                Media.objects.values('compressed_file').get(story_id=self.story_no_compressed.id)
        except:
            self.comp_no_compressed_file = None

    def test_fetch_media(self):
        response = client.get(
            reverse('fetch_media', kwargs={'story_id': self.story.id})
        )
        self.assertEqual(json.loads(response.content)['data'], self.comp_file)
        self.assertEqual(response.status_code, 200)

    def test_fetch_no_compressed(self):
        response = client.get(
            reverse('fetch_media', kwargs={'story_id': self.story_no_compressed.id})
        )
        self.assertEqual(json.loads(response.content)['data'], self.comp_no_compressed_file)
        self.assertEqual(response.status_code, 200)

    def test_fetch_no_media(self):
        response = client.get(
            reverse('fetch_media', kwargs={'story_id': self.story_no_media.id})
        )
        self.assertEqual(json.loads(response.content)['data'], self.comp_no_media_file)
        self.assertEqual(response.status_code, 200)

class ImageCompressionTest(TestCase):
    def setUp(self):
        self.story1 = Story.objects.create(name="Test Story 1", user_name="User 1",
                                      description="Graphy Test Story 1 size 600x600",
                                      timestamp=timezone.now(), longitude=23.456,
                                      latitude=54.232)

        self.filename1 = MEDIA_PATH+str(self.story1.id)+"_image_600x600.png"
        self.media1 = Media.objects.create(media_type="image", duration=0, original_file=self.filename1,
                             compressed_file=None, story_id=self.story1.id)

        self.story2 = Story.objects.create(name="Test Story 2", user_name="User 2",
                                      description="Graphy Test Story 2 size 600x1300",
                                      timestamp=timezone.now(), longitude=23.456,
                                      latitude=54.232)

        self.filename2 = MEDIA_PATH+str(self.story2.id)+"_image_600x1300.png"
        self.media2 = Media.objects.create(media_type="image", duration=0, original_file=self.filename2,
                             compressed_file=None, story_id=self.story2.id)

        self.story3 = Story.objects.create(name="Test Story 3", user_name="User 3",
                                      description="Graphy Test Story 3 size 1300x1300",
                                      timestamp=timezone.now(), longitude=23.456,
                                      latitude=54.232)

        self.filename3 = MEDIA_PATH+str(self.story3.id)+"_image_1300x1300.png"
        self.media3 = Media.objects.create(media_type="image", duration=0, original_file=self.filename3,
                             compressed_file=None, story_id=self.story3.id)

        self.story4 = Story.objects.create(name="Test Story 4", user_name="User 4",
                                      description="Graphy Test Story 4 size 800x800",
                                      timestamp=timezone.now(), longitude=23.456,
                                      latitude=54.232)
        self.filename4 = MEDIA_PATH+str(self.story4.id)+"_image_800x800.png"
        self.media4 = Media.objects.create(media_type="image", duration=0, original_file=self.filename4,
                             compressed_file=None, story_id=self.story4.id)

    def test_600x600_image(self):
        file_name = "image_600x600.png"
        w, h = tasks.get_media_dimensions(self.filename1)
        tasks.image_compression(file_name, self.media1.id, self.story1.id)

        compressed_image = Media.objects.values('compressed_file').get(id=self.media1.id)['compressed_file']
        # new dimensions after compression
        new_w, new_h = tasks.get_media_dimensions(compressed_image)

        #checking contraints(should not compress if size < 600x1200, height <= 1200, width <= 600)
        self.assertLessEqual(new_w, 600)
        self.assertLessEqual(new_h, 1200)

        #matching compressed file dimensions as aspect ratio
        self.assertEqual(w, new_w)
        self.assertEqual(h, new_h)
        self.assertEqual(round(w/h), round(new_w/new_h))

    def test_600x1300_image(self):
        file_name = "image_600x1300.png"
        w, h = tasks.get_media_dimensions(self.filename2)
        tasks.image_compression(file_name, self.media2.id, self.story2.id)

        compressed_image = Media.objects.values('compressed_file').get(id=self.media2.id)['compressed_file']
        # new dimensions after compression
        new_w, new_h = tasks.get_media_dimensions(compressed_image)

        #checking contraints
        self.assertLessEqual(new_w, 600)
        self.assertLessEqual(new_h, 1200)

        #matching compressed file dimensions as aspect ratio
        self.assertEqual(round(w/h), round(new_w/new_h))

    def test_1300x1300_image(self):
        file_name = "image_1300x1300.png"
        w, h = tasks.get_media_dimensions(self.filename3)
        tasks.image_compression(file_name, self.media3.id, self.story3.id)

        compressed_image = Media.objects.values('compressed_file').get(id=self.media3.id)['compressed_file']
        # new dimensions after compression
        new_w, new_h = tasks.get_media_dimensions(compressed_image)

        #checking contraints
        self.assertLessEqual(new_w, 600)
        self.assertLessEqual(new_h, 1200)

        #matching compressed file dimensions as aspect ratio
        self.assertEqual(round(w/h), round(new_w/new_h))

    def test_800x800_image(self):
        file_name = "image_800x800.png"
        w, h = tasks.get_media_dimensions(self.filename4)
        tasks.image_compression(file_name, self.media4.id, self.story4.id)

        compressed_image = Media.objects.values('compressed_file').get(id=self.media4.id)['compressed_file']
        # new dimensions after compression
        new_w, new_h = tasks.get_media_dimensions(compressed_image)

        #checking contraints
        self.assertLessEqual(new_w, 600)
        self.assertLessEqual(new_h, 1200)

        #matching compressed file dimensions as aspect ratio
        self.assertEqual(round(w/h), round(new_w/new_h))

class VideoCompressionTest(TestCase):
    def setUp(self):
        self.story1 = Story.objects.create(name="Test Story 1", user_name="User 1",
                                      description="Graphy Test Story 1 size 720x1352",
                                      timestamp=timezone.now(), longitude=23.456,
                                      latitude=54.232)

        self.filename1 = MEDIA_PATH+str(self.story1.id)+"_video_720x1352.MP4"
        self.media1 = Media.objects.create(media_type="video", duration=6, original_file=self.filename1,
                             compressed_file=None, story_id=self.story1.id)

        self.story2 = Story.objects.create(name="Test Story 2", user_name="User 2",
                                      description="Graphy Test Story 2 size 352x640",
                                      timestamp=timezone.now(), longitude=23.456,
                                      latitude=54.232)

        self.filename2 = MEDIA_PATH+str(self.story2.id)+"_video_352x640.mp4"
        self.media2 = Media.objects.create(media_type="video", duration=30, original_file=self.filename2,
                             compressed_file=None, story_id=self.story2.id)


    def test_720x1352_video(self):
        file_name = "video_720x1352.MP4"
        w, h = tasks.get_media_dimensions(self.filename1)
        tasks.video_compression(file_name, self.media1.id, self.story1.id)

        compressed_video = Media.objects.values('compressed_file').get(id=self.media1.id)['compressed_file']
        # new dimensions after compression
        new_w, new_h = tasks.get_media_dimensions(compressed_video)

        #checking contraints(should be 480p)
        self.assertEqual(new_h, 480)
        self.assertEqual(new_w, 640)

    def test_352x640_video(self):
        file_name = "video_352x640.mp4"
        w, h = tasks.get_media_dimensions(self.filename2)
        tasks.video_compression(file_name, self.media2.id, self.story2.id)

        compressed_video = Media.objects.values('compressed_file').get(id=self.media2.id)['compressed_file']
        # new dimensions after compression
        new_w, new_h = tasks.get_media_dimensions(compressed_video)

        #checking contraints
        self.assertEqual(new_h, 480)
        self.assertEqual(new_w, 640)

