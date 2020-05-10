from datetime import datetime
import requests
import json
import time
import os
import boto3

def lambda_handler(event, context):
    number_of_videos = os.environ.get("number_of_videos")
    bucketname='leinsterdash'
    url="https://api.twitch.tv/kraken/clips/top?limit="+str(number_of_videos)+"&game=League%20of%20Legends&trending=true&period=week"
    
    referrer = "google.ie"
    client_id = '022i90v7stu8i3u71otlf5xxa6w8si'
    
    headers = {
        'Client-ID' : client_id,    
        'Accept': 'application/vnd.twitchtv.v5+json'
    }
    response = requests.get(url, headers=headers, timeout=10)
    clips=[]       
    test = json.loads(response.content)
    today = datetime.now().strftime("%d_%m_%Y")
    save_location = "top_clips_" + today
    for item in test['clips']:
        temp = item['thumbnails']['medium']
        temp2='-'.join(temp.split('-')[:-2])+".mp4"
        clips.append(temp2)


    for clip in clips:
        r=requests.get(clip)
        key=clip.split('/')[-1]
        s3=boto3.client('s3')
        final_key = 'videos/' +today+'/'+key
        place='/tmp/'+key
        #os.mkdir('league_videos/top_clips_'+today)
        with open(place, 'wb') as f:
            f.write(r.content)
        s3.upload_file(place, bucketname,final_key)
