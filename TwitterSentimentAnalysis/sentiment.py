from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from pymongo import MongoClient
from textblob import TextBlob
import statistics
import json
import re
from collections import Counter
import sys
import markup
import numpy as np
import matplotlib.pyplot as plt
from pylab import *
from pytagcloud import create_tag_image, make_tags
from pytagcloud.lang.counter import get_tag_counts
import operator
import obo
import webbrowser
import random
from random import randrange
from textblob.en import positive


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
        print json_data
       
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

    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)
    stream.filter(track=['iphone,iPhone'],languages=['en'])
    sum = 0.0
    sum1 = 0.0
    layout = 3
    background_color = (255, 255, 255)
    max_word_size = 80
    max_words = 180
    width = 1280
    height = 800
    my_text=''
    f = open('stopwords.txt', 'rb')
    stop_words = [line.strip() for line in f]
    tweets_words = ['iphone', 'iPhone', 'amp']
    alist = []
    tweets = []
    horrible = []
    bad = []
    awesome = []
    good = []
    positive = []
    negative = []
    neutral = []
    tecPositive = {'screen':0,'wifi':0,'camera':0,'ios':0,'bluetooth':0,'16gb':0,'iphonegames':0,'5c':0,'5s':0}
    tecNegative = {'screen':0,'wifi':0,'camera':0,'ios':0,'bluetooth':0,'16gb':0,'iphonegames':0,'5c':0,'5s':0}
    tecLabels = ['screen','wifi','camera','ios','bluetooth','16gb','iphonegames','5c','5s']
    client = MongoClient()
    db = client.tweetdb
    for iphonetweet in db.iphonetweets.find():
        tweet = TextBlob(iphonetweet["text"])
        sum1 = sum1 + tweet.word_counts['screen']
        if tweet.sentiment.subjectivity != 0.0:
            tweets.append(iphonetweet["text"])
            important_words = iphonetweet['text'].lower()
            my_text += important_words
            alist.append(tweet.sentiment.polarity)
            if tweet.sentiment.polarity>0:

                for word in tecLabels:
                    if tweet.word_counts[word]>0:
                        tecPositive[word] = tecPositive[word]+1
                
                positive.append(tweet.sentiment.polarity)
                if tweet.sentiment.polarity<0.5:
                    good.append(tweet.sentiment.polarity)
                else:
                    awesome.append(tweet.sentiment.polarity)   
            elif  tweet.sentiment.polarity<0:

                for word in tecLabels:
                    if tweet.word_counts[word]>0:
                        tecNegative[word] = tecNegative[word]+1
                
                negative.append(tweet.sentiment.polarity)
                if tweet.sentiment.polarity> -0.5:
                    bad.append(tweet.sentiment.polarity)
                else:
                    horrible.append(tweet.sentiment.polarity)
            else:
                neutral.append(tweet.sentiment.polarity)
    total= len(alist)

    print tecPositive
    print tecNegative
   
    words = my_text.split()
    counts = Counter(words)
    for word in stop_words:
        del counts[word]
    for word in tweets_words:
        del counts[word]
        

    final = counts.most_common(max_words)
    max_count = max(final, key=operator.itemgetter(1))[1]
    final = [(name, count / float(max_count))for name, count in final]
    tags = make_tags(final, maxsize=max_word_size)
    create_tag_image(tags, 'cloud_large.png', size=(width, height), layout=layout, fontname='Lobster', background = background_color)
    
    mean = statistics.mean(alist)
    mode = statistics.mode(alist)
    median = statistics.median(alist)
    standard_deviation = statistics.stdev(alist, xbar=None)
    
    print "mean: " + str(mean)
    print "mode: " + str(mode)
    print "median: " + str(median)
    print "standatd_deviation: " + str(standard_deviation)
    
    people = ('Positive', 'Negative', 'Neutral')
    y_pos = np.arange(len(people))
    sizes=[len(positive)/float(total), len(negative)/float(total), len(neutral)/float(total)]
  
    plt.barh(y_pos, sizes, alpha=0.4, align='center')
    plt.yticks(y_pos, people)
    plt.title('Product Sentiment Analysis')
    savefig('barchart.png')
    
    plt.clf()
    
    
    labels = ['Positive', 'Negative', 'Neutral']
    colors = ['blue', 'green', 'yellow']
   
    sizes=[len(positive)/float(total), len(negative)/float(total), len(neutral)/float(total)]
    plt.pie(sizes, labels = labels, colors=colors, autopct='%1.1f%%', shadow=True)
    plt.axis('equal')
    savefig('piechart.png') 
   
    plt.clf()

    n_groups = 9
    positives = []
    negatives = []

    for word in tecLabels:
        total = tecPositive[word]+tecNegative[word]
        if total == 0:
            continue
        positives.append(tecPositive[word]*100/total)
        negatives.append(tecNegative[word]*100/total)


    fig, ax = plt.subplots()

    index = np.arange(n_groups)
    bar_width = 0.35

    opacity = 0.4
    error_config = {'ecolor': '0.3'}

    rects1 = plt.bar(index, positives, bar_width,
                 alpha=opacity,
                 color='b',
                 error_kw=error_config,
                 label='Positive')

    rects2 = plt.bar(index + bar_width, negatives, bar_width,
                 alpha=opacity,
                 color='r',
                 error_kw=error_config,
                 label='Negative')

    plt.ylabel('Sentiments')
    plt.title('Technical Details')
    plt.xticks(index + bar_width, tecLabels)
    plt.legend()

    plt.tight_layout()
    
    savefig('details.png')
   
    f = open('Output.html','w')

    message = """<!DOCTYPE html>
<html lang="en">
<head>
<title>Twitter Sentiment Analysis</title>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet"
    href="http://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css">
<script
    src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
<script
    src="http://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/js/bootstrap.min.js"></script>
    <style>
   
    

    


    </style>
</head>

<body>

    <nav class="navbar navbar-inverse">
        <div class="container-fluid">
            <div class="navbar-header">
                <a class="navbar-brand" href="#">Twitter Sentiment Analysis</a>
            </div>
        </div>
    </nav>
    <div class="container-fluid">
        <div class="row">
        <div class="col-lg-4">
        <h2>Top 10 tweets</h2>
            <ul class="list-group">
        <li class="list-group-item">""" + tweets[randrange(0,len(tweets)-1)]+"""</li>
        <li class="list-group-item">""" + tweets[randrange(0,len(tweets)-1)]+"""</li>
        <li class="list-group-item">""" + tweets[randrange(0,len(tweets)-1)]+"""</li>
        <li class="list-group-item">""" + tweets[randrange(0,len(tweets)-1)]+"""</li>
        <li class="list-group-item">""" + tweets[randrange(0,len(tweets)-1)]+"""</li>
        <li class="list-group-item">""" + tweets[randrange(0,len(tweets)-1)]+"""</li>
        <li class="list-group-item">""" + tweets[randrange(0,len(tweets)-1)]+"""</li>
        <li class="list-group-item">""" + tweets[randrange(0,len(tweets)-1)]+"""</li>
        <li class="list-group-item">""" + tweets[randrange(0,len(tweets)-1)]+"""</li>
        <li class="list-group-item">""" + tweets[randrange(0,len(tweets)-1)]+"""</li>
            </ul>
        </div>
        <div class="col-lg-4">
            <img src="barchart.png" class="img-responsive">
            </div>
            <div class="col-lg-2">
            
            </div>
            <div class="col-lg-2" style="height:50px;">
                <ul class="list-group list-special">
                    <li class="list-group-item row">
                    <div class="col-md-6">
                    <img src="iphone.png">
                    </div>
                    <div class="col-md-6">
                    </br>
                    </br>
                    <h4>Iphone</h4>
                    </div>
                    </li>
                    <li class="list-group-item row">
                    <div class="col-md-6">
                    <img src="twitter_bird.png">
                    </div>
                    <div class="col-md-6">
                    </br>
                    </br>
                    <h4>""" + str(db.iphonetweets.count()) + """</h4>
                    </div>
                    </li>
                    <li class="list-group-item row">
                    <div class="col-md-6">
                    <img src="5.jpg">
                    </div>
                    <div class="col-md-6">
                    </br>
                    </br>
                    <h4>""" + str(len(horrible)) + """</h4>
                    </div>
                    </li>
                    <li class="list-group-item row">
                    <div class="col-md-6">
                    <img src="4.jpg">
                    </div>
                    <div class="col-md-6">
                    </br>
                    </br>
                    <h4>""" + str(len(bad)) + """</h4>
                    </div>
                    </li>
                    <li class="list-group-item row">
                    <div class="col-md-6">
                    <img src="3.jpg">
                    </div>
                    <div class="col-md-6">
                    </br>
                    </br>
                    <h4>""" + str(len(neutral)) + """</h4>
                    </div>
                    </li>
                    <li class="list-group-item row">
                    <div class="col-md-6">
                    <img src="2.jpg">
                    </div>
                    <div class="col-md-6">
                    </br>
                    </br>
                    <h4>""" + str(len(good)) + """</h4>
                    </div>
                    </li>
                    <li class="list-group-item row">
                    <div class="col-md-6">
                    <img src="1.jpg">
                    </div>
                    <div class="col-md-6">
                    </br>
                    </br>
                    <h4>""" + str(len(awesome)) + """</h4>
                    </div>
                    </li>  
                    </ul>
                </div>
           
            </div>
            <div class="row">
            <div class="col-lg-4">
            <img src="cloud_large.png" class="img-responsive">
            </div>
            
            <div class="row">
            <div class="col-lg-4">
            <img src="details.png" class="img-responsive">
            </div>

            </div>
    </div>
</body>
</html>"""

    f.write(message)
    f.close()
    
