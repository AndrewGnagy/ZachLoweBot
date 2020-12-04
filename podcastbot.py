#!/usr/bin/python
import praw
import re
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

def not_already_posted(url_to_check, other_links):
    for links in other_links:
        if url_to_check == links['url']:
            return False
    return True

def stitcher_get_links(browser, url, title, title_assert):
    valid_links = []
    print('Get ' + title + ' links')
    browser.get(url)
    time.sleep(2)
    assert title_assert in browser.title
    links = browser.find_elements_by_css_selector('a.episode-link')
    for i, link in enumerate(links[:2]):
        linkText = link.find_element_by_css_selector('div.text-truncate')
        print(i, linkText.text, link.get_attribute("href"))
        valid_links.append({'url': link.get_attribute("href"), 'title': title + ' | ' + linkText.text})
    return valid_links

def spotify_get_links(browser, url, title, title_assert):
    valid_links = []
    print('Get ' + title + ' links')
    browser.get(url)
    time.sleep(2)
    assert title_assert in browser.title
    links = browser.find_elements_by_css_selector('[data-testid="show-all-episode-list"] a')
    for i, link in enumerate(links[:2]):
        print(i, link.text, link.get_attribute("href"))
        valid_links.append({'url': link.get_attribute("href"), 'title': title + ' | ' + link.text})
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
    ["https://open.spotify.com/show/2mZHt3zBxyIuc0PYLdDDkr", "Lowe Post", "Lowe"],
    ["https://open.spotify.com/show/12kpkAvUj6LGxzViDIH0qH", "Thinking Basketball", "Thinking"],
    ["https://open.spotify.com/show/5vMLIaAcXeWUpXRpUt5qXY", "JJ Redick's Old Man and the Three", "JJ"],
    ["https://open.spotify.com/show/7rPj9HV9s5gwPnyPIruxKU", "Dunc'd On", "Dunc"],
    ["https://open.spotify.com/show/5IQEIZpEp32XFef8MyQaq7", "Hollinger & Duncan", "Hollinger"],
    ["https://open.spotify.com/show/6plYDxq6lq6V8gYSpvw783", "House of Strauss", "House"],
    ["https://open.spotify.com/show/7hVMyKCBLJ6uqIKcvKuz88", "Athletic NBA Show", "Athletic"],
    ["https://open.spotify.com/show/6ePgqbuKwFIcdxis8oPhGU", "Book of Basketball", "Book"]
]

#*************
# Lowe Post
#*************
print('Get LowePost links')
browser.get('http://www.espn.com/espnradio/podcast/archive/_/id/10528553')
assert 'PodCenter' in browser.title
links = browser.find_elements_by_css_selector('.arclist-item')
for i, listItem in enumerate(links[:2]):
    linkTag = listItem.find_element_by_css_selector('.arclist-play a:first-child')
    linkText = listItem.find_element_by_css_selector('h2')
    print(i, linkText.text, linkTag.get_attribute("href"))
    valid_links.append({'url': linkTag.get_attribute("href"), 'title': 'Lowe Post | ' + linkText.text})

#*************
# The Mismatch
#*************
print('Get The Mismatch links')
browser.get('https://www.theringer.com/the-mismatch-nba-show')
assert 'The Mismatch' in browser.title
links = browser.find_elements_by_css_selector('a[data-analytics-link="article"]')
for i, link in enumerate(links[:2]):
    print(i, link.text, link.get_attribute("href"))
    valid_links.append({'url': link.get_attribute("href"), 'title': 'The Mismatch | ' + link.text})

#*************
# Hollinger & Duncan
#*************
valid_links += stitcher_get_links(browser, 'https://www.stitcher.com/show/hollinger-duncan-nba-show', "Hollinger & Duncan", "Hollinger")

#*************
# Thinking Basketball
#*************
valid_links += stitcher_get_links(browser, 'https://www.stitcher.com/show/thinking-basketball-podcast', "Thinking Basketball", "Thinking")

#Iterate through podcasts to get links
for pod in pods:
    spotify_links += spotify_get_links(browser, pod[0], pod[1], pod[2])

for spot_link in spotify_links:
    for valid_link in valid_links:
        if valid_link['title'][0:30] == spot_link['title'][0:50]:
            spot_link['comment'] = "Additional links: " + valid_link['url']

print('Links:')
print(valid_links)
print(spotify_links)

reddit = praw.Reddit('zachlowebot')
subreddit = reddit.subreddit("nbapodcasts")

# Get existing links in r/nbapodcasts
print('Get existing sub links')
existing_links = []
for i, submission in enumerate(subreddit.new(limit=35)):
    print(i, submission.title, submission.url)
    existing_links.append({'url': submission.url, 'title': submission.title})

# Check so we dont re-post and existing link
# Neat idiomatic python bit! (I think)
links_to_post = [new_link for new_link in spotify_links if not_already_posted(new_link['url'], existing_links)]
print("Posting:")
print(links_to_post)

#Get ZachLoweBot flair
flair_id = ""
for template in subreddit.flair.link_templates:
    if "ZachLoweBot" in template['text']:
        flair_id = template["id"]

# Submit the posts
for link in links_to_post:
    submission = subreddit.submit(link['title'], url=link['url'], flair_id=flair_id)
    #Wait 5 seconds in case Reddit api is slow
    time.sleep(5)
    #Comment on newly posted submission
    if 'comment' in link:
        comment = submission.reply(link['comment'])
        comment.mod.distinguish(sticky=True)
