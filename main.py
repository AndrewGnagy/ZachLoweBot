#!/usr/bin/python
import praw
import os
import time
from datetime import date
import requests
import base64
from dotenv import load_dotenv
load_dotenv()

def not_already_posted(title_to_check, other_titles):
    for title in other_titles:
        if title_to_check in title['title']:
            return False
    return True

def spotify_get_links(id, title, title_assert):
    
    client_id = os.getenv("SP_CLIENT_ID")
    client_secret = os.getenv("SP_CLIENT_SECRET")

    encoded = base64.b64encode((client_id + ":" + client_secret).encode("ascii")).decode("ascii")

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic " + encoded
    }
    
    payload = {
        "grant_type": "client_credentials"
    }
    
    response = requests.post("https://accounts.spotify.com/api/token", data=payload, headers=headers)
    print(response.text)

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + response.json()['access_token']
    }
    response = requests.get('https://api.spotify.com/v1/shows/' + id + '/episodes?limit=1', headers=headers)
    print(response.json())
    return [{'url': 'https://open.spotify.com/episode/' + x['id'], 'title': x['name']} for x in response.json()['items']]

def main(x, y):
    print('Starting ZachLoweBot')

    valid_links = []
    spotify_links = []

    pods = [
        ["2mZHt3zBxyIuc0PYLdDDkr", "Lowe Post", "Lowe"]
    ]

    #Iterate through podcasts to get links
    for pod in pods:
        spotify_links += spotify_get_links(pod[0], pod[1], pod[2])

    print('Links:')
    print(valid_links)
    print(spotify_links)

    reddit = praw.Reddit(
        client_id=os.getenv("LB_CLIENT_ID"),
        client_secret=os.getenv("LB_CLIENT_SECRET"),
        user_agent=os.getenv("LB_USER_AGENT"),
        username=os.getenv("LB_USERNAME"),
        password=os.getenv("LB_PASSWORD"),
    )
    subreddit = reddit.subreddit("zachlowe")

    existing_links = []
    # Only need a few. Honestly ZachLoweBot is about the only poster
    for i, submission in enumerate(subreddit.new(limit=10)):
        print(i, submission.title, submission.url)
        existing_links.append({'url': submission.url, 'title': submission.title})
            
    print(existing_links)

    # Check so we dont re-post and existing link
    # Neat idiomatic python bit! (I think)
    links_to_post = [new_link for new_link in spotify_links if not_already_posted(new_link['title'], existing_links)]
    print("Posting:")
    print(links_to_post)

    # Submit the posts
    for link in links_to_post:
        submission = subreddit.submit("Lowe Post - " + link['title'] + ": " + date.today().strftime("%B %d, %Y"), url=link['url'])
        #Wait 5 seconds in case Reddit api is slow
        time.sleep(5)
        #Comment on newly posted submission
    #    if 'comment' in link:
    #        comment = submission.reply(link['comment'])
    #        comment.mod.distinguish(sticky=True)