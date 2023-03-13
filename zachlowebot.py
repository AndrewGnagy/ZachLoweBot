#!/usr/bin/python
import praw
import re
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from datetime import date
from selenium.webdriver.common.by import By

def not_already_posted(title_to_check, other_titles):
    for title in other_titles:
        if title_to_check in title['title']:
            return False
    return True

def spotify_get_links(browser, url, title, title_assert):
    valid_links = []
    print('Get ' + title + ' links')
    browser.get(url)
    time.sleep(2)
    assert title_assert in browser.title
    links = browser.find_elements(By.CSS_SELECTOR, '[data-testid="show-all-episode-list"] a')
    for i, link in enumerate(links[:1]):
        print(i, link.text, link.get_attribute("href"))
        valid_links.append({'url': link.get_attribute("href"), 'title': link.text})
    return valid_links

print('Starting ZachLoweBot')

# Doing a headless browser, because that's neat
#browser = webdriver.PhantomJS()
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
browser = webdriver.Chrome(chrome_options=options)

valid_links = []
spotify_links = []

pods = [
    ["https://open.spotify.com/show/2mZHt3zBxyIuc0PYLdDDkr", "Lowe Post", "Lowe"]
]

#Iterate through podcasts to get links
for pod in pods:
    spotify_links += spotify_get_links(browser, pod[0], pod[1], pod[2])

print('Links:')
print(valid_links)
print(spotify_links)

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
