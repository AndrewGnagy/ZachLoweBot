#!/usr/bin/python
import praw
import re
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def valid_and_not_already_posted(url_to_check, other_links):
    found_ids = re.findall(r"id\/([0-9]+)\/", url_to_check)
    if len(found_ids) != 1:
        return False
    found_id = found_ids[0]
    for links in other_links:
        if found_id in links['url']:
            return False
    return True

# Doing a headless browser, because that's neat
browser = webdriver.PhantomJS()

# Go to ESPNs search page for "lowe"
browser.get('http://www.espn.com/search/results?q=lowe#gsc.tab=0&gsc.q=lowe')
assert 'ESPN' in browser.title

# Grab links
links = browser.find_elements_by_css_selector('#main-container table.gsc-table-result a.gs-title')

# I'll just look at the first 4 to keep it recent
valid_links = []
for i, a in enumerate(links[:4]):
    print(i, a.text, a.get_attribute("href"))
    # Only stories, no dumb videos
    if ("/story/" in a.get_attribute("href")):
        valid_links.append({'url': a.get_attribute("href"), 'title': a.text})

#print(valid_links)

reddit = praw.Reddit('zachlowebot')
subreddit = reddit.subreddit("zachlowe")

# Get existing links in r/zachlowe
existing_links = []
for i, submission in enumerate(subreddit.new(limit=25)):
    print(i, submission.title, submission.url)
    existing_links.append({'url': submission.url, 'title': submission.title})

# Check so we dont re-post and existing link
# Neat idiomatic python bit! (I think)
links_to_post = [new_link for new_link in valid_links if valid_and_not_already_posted(new_link['url'], existing_links)]
print(links_to_post)

for link in links_to_post:
    subreddit.submit(link['title'], url=link['url'])
    time.sleep(5)
    for submission in subreddit.new(limit=10):
        if submission.title == link.title:
            submission.reply('This post was generated automatically by ZachLoweBot')
