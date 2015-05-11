from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from pymongo import MongoClient
import json

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
        trimmed={}
        trimmed['id'] =  datajson['id']
        trimmed['created_at'] = datajson['created_at']
        trimmed['text'] = datajson['text']
        trimmed['location'] = datajson['user']['location']
        trimmed['time_zone'] = datajson['user']['time_zone']
        
        
        json_data = json.dumps(trimmed)
        db.iphonetweets.insert(json.loads(json_data))
        
        print json_data
        with open('tweets.txt', 'a') as tf:
            tf.write(data)
        
        self.num_of_tweets = self.num_of_tweets + 1
        if self.num_of_tweets <1:
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
    stream.filter(track=['iphone'],languages=['en'])
    
    