## SI 206 2017
## Project 3
## Bradley Scharf
## Building on HW7, HW8 (and some previous material!)

##THIS STARTER CODE DOES NOT RUN!!


##OBJECTIVE:
## In this assignment you will be creating database and loading data 
## into database.  You will also be performing SQL queries on the data.
## You will be creating a database file: 206_APIsAndDBs.sqlite

import unittest
import itertools
import collections
import tweepy
import twitter_info # same deal as always...
import json
import sqlite3
import datetime

## Your name:
## The names of anyone you worked with on this project:

#####

##### TWEEPY SETUP CODE:
# Authentication information should be in a twitter_info file...
consumer_key = twitter_info.consumer_key
consumer_secret = twitter_info.consumer_secret
access_token = twitter_info.access_token
access_token_secret = twitter_info.access_token_secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Set up library to grab stuff from twitter with your authentication, and 
# return it in a JSON format 
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

##### END TWEEPY SETUP CODE

## Task 1 - Gathering data

## Define a function called get_user_tweets that gets at least 20 Tweets 
## from a specific Twitter user's timeline, and uses caching. The function 
## should return a Python object representing the data that was retrieved 
## from Twitter. (This may sound familiar...) We have provided a 
## CACHE_FNAME variable for you for the cache file name, but you must 
## write the rest of the code in this file.

CACHE_FNAME = "206_APIsAndDBs_cache.json"
# Put the rest of your caching setup here:

try:
    cache_file = open(CACHE_FNAME, 'r') # Try to read the data from the file
    cache_contents = cache_file.read()  # If it's there, get it into a string
    CACHE_DICTION = json.loads(cache_contents) # And then load it into a dictionary
    cache_file.close() # Close the file, we're good, we got the data in a dictionary.
except:
    CACHE_DICTION = {}


# Define your function get_user_tweets here:

def get_user_tweets(user):
# check if our search term is already in the cache
    if user in CACHE_DICTION:
        # return data from the cache
        # print ("using cache")
        return CACHE_DICTION[user]
    else:
        # query twitter API for new data

        response = api.user_timeline(user) 
        CACHE_DICTION[user] = response
        #print ("fetching")
        return response



# Write an invocation to the function for the "umich" user timeline and 
# save the result in a variable called umich_tweets:
umich_tweets = get_user_tweets("@umich")

# print(umich_tweets)

## Task 2 - Creating database and loading data into database
## You should load into the Users table:
# The umich user, and all of the data about users that are mentioned 
# in the umich timeline. 
# NOTE: For example, if the user with the "TedXUM" screen name is 
# mentioned in the umich timeline, that Twitter user's info should be 
# in the Users table, etc.

sqlite_file = '206_APIsAndDBs.sqlite'

# Connecting to the database file
conn = sqlite3.connect(sqlite_file)
c = conn.cursor()

c.execute("drop table if exists Users");
c.execute("drop table if exists Tweets");

c.execute('CREATE TABLE Users ( user_id TEXT PRIMARY KEY, screen_name TEXT, num_favs INTEGER, description TEXT )')



user_info = api.get_user("umich")
user_id = user_info['id']
screen_name = user_info['screen_name']
num_favs = user_info['favourites_count']
description = user_info['description']
c.execute("INSERT INTO Users VALUES ( '{i}', '{sn}', {nf}, \"{d}\") "\
    .format(i = user_id, sn = screen_name, nf = num_favs, d = description))
    
    
            
# iterate through the tweets
for t in umich_tweets:
    # check whether each tweet has any user mention
    # (get a list of all of the mentioned users)
    mentioned_users = t['entities']['user_mentions']
    for user in mentioned_users:
        user_name = user['screen_name']
        # if so, get info on that user and
        user_info = api.get_user(user_name)
        # print(user_info)
        user_id = user_info['id']
        screen_name = user_info['screen_name']
        num_favs = user_info['favourites_count']
        description = user_info['description']
        
        # check if we already have them in our table
        c.execute("SELECT * FROM Users WHERE user_id = {ui}".format(ui=user_id))
        entry = c.fetchall()
        if(entry == []):
            # if not, add the info to the table
            c.execute("INSERT INTO Users VALUES ( {i}, '{sn}', {nf}, \"{d}\") "\
                .format(i = user_id, sn = screen_name, nf = num_favs, d = description))


## You should load into the Tweets table: 
# Info about all the tweets (at least 20) that you gather from the 
# umich timeline.
# NOTE: Be careful that you have the correct user ID reference in 
# the user_id column! See below hints.

c.execute('CREATE TABLE Tweets ( tweet_id INTEGER PRIMARY KEY, text TEXT, user_posted TEXT, time_posted TIMESTAMP, retweets INTEGER, FOREIGN KEY (user_posted) REFERENCES Users(user_id))')

for t in umich_tweets:
    tweet_id = t['id']
    user_posted = t['user']['id']
    format_str = "%a %b %d %H:%M:%S %z %Y"
    time_posted = datetime.datetime.strptime(t['created_at'], format_str)
    time_posted = time_posted.strftime("%Y-%m-%d %H:%M:%S")
    text = t['text']
    retweets = t['retweet_count']
    # print(tweet_id)
    # print(user_posted)
    # print(time_posted)
    # print(text)
    # print(retweets)
    c.execute("INSERT INTO Tweets VALUES ( {i}, \"{txt}\", '{up}', '{tp}', {rt} ) "\
        .format(i = tweet_id, txt = text, up = user_posted, tp = time_posted, rt = retweets))

#  5- Use the database connection to commit the changes to the database
conn.commit()



## HINT: There's a Tweepy method to get user info, so when you have a 
## user id or screenname you can find alllll the info you want about 
## the user.

## HINT: The users mentioned in each tweet are included in the tweet 
## dictionary -- you don't need to do any manipulation of the Tweet 
## text to find out which they are! Do some nested data investigation 
## on a dictionary that represents 1 tweet to see it!


## Task 3 - Making queries, saving data, fetching data

# All of the following sub-tasks require writing SQL statements 
# and executing them using Python.

# Make a query to select all of the records in the Users database. 
# Save the list of tuples in a variable called users_info.
c.execute('SELECT * FROM Users')
users_info = c.fetchall() # a list of tuples, each tuple has info on 1 user

# Make a query to select all of the user screen names from the database. 
# Save a resulting list of strings (NOT tuples, the strings inside them!) 
# in the variable screen_names. HINT: a list comprehension will make 
# this easier to complete! 
c.execute('SELECT screen_name FROM Users')
screen_names = c.fetchall() # a list of tuples, each tuple contains only the screen_name

# need to get information out of the tuples by indexing each one
# and reassbling that information in a list
# list comprehension lets us do both at once
screen_names = [ sn[0]  for sn in screen_names ]

#equivalent to:
# new_list = []
# for sn in screen_names:
#     new_list.append(sn[0])


# Make a query to select all of the tweets (full rows of tweet information)
# that have been retweeted more than 10 times. Save the result 
# (a list of tuples, or an empty list) in a variable called retweets.
c.execute('SELECT * FROM Tweets WHERE retweets > 10')
retweets = c.fetchall()



# Make a query to select all the descriptions (descriptions only) of 
# the users who have favorited more than 500 tweets. Access all those 
# strings, and save them in a variable called favorites, 
# which should ultimately be a list of strings.
c.execute('SELECT description FROM Users WHERE num_favs > 500')
favorites = c.fetchall() # list of tuples, each tuple containts one string

favorites = [ nf[0]  for nf in favorites ]


# Make a query using an INNER JOIN to get a list of tuples with 2 
# elements in each tuple: the user screenname and the text of the 
# tweet. Save the resulting list of tuples in a variable called joined_data2.

# bring together information from 2 different tables into 1 query
# keyword: INNER_JOIN tells SQL to cross-reference between the 2 tables. 
c.execute('SELECT u.screen_name, t.text FROM Tweets t INNER JOIN Users u ON t.user_posted = u.user_id ')

joined_data = c.fetchall()

# Make a query using an INNER JOIN to get a list of tuples with 2 
# elements in each tuple: the user screenname and the text of the 
# tweet in descending order based on retweets. Save the resulting 
# list of tuples in a variable called joined_data2.
c.execute('SELECT Users.screen_name, Tweets.text FROM Tweets INNER JOIN Users ON Tweets.user_posted = Users.user_id ORDER BY Tweets.retweets DESC')

joined_data2 = c.fetchall()



file_string = json.dumps(CACHE_DICTION)
with(open(CACHE_FNAME, 'w')) as file:
    file.write(file_string)
    
conn.close()

### IMPORTANT: MAKE SURE TO CLOSE YOUR DATABASE CONNECTION AT THE END 
### OF THE FILE HERE SO YOU DO NOT LOCK YOUR DATABASE (it's fixable, 
### but it's a pain). ###

###### TESTS APPEAR BELOW THIS LINE ######
###### Note that the tests are necessary to pass, but not sufficient -- 
###### must make sure you've followed the instructions accurately! 
######
print("\n\nBELOW THIS LINE IS OUTPUT FROM TESTS:\n")


class Task1(unittest.TestCase):
    def test_umich_caching(self):
        fstr = open("206_APIsAndDBs_cache.json","r")
        data = fstr.read()
        fstr.close()
        self.assertTrue("umich" in data)
    def test_get_user_tweets(self):
        res = get_user_tweets("umsi")
        self.assertEqual(type(res),type(["hi",3]))
    def test_umich_tweets(self):
        self.assertEqual(type(umich_tweets),type([]))
    def test_umich_tweets2(self):
        self.assertEqual(type(umich_tweets[18]),type({"hi":3}))
    def test_umich_tweets_function(self):
        self.assertTrue(len(umich_tweets)>=20)

class Task2(unittest.TestCase):
    def test_tweets_1(self):
        conn = sqlite3.connect('206_APIsAndDBs.sqlite')
        cur = conn.cursor()
        cur.execute('SELECT * FROM Tweets');
        result = cur.fetchall()
        self.assertTrue(len(result)>=20, "Testing there are at least 20 records in the Tweets database")
        conn.close()
    def test_tweets_2(self):
        conn = sqlite3.connect('206_APIsAndDBs.sqlite')
        cur = conn.cursor()
        cur.execute('SELECT * FROM Tweets');
        result = cur.fetchall()
        self.assertTrue(len(result[1])==5,"Testing that there are 5 columns in the Tweets table")
        conn.close()
    def test_tweets_3(self):
        conn = sqlite3.connect('206_APIsAndDBs.sqlite')
        cur = conn.cursor()
        cur.execute('SELECT tweet_id FROM Tweets');
        result = cur.fetchall()
        self.assertTrue(result[0][0] != result[19][0], "Testing part of what's expected such that tweets are not being added over and over (tweet id is a primary key properly)...")
        if len(result) > 20:
            self.assertTrue(result[0][0] != result[20][0])
        conn.close()


    def test_users_1(self):
        conn = sqlite3.connect('206_APIsAndDBs.sqlite')
        cur = conn.cursor()
        cur.execute('SELECT * FROM Users');
        result = cur.fetchall()
        self.assertTrue(len(result)>=2,"Testing that there are at least 2 distinct users in the Users table")
        conn.close()
    def test_users_2(self):
        conn = sqlite3.connect('206_APIsAndDBs.sqlite')
        cur = conn.cursor()
        cur.execute('SELECT * FROM Users');
        result = cur.fetchall()
        self.assertTrue(len(result)<20,"Testing that there are fewer than 20 users in the users table -- effectively, that you haven't added duplicate users. If you got hundreds of tweets and are failing this, let's talk. Otherwise, careful that you are ensuring that your user id is a primary key!")
        conn.close()
    def test_users_3(self):
        conn = sqlite3.connect('206_APIsAndDBs.sqlite')
        cur = conn.cursor()
        cur.execute('SELECT * FROM Users');
        result = cur.fetchall()
        self.assertTrue(len(result[0])==4,"Testing that there are 4 columns in the Users database")
        conn.close()

class Task3(unittest.TestCase):
    def test_users_info(self):
        self.assertEqual(type(users_info),type([]),"testing that users_info contains a list")
    def test_users_info2(self):
        self.assertEqual(type(users_info[0]),type(("hi","bye")),"Testing that an element in the users_info list is a tuple")

    def test_track_names(self):
        self.assertEqual(type(screen_names),type([]),"Testing that screen_names is a list")
    def test_track_names2(self):
        self.assertEqual(type(screen_names[0]),type(""),"Testing that an element in screen_names list is a string")

    def test_more_rts(self):
        if len(retweets) >= 1:
            self.assertTrue(len(retweets[0])==5,"Testing that a tuple in retweets has 5 fields of info (one for each of the columns in the Tweet table)")
    def test_more_rts2(self):
        self.assertEqual(type(retweets),type([]),"Testing that retweets is a list")
    def test_more_rts3(self):
        if len(retweets) >= 1:
            self.assertTrue(retweets[1][-1]>10, "Testing that one of the retweet # values in the tweets is greater than 10")

    def test_descriptions_fxn(self):
        self.assertEqual(type(favorites),type([]),"Testing that favorites is a list")
    def test_descriptions_fxn2(self):
        self.assertEqual(type(favorites[0]),type(""),"Testing that at least one of the elements in the favorites list is a string, not a tuple or anything else")
    def test_joined_result(self):
        self.assertEqual(type(joined_data[0]),type(("hi","bye")),"Testing that an element in joined_result is a tuple")



if __name__ == "__main__":
    unittest.main(verbosity=2)
