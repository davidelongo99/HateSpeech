from hs_functions import get_tweets, remove_usernames_links
import pandas as pd
import time

twitter_veracc = pd.read_csv('twitter_veracc.csv', index_col=0)
all_tweets = pd.DataFrame()

for n in [50, 100, len(twitter_veracc)]:
    df = twitter_veracc[:n]
    all_tweets_n = get_tweets(df.screen_name, 'config.ini')
    time.sleep(600)  # wait 10 minutes (too many requests error)
    all_tweets = pd.concat([all_tweets, all_tweets_n],
                           axis=0, ignore_index=True)

# save all the Twitter storyline of politicians
all_tweets.to_csv('all_tweets.csv')

# filter by starting date of the XIX legislature
all_tweets = all_tweets[all_tweets['Time'] > '2022-10-13 00:00:00+00:00']

# remove @usernames and links
all_tweets['Tweet'] = all_tweets['Tweet'].apply(remove_usernames_links)

# save only tweet published since the beginning of the legislature XIX
all_tweets.to_csv('all_tweets_19L.csv')


