from django.shortcuts import render
from django.http import HttpResponse

from urllib import response
from googleapiclient.discovery import build
from maincodes import get_video_ids, comment_threads, pushtomodel

# Create your views here.

def index(request):
    return render(request, 'form.html')

def getoutput(request):
    if request.method == "POST":
        channelid = request.POST["channelid"]
        youtube = build("youtube", "v3", developerKey=request.POST["youtubeapikey"])
        if request.POST["jenis"] == "videoId":
            result = get_video_ids(youtube, channelid)
        else:
            videoid = get_video_ids(youtube, channelid)
            result = comment_threads(youtube, videoID = videoid[1], channelID = channelid, to_csv = False)
        return render(request, 'form.html', {"result":result[0:5], "channelid" : channelid, "youtubeapikey": request.POST["youtubeapikey"], "jenis":request.POST["jenis"] })
    
    else:
        return render(request,"form.html")