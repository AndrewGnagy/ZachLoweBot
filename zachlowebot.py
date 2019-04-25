#!/usr/bin/python
import praw
import re
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

def valid_and_not_already_posted(url_to_check, other_links):
    found_ids = re.findall(r"id\/([0-9]+)\/", url_to_check)
    if len(found_ids) != 1:
        found_ids = re.findall(r"play\?id=([0-9]+)", url_to_check)
        if len(found_ids) != 1:
            return False
    found_id = found_ids[0]
    for links in other_links:
        if found_id in links['url']:
            return False
    return True

print('Starting ZachLoweBot')

# Doing a headless browser, because that's neat
#browser = webdriver.PhantomJS()
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
browser = webdriver.Chrome(chrome_options=options)

# Go to ESPNs search page for "lowe"
browser.get('http://www.espn.com/search/results?q=lowe#gsc.tab=0&gsc.q=lowe')
assert 'ESPN' in browser.title

# Grab links
links = browser.find_elements_by_css_selector('#main-container table.gsc-table-result a.gs-title')

# I'll just look at the first 2 to keep it recent
valid_links = []
for i, a in enumerate(links[:2]):
    print(i, a.text, a.get_attribute("href"))
    # Only stories, no dumb videos
    if ("/story/" in a.get_attribute("href") and "nba" in a.get_attribute("href")):
        valid_links.append({'url': a.get_attribute("href"), 'title': a.text})

# Grab LowePost links
browser.get('http://www.espn.com/espnradio/podcast/archive/_/id/10528553')
assert 'PodCenter' in browser.title
links = browser.find_elements_by_css_selector('.arclist-item')
for i, listItem in enumerate(links[:2]):
    linkTag = listItem.find_element_by_css_selector('.arclist-play a:first-child')
    linkText = listItem.find_element_by_css_selector('h2')
    print(i, linkText.text, linkTag.get_attribute("href"))
    valid_links.append({'url': linkTag.get_attribute("href"), 'title': 'Lowe Post - ' + linkText.text})

#print(valid_links)

reddit = praw.Reddit('zachlowebot')
subreddit = reddit.subreddit("zachlowe")

# Get existing links in r/zachlowe
existing_links = []
# Only need a few. Honestly ZachLoweBot is about the only poster
for i, submission in enumerate(subreddit.new(limit=10)):
    print(i, submission.title, submission.url)
    existing_links.append({'url': submission.url, 'title': submission.title})

# Check so we dont re-post and existing link
# Neat idiomatic python bit! (I think)
links_to_post = [new_link for new_link in valid_links if valid_and_not_already_posted(new_link['url'], existing_links)]
print(links_to_post)

# Submit the posts
for link in links_to_post:
    submission = subreddit.submit(link['title'], url=link['url'])
    # Wait 5 seconds in case Reddit api is slow
    time.sleep(5)
    # Comment on newly posted submission
    comment = submission.reply('This post was generated automatically by [ZachLoweBot](https://github.com/AndrewGnagy/ZachLoweBot)')
    comment.mod.distinguish(sticky=True)
