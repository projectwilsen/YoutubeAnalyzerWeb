import os
import csv
from datetime import datetime as dt
from urllib import response
from googleapiclient.discovery import build
from videoid.models import Comment


today = dt.today().strftime('%d-%m-%Y')
PATH = 'commentsFolder/'

def process_comments(response_items, csv_output=False):
    comments = []

    for res in response_items:

        # loop through the replies
        if 'replies' in res.keys():
            for reply in res['replies']['comments']:
                comment = reply['snippet']
                comment['commentId'] = reply['id']
                comments.append(comment)
        else:
            comment = {}
            comment['snippet'] = res['snippet']['topLevelComment']['snippet']
            comment['snippet']['parentId'] = None
            comment['snippet']['commentId'] = res['snippet']['topLevelComment']['id']

            comments.append(comment['snippet'])
        
    keytoremove = ['textDisplay','authorProfileImageUrl','authorChannelUrl','authorChannelId','canRate','viewerRating','likeCount','updatedAt','parentId']
    for i in comments:
        for y in keytoremove:
            del i[y]

    new_comments = []
    for original_dict in comments:
        new_dict = {
            'video_id': original_dict['videoId'],
            'comment_id': original_dict['commentId'],
            'date': original_dict['publishedAt'],
            'author': original_dict['authorDisplayName'],
            'comment_text': original_dict['textOriginal']
        }
        new_comments.append(new_dict)

    if csv_output:
         make_csv(new_comments)
    
    print(f'Finished processing {len(new_comments)} comments.')

    return new_comments


def make_csv(comments, channelID=None, videoID=None):

    new_key = 'channel_id'
    new_value = channelID

    for dictionary in comments:
        new_dict = {new_key: new_value}
        new_dict.update(dictionary)
        dictionary.clear()
        dictionary.update(new_dict)

    # Handle 0 comments issue
    if len(comments) == 0:
        return

    header = comments[0].keys()

    if channelID and videoID:
        filename = f'{PATH}comments_{channelID}_{videoID}_{today}.csv'
    elif channelID:
        filename = f'{PATH}comments_{channelID}_{today}.csv'
    else:
        filename = f'{PATH}comments_{today}.csv'

    with open(filename, 'w', encoding='utf8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(comments)  

    #     channel = next(writer)
    #     channel.append('channel_id')
    #     for item in writer:
    #         item.append(channelID)

    
    pushtomodel(filename)


def pushtomodel(filename):
    with open(filename, newline='',encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Check if the row already exists
            if Comment.objects.filter(comment_id = row['comment_id']).exists(): 
                continue
            
            instance = Comment(channel_id = row['channel_id'], video_id = row['video_id'],
                               comment_id = row['comment_id'], date = row['date'],
                               author = row['author'], comment_text = row['comment_text'])
            instance.save()


scraped_videos = {}

def search_result(youtube, query):
    """
    Refer to the documentation: https://googleapis.github.io/google-api-python-client/docs/dyn/youtube_v3.search.html
    """
    request = youtube.search().list(
        part="snippet",
        q=query,
        maxResults=10,
    )

    return request.execute()

def get_video_ids(youtube, channelId):
    """
    Refer to the documentation: https://googleapis.github.io/google-api-python-client/docs/dyn/youtube_v3.search.html
    """
    videoIds = []

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
        print(f'Fetching next page of videos for {channelId}_{playlistId}')
        request = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlistId,
            maxResults=50,
            pageToken=response['nextPageToken']
        )
        response = request.execute()
        responseItems = response['items']

        videoIds.extend([item['contentDetails']['videoId'] for item in responseItems])
    
    print(f"Finished fetching videoIds for {channelId}. {len(videoIds)} videos found.")

    return videoIds

def channel_stats(youtube, channelIDs, to_csv=False):
    """
    Refer to the documentation: https://googleapis.github.io/google-api-python-client/docs/dyn/youtube_v3.channels.html
    """
    if type(channelIDs) == str:
        channelIDs = [channelIDs]

    stats_list = []

    for channelId in channelIDs:
        request = youtube.channels().list(
            part="statistics",
            id=channelId
        )
        response = request.execute()
        response = response['items'][0]['statistics']
        response['channelId'] = channelId

        stats_list.append(response)

    if to_csv:
        header = stats_list[0].keys()
        with open(f'channelStats.csv', 'w') as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writeheader()
            writer.writerows(stats_list)

    return stats_list

def video_stats(youtube, videoIDs, channelID, to_csv=False):
    if type(videoIDs) == str:
        videoIDs = [videoIDs]
    
    stats_list = []

    for videoId in videoIDs:
        request = youtube.videos().list(
            part="snippet, statistics, contentDetails",
            id=videoId
        )
        response = request.execute()
        statistics = response['items'][0]['statistics']
        snippet = response['items'][0]['snippet']
        statistics['videoId'] = videoId
        statistics['title'] = snippet['title']
        statistics['description'] = snippet['description']
        statistics['publishedAt'] = snippet['publishedAt']
        statistics['duration'] = response['items'][0]['contentDetails']['duration']
        statistics['thumbnail'] = snippet['thumbnails']['high']['url']
        statistics['channelId'] = channelID
        statistics['likeCount'] = statistics.get('likeCount', 0)

        print(f"Fetched stats for {videoId}")
        stats_list.append(statistics)
    
    if to_csv:
        header = stats_list[0].keys()
        with open(f'videosFolder/videoStats_{channelID}.csv', 'w', encoding='utf8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writeheader()
            writer.writerows(stats_list)
    
    print(f'Success in fetching video stats for {channelID}')

    return stats_list


def comment_threads(youtube, videoID, channelID=None, to_csv=False):
    
    comments_list = []
    
    try:
        request = youtube.commentThreads().list(
            part='id,replies,snippet',
            videoId=videoID,
        )
        response = request.execute()
    except Exception as e:
        print(f'Error fetching comments for {videoID} - error: {e}')
        if scraped_videos.get('error_ids', None):
            scraped_videos['error_ids'].append(videoID)
        else:
            scraped_videos['error_ids'] = [videoID]
        return

    comments_list.extend(process_comments(response['items']))

    # if there is nextPageToken, then keep calling the API
    while response.get('nextPageToken', None):
        request = youtube.commentThreads().list(
            part='id,replies,snippet',
            videoId=videoID,
            pageToken=response['nextPageToken']
        )
        response = request.execute()
        comments_list.extend(process_comments(response['items'])) 
    
    print(f"Finished fetching comments for {videoID}. {len(comments_list)} comments found.")
    
    if to_csv:
        try:
            make_csv(comments_list, channelID, videoID)
        except Exception as e:
            print(f'Error writing comments to csv for {videoID} - error: {e}')
            if scraped_videos.get('error_csv_ids', None):
                scraped_videos['error_csv_ids'].append(videoID)
            else:
                scraped_videos['error_csv_ids'] = [videoID]
            return

    if scraped_videos.get(channelID, None):
        scraped_videos[channelID].append(videoID)
    else:
        scraped_videos[channelID] = [videoID]
    
    return comments_list
