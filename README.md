<p align="center">
  <a href="" rel="noopener">
 <img width=200px height=200px src="https://i.imgur.com/6wj0hh6.jpg" alt="Project logo"></a>
</p>

<h3 align="center">Graphy API</h3>

---

## Table of Contents
- [About](#about)
- [Getting Started](#getting_started)
- [Design](#design)
- [Usage](#usage)
- [Built Using](#built_using)
- [Authors](#authors)

## About <a name = "about"></a>
Users (also called graphers) will use a mobile app to add their stories. The mobile app will use a REST API to create stories. A story can have a photo, video or text. After a story has been created, a job is queued by the REST API to resize the photo into a size more suitable for the mobile app and downgrade the video in 480p.

The mobile app also has a feed that shows all stories. For every story the app requests and displays the associated photo.

## Getting Started <a name = "getting_started"></a>
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites
Run this commands to get all the prerequisite tools for the project.

```
apt-get install mysql-server mysql-client redis-server ffmpeg ffprobe 
```

### Installing
Following step will get you a copy of the project and run the server in development environment

```
git clone https://github.com/harmanvirk/graphy-api && cd graphy-api
pip3 install -r REQUIREMENTS.txt
cd app
python3 manage.py runserver
```

## Design <a name = "design"></a>
1. Basically this app creates and fetches stories. A story can contain  text, image or video with other params. 
2. To achieve the goal of this app, two models have been defined.
  - Story  
  
|Field Name|Field Description|  
| ----------- | ----------- |  
|user_name|name of the grapher  (string)|  
|name|name of the story (string)|  
|description|any text information that user wants to provide (string)|  
|timestamp|creation time of story (datetime)|  
|latitude|(decimal)|  
|longitude|(decimal)|

  - Media  
  
|Field Name|Field Description|  
| ----------- | ----------- |  
|media_type|image or video (string)|  
|duration|for video (int)|  
|original_file|saved location of file uploaded by user (string)|  
|compressed_file|location of file after compression (string)|  
|story_id|foreign key to story (int)|  

3. The post request for creating story goes through following processing:
	- Story is created with the params from user
	- If the story contains media file of type video or image, it is stored in specific location(uncompressed_media) with filename starting with story_id to make it unique as user might post different file content but with same name. This will prevent overriding of media files.
	- If story doesn't contain any media_file, this process stops here as media model comes into picture only if story contains image or video file.
   - If story contains any media_file, type of the file is checked and accordingly job is queued to the respective compression task for further processing of the file. The job runs in background and is handled by celery an asynchronous task based on distributed messaging passing. Once the job is queued in task, response is returned.

4. Two Compression tasks have been defined to compress image and video:
	- Image: requirement ->  All photos should be resized to be max 1200px (height) by 600px (width)
    	- First step is to calculate the dimensions of the given image file. 
    	- Keeping in mind the given dimensions and aspect ratio of the image, dimensions are calculated and image is resized with new_dimensions using ffmpeg command and is saved to new location(compressed_media) and also compressed_file field is upated in media model.

	- Video: requirement -> All videos should be 480p.
    	- As 480p has the aspect ratio of 4:3 which denotes a vertical resolution of 480 pixels, usually with a horizontal resolution of 640 pixels [reference](https://en.wikipedia.org/wiki/480p)
        - If the dimensions of the video doesn't match with 640x480, video's resolution is changed using ffmpeg command and save to compressed_media location.

        - Note: If both video and image already fulfil the requirements, compressed_file location in  media model is updated with original location of file.

        - Assumptions: media type and duration should be sent by the user.

        In real scenario, user will just upload the file and client will send the required information to the server. But as we don't have a client here so user will be providing the info.
        It should be handled by the client as server should not take this load and should be rejected from client itself if uploaded file size is more than the required size or user has uploaded file other than image or video.

## Running the tests <a name = "tests"></a>
To run the automated test use the following command in ```app``` directory in the graphy-api folder

```
python3 manage.py test
```

## Usage <a name="usage"></a>
1. create API:
	- Attributes: name of grapher, name, description, duration(sec), type (video or image), latitude, longitude and a timestamp
	- To run:
        eg. Postman
            api(Post Request) : http://13.68.190.213:5000/api/create  
            Following key - value pair needs to be send  
            name(story_name), user_name(grapher_name), description, longitude, latitude, file_name(upload a file), duration, type

2. Fetch All API:
	- To run:
            api(GET Request) : http://13.68.190.213:5000/api/fetch_all  
	-Json Response:
			```
            {
                "message": "success",
                "data": [
                {
                    "user_name": "Harman",
                    "name": "graphy",
                    "description": "Graphy app coming soon",
                    "longitude": "65.324000",
                    "latitude": "85.324000",
                    "timestamp": "2020-05-28 11:28:01.675106+00:00",
                    "media": null
                },
                {
                    "user_name": "User1",
                    "name": "image",
                    "description": "Uploading image file",
                    "longitude": "85.324000",
                    "latitude": "45.324000",
                    "timestamp": "2020-05-27 19:58:55.807404+00:00",
                    "media": {
                        "type": "image",
                        "duration": 0,
                        "file": "/home/ved/compressed_media/2_uploadImage.png"
                    }
                },
                {
                    user_name": "User_Graphy",
                    "name": "video",
                    "description": "Uploading video file",
                    "longitude": "23.717200",
                    "latitude": "43.717200",
                    "timestamp": "2020-05-27 19:55:18.168566+00:00",
                    "media": {
                        "type": "video",
                        "duration": 30,
                        "file": "/home/ved/uncompressed_media/3_videoTest.mp4"
                    }
                }]
            }
			```
        
        The above json response contains three stories, newest first.

3. Fetch media file for story:
	- To run:
            api(GET Request) : http://13.68.190.213:5000/api/fetch_media/47  
            47 is the id of some random story
	- Json response:
			```
            {
                "message": "success",
                "data": {
                    "compressed_file": "/home/ved/uncompressed_media/47_Test.mp4"
                }
            }
			```


## Built Using <a name = "built_using"></a>
- [Django](https://www.djangoproject.com/) - REST API Framework
- [MySQL](https://www.mysql.com/) - Database

## Authors <a name = "authors"></a>
- [@harmanvirk](https://github.com/harmanvirk)
