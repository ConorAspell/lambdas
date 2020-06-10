from datetime import datetime
import requests
import json
import time
import os
import boto3

def lambda_handler(event, context):
    number_of_videos = os.environ.get("NUMBER_OF_VIDEOS")
    bucketname= os.environ.get("BUCKET_NAME")
    client_id = os.environ.get("CLIENT_ID")
    game = os.environ.get("GAME")
    url="https://api.twitch.tv/kraken/clips/top?limit="+str(number_of_videos)+"&game="+game+"&trending=true&period=week"
  
    referrer = "google.ie"
    headers = {
        'Client-ID' : client_id,    
        'Accept': 'application/vnd.twitchtv.v5+json'
    }
    response = requests.get(url, headers=headers, timeout=10)
      
    test = json.loads(response.content)
    today = datetime.now().strftime("%d_%m_%Y")
    clips=[] 
    for item in test['clips']:
        temp = item['thumbnails']['medium']
        slug='-'.join(temp.split('-')[:-2])+".mp4"
        clips.append(slug)


    for clip in clips:
        r=requests.get(clip)
        key=clip.split('/')[-1]
        s3=boto3.client('s3')
        final_key = 'videos/' +today+'/'+key
        place='/tmp/'+key
        with open(place, 'wb') as f:
            f.write(r.content)
        s3.upload_file(place, bucketname,final_key)
lambda_handler(0,0)
