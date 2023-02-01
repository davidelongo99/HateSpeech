from hs_functions import get_tweets, remove_usernames_links
from transformers import pipeline
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

# rename columns
header_list = ['Tweet_ID', 'Time', 'User',
               'Tweet', 'Hate_score', 'NonHate_score']
all_tweets_v4 = all_tweets.reindex(columns=header_list)

# apply hate speech classifier to each tweet
classifier = pipeline("text-classification",
                      model='MilaNLProc/hate-ita', top_k=2)

for i in range(len(all_tweets_v4)):
    # tweet column
    tweet = all_tweets_v4.iloc[i, 3]
    if type(tweet) is not str:
        continue
    else:
        prediction = classifier(tweet)
        # the output order change based on assigned class
        if prediction[0][0]['label'] == 'non-hateful':
            all_tweets_v4.iloc[i, 5] = prediction[0][0]['score']
            all_tweets_v4.iloc[i, 4] = prediction[0][1]['score']
        else:
            all_tweets_v4.iloc[i, 4] = prediction[0][0]['score']
            all_tweets_v4.iloc[i, 5] = prediction[0][1]['score']

# save all the tweets published in the current legislature with associated hate speech value.
all_tweets_v4.to_csv('all_tweets_19L_hs.csv')
