import pandas as pd
import numpy as np
import tweepy
import configparser

def search_twitter_info(name_surname_list, config_file):
    # read all the credentials from the config file 
    config = configparser.ConfigParser()
    config.read(config_file)

    api_key = config['twitter']['api_key']
    api_key_secret = config['twitter']['api_key_secret']

    access_token = config['twitter']['access_token']
    access_token_secret = config['twitter']['access_token_secret']

    # authorization of consumer key and consumer secret
    auth = tweepy.OAuthHandler(api_key, api_key_secret)
    
    # set access to user's access key and access secret 
    auth.set_access_token(access_token, access_token_secret)

    # calling the api 
    api = tweepy.API(auth)

    psn = name_surname_list
    twitter_info = {
        'deputy' : psn,
        'user_id' : pd.Series(np.nan),
        'name' : pd.Series(np.nan),
        'screen_name' : pd.Series(np.nan),
        'followers_count' : pd.Series(np.nan),
        'friends_count' : pd.Series(np.nan),
        'statuses_count':pd.Series(np.nan),
        'verified' : pd.Series(np.nan)
    }
    twitter_info = pd.DataFrame.from_dict(twitter_info)
    for i in range(len(psn)):
        user = api.search_users(psn[i])
        if len(user) == 0:
            continue
        else:
            user = user[0]._json
            info = ['id', 'name', 'screen_name','followers_count','friends_count', 'statuses_count', 'verified']
            for n in range(1, 8): 
                twitter_info.iloc[i, n] = user[info[n-1]]

    return twitter_info