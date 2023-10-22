#!/usr/bin/python
import praw
import os
import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import date

def not_already_posted(title_to_check, other_titles):
    for title in other_titles:
        if title_to_check in title['title']:
            return False
    return True

def spotify_get_links(url, title, title_assert):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    valid_links = []
    print('Get ' + title + ' links')
    assert title_assert in soup.title.text
    links = soup.select('[data-testid="show-all-episode-list"] a')
    for i, link in enumerate(links[:1]):
        print(i, link.text, link.get("href"))
        valid_links.append({'url': link.get("href"), 'title': link.text})
    return valid_links

def main():
    print('Starting ZachLoweBot')

    valid_links = []
    spotify_links = []

    pods = [
        ["https://open.spotify.com/show/2mZHt3zBxyIuc0PYLdDDkr", "Lowe Post", "Lowe"]
    ]

    #Iterate through podcasts to get links
    for pod in pods:
        spotify_links += spotify_get_links(pod[0], pod[1], pod[2])

    print('Links:')
    print(valid_links)
    print(spotify_links)

    if "LB_CLIENT_ID" in os.environ:
        reddit = praw.Reddit(
            client_id=os.getenv("LB_CLIENT_ID"),
            client_secret=os.getenv("LB_CLIENT_SECRET"),
            user_agent=os.getenv("LB_USER_AGENT"),
        )
    else:
        reddit = praw.Reddit('zachlowebot')
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
