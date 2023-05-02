from django.shortcuts import render
from django.http import HttpResponse

from urllib import response
from googleapiclient.discovery import build

# Create your views here.

def index(request):
    return render(request, 'form.html')

videoIds = []

def get_video_ids(youtube, channelId):
    """
    Refer to the documentation: https://googleapis.github.io/google-api-python-client/docs/dyn/youtube_v3.search.html
    """

    request = youtube.channels().list(
        part="contentDetails",
        id=channelId
    )

    response = request.execute()

    playlistId = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    request = youtube.playlistItems().list(
        part="contentDetails",
        playlistId=playlistId,
        maxResults=50
    )

    response = request.execute()
    responseItems = response['items']

    videoIds.extend([item['contentDetails']['videoId'] for item in responseItems])

    # if there is nextPageToken, then keep calling the API
    while response.get('nextPageToken', None):
        #print(f'Fetching next page of videos for {channelId}_{playlistId}')
        request = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlistId,
            maxResults=50,
            pageToken=response['nextPageToken']
        )
        response = request.execute()
        responseItems = response['items']

        videoIds.extend([item['contentDetails']['videoId'] for item in responseItems])
    
    #print(f"Finished fetching videoIds for {channelId}. {len(videoIds)} videos found.")

    return videoIds

def findvideoid(request):
    channelid = request.GET["channelid"]
    youtube = build("youtube", "v3", developerKey=request.GET["youtubeapikey"])
    get_video_ids(youtube, channelid)
    return render(request, 'result.html', {"result":videoIds})