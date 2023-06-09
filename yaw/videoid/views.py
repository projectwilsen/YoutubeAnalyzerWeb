from django.shortcuts import render
from django.http import HttpResponse
from urllib import response
from googleapiclient.discovery import build
from maincodes import get_video_ids, comment_threads, pushtomodel
import pandas as pd
import io
import csv

TABLE = None

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
            result = comment_threads(youtube, videoID = videoid[1], channelID = channelid)
            global TABLE 
            TABLE = pd.DataFrame(result)
        return render(request, 'form.html', {"result":result[0:5], "channelid" : channelid, "youtubeapikey": request.POST["youtubeapikey"], "jenis":request.POST["jenis"] })
    
    else:
        return render(request,"form.html")
    
def download(request):

    buffer = io.StringIO()
    df = TABLE
    df.to_csv(buffer, index=False, quoting=csv.QUOTE_ALL)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=comment_analysis.csv'

    return response