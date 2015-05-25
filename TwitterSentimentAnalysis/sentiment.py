from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from pymongo import MongoClient
from textblob import TextBlob
import statistics
import json
import re
import sys
import markup


access_token = "3166078670-kUTXvUAHyaddLaoWiibqT4aSYKhLAS2zy1I7pos"
access_token_secret = "ZcOHVTe4PwdDCmjAdmwGfepyJWI6eXpRouCwHVvaPyFLi"
consumer_key = "fFStHXn6NiOvunlkYF1ojGn8M"
consumer_secret = "4KcD7FaW8OvSS8SHaiEkthohElPBY1NOslVkR8owzNQjLZ8T6Q"



class StdOutListener(StreamListener):


    def __init__(self, api=None):
        super(StdOutListener, self).__init__()
        self.num_of_tweets = 0
        open('tweets.txt', 'w').close()
        
    def on_connect(self):
        print("You're connected to the streaming server.")
        print("\n")   
    
    def on_data(self, data):
        client = MongoClient()
        db = client.tweetdb
        datajson = json.loads(data)
        
        x =  datajson['text']
        munged={}
        munged['id'] =  datajson['id']
        munged['created_at'] = datajson['created_at']
        munged['text'] = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",x).split())
        munged['location'] = datajson['user']['location']
        munged['time_zone'] = datajson['user']['time_zone']
        
        
        json_data = json.dumps(munged)
        db.iphonetweets.insert_one(json.loads(json_data))
        
        with open('tweets.txt', 'a') as tf:
            tf.write(json_data)
        
        self.num_of_tweets = self.num_of_tweets + 1
        if self.num_of_tweets <100:
            return True
        else:
            tf.close()
            return False

    def on_error(self, status):
        print status

    

if __name__ == '__main__':


    sum = 0.0
    alist = []
    positive = []
    negative = []
    neutral = []
    client = MongoClient()
    db = client.tweetdb
    for iphonetweet in db.iphonetweets.find():
        tweet = TextBlob(iphonetweet["text"])
        if tweet.sentiment.subjectivity != 0.0:
            alist.append(tweet.sentiment.polarity)
        if tweet.sentiment.polarity>0:
            positive.append(tweet.sentiment.polarity)
        elif  tweet.sentiment.polarity<0:  
            negative.append(tweet.sentiment.polarity)
        else:
            neutral.append(tweet.sentiment.polarity)


    title = "Sentiment Analysis"
    header = "Twitter Sentiment Analysis"
    footer = "This is the end."
    styles = ( 'layout.css', 'alt.css', 'images.css' )

    page = markup.page( )
    page.init( css=styles, title=title, header=header, footer=footer )
    page.br( )

    paragraphs = (statistics.mean(alist))

    page.h1( paragraphs )

    page.img( width=30, height=30, alt='Fantastic!', src='1.png' )
    page.br( )
    page.img( width=30, height=30, alt='Fantastic!', src='2.png' )
    page.br( )
    page.img( width=30, height=30, alt='Fantastic!', src='3.png' )
    page.br( )
    page.img( width=30, height=30, alt='Fantastic!', src='4.png' )
    page.br( )
    page.img( width=30, height=30, alt='Fantastic!', src='5.png' )
    page.br( )

    with open("Output.html", "w") as outputFile:
        print >>outputFile,page  
    
