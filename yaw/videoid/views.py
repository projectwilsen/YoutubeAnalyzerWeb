from django.shortcuts import render
from django.http import HttpResponse

import scrapetube

# Create your views here.

def index(request):
    return render(request, 'form.html')

# def findvideoid(request):
#     channelid = request.GET["channelid"]
#     return render(request, 'result.html', {"result":channelid})

def findvideoid(request):
    channelid = request.GET["channelid"]
    videoid = []
    videos = scrapetube.get_channel(channelid)
    for video in videos:
        videoid.append(video['videoId'])
    return render(request, 'result.html', {"result":videoid})