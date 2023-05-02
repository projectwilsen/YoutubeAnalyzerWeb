from django.shortcuts import render
from django.http import HttpResponse

from urllib import response
from googleapiclient.discovery import build
from maincodes import get_video_ids, comment_threads

# Create your views here.

def index(request):
    return render(request, 'form.html')

def findvideoid(request):
    channelid = request.GET["channelid"]
    youtube = build("youtube", "v3", developerKey=request.GET["youtubeapikey"])
    result = get_video_ids(youtube, channelid)
    return render(request, 'videoid.html', {"result":result})

def findcomment(request):
    channelid = request.GET["channelid"]
    youtube = build("youtube", "v3", developerKey=request.GET["youtubeapikey"])
    videoid = get_video_ids(youtube, channelid)
    result = comment_threads(youtube, videoID = videoid[2], channelID = channelid, to_csv = True)
    return render(request, 'comment.html', {"result":result})