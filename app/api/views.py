from django.shortcuts import render
from django.http import HttpResponse
from . import helpers
from django.views.decorators.csrf import csrf_exempt
import json
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def create(request):
    try:
        data = request.POST.copy()
        file_name = request.FILES.get('file_name', None)
        resp = helpers.create_story(data, file_name, logger)
        if resp:
            return HttpResponse(
                json.dumps({
                    'message': 'success'
                    }),
                status=200)
        else:
            logger.error("Response for create api is empty")
            return HttpResponse(
                json.dumps({
                    'message': 'failure'
                    }),
                status=500)

    except Exception as e:
        logger.error("Exception in create : {0}".format(e))
        return HttpResponse(
                json.dumps({
                    'message': 'failure',
                    'error_reason' : e
                    }),
                status=500)

def index(request):
    try:
        resp = helpers.fetch_stories(logger)
        if resp:
            return HttpResponse(
                json.dumps({
                    'message': 'success',
                    'data': resp
                    }),
                content_type="application/json",
                status=200)
        else:
            logger.error("Response for fetch_all api is empty")
            return HttpResponse(
                json.dumps({
                    'message': 'failure',
                    'data' : None
                    }),
                status=500)
    except Exception as e:
        logger.error("Exception in index : {0}".format(e))
        return HttpResponse(
                json.dumps({
                    'message': 'failure',
                    'data' : None,
                    'error_reason': str(e)
                    }),
                status=500)

def fetch_media(request, story_id):
    try:
        resp = helpers.fetch_media(story_id, logger)
        if resp:
            return HttpResponse(
                json.dumps({
                    'message': 'success',
                    'data': resp
                    }),
                content_type="application/json",
                status=200)
        else:
            logger.error("Response for fetch_media api is empty")
            return HttpResponse(
                json.dumps({
                    'message': 'failure',
                    'data' : None
                    }),
                status=500)
    except Exception as e:
        logger.error("Exception in fetch_media : {0}".format(e))
        return HttpResponse(
                json.dumps({
                    'message': 'failure',
                    'data' : None,
                    'error_reason': str(e)
                    }),
                status=500)


