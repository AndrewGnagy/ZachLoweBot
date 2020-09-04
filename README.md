# ZachLoweBot
A reddit bot for scraping and posting Zach Lowe stories  

*ZachLoweBot doesn't hate your favorite team!*

![Zach Lowe SWAMP DRAGONS](zachLoweGoZ.png)

## Setup
First you'll need to create a praw.ini file that contains info needed to connect to Reddit. It will look something like this:
```
[DEFAULT]
# A boolean to indicate whether or not to check for package updates.
check_for_updates=True

# Object to kind mappings
comment_kind=t1
message_kind=t4
redditor_kind=t2
submission_kind=t3
subreddit_kind=t5

# The URL prefix for OAuth-related requests.
oauth_url=https://oauth.reddit.com

# The URL prefix for regular requests.
reddit_url=https://www.reddit.com

# The URL prefix for short URLs.
short_url=https://redd.it

[zachlowebot]
client_id={YOUR_CLIENT_ID}
client_secret={YOUR_SECRET}
password={YOUR_PASSWORD}
username={YOUR_USERNAME}
user_agent=ZachLoweBot v1
```

Next, you'll want to set up a cron job to execute this. I do once every 6 hours: `0 */6 * * *` 
Remember to set your paths in order to get chromedriver to work correctly: `PATH=/usr/local/bin:/usr/bin`  

Dont forget to `pip install`
