from transformers import pipeline
from hs_functions import remove_usernames_links, check_replys
import pandas as pd
import json
import time
import argparse

parser = argparse.ArgumentParser(
    description="""The script collect replies to tweets published by politicians""")
parser.add_argument("week", type=int,
                    help="week number of the experiment")
parser.add_argument("start_date", type=str,
                    help="Starting date of replies collection, e.g. '2023-01-23 00:00:00+00:00' ")
parser.add_argument("end_date", type=str,
                    help="Ending date of replies collection, e.g. '2023-01-23 00:00:00+00:00' ")

args = parser.parse_args()
week = args.week
start_date = args.start_date
end_date = args.end_date


all_tweets_19L = pd.read_csv('all_tweets_19L.csv', index_col=0)
tweets_week = all_tweets_19L[(all_tweets_19L['Time'] >= start_date) &
                             (all_tweets_19L['Time'] < end_date)]

all_replies = dict()

for i in range(len(tweets_week)):
    if i % 250 == 0:
        time.sleep(900)
        tweet = tweets_week.iloc[i, 0]
        replies = check_replys(tweet)
        all_replies[tweet] = replies
    else:
        tweet = tweets_week.iloc[i, 0]
        replies = check_replys(tweet)
        all_replies[tweet] = replies

# save dictionary as json file
to_json = {str(k): v for k, v in all_replies.items()}
with open(f"data_collection_w{week}/replies_w{week}.json", "w") as wf:
    json.dump(to_json, wf, indent=4)

# save dictionary as csv file
replies_df = pd.DataFrame(columns=['source_tweet', 'reply'])
for k in all_replies.keys():
    replies = all_replies[k]
    for reply in replies:
        new_row = [k, reply]
        replies_df.loc[len(replies_df)] = new_row

replies_df.to_csv(f"data_collection_w{week}/replies_w{week}.csv")

replies_df['reply'] = replies_df['reply'].apply(remove_usernames_links)
header_list = ['source_tweet', 'reply', 'Hate_score', 'NonHate_score']
replies_df = replies_df.reindex(columns=header_list)

classifier = pipeline("text-classification",
                      model='MilaNLProc/hate-ita', top_k=2)

for i in range(len(replies_df)):
    tweet = replies_df.iloc[i, 1]
    if type(tweet) is not str:
        continue
    else:
        prediction = classifier(tweet)
        if prediction[0][0]['label'] == 'non-hateful':
            replies_df.iloc[i, 3] = prediction[0][0]['score']
            replies_df.iloc[i, 2] = prediction[0][1]['score']
        else:
            replies_df.iloc[i, 2] = prediction[0][0]['score']
            replies_df.iloc[i, 3] = prediction[0][1]['score']

replies_df.to_csv(f'data_collection_w{week}/replies_w{week}_hs.csv')

hs_mean_bytweet = replies_df.groupby("source_tweet")["Hate_score"].mean()

tweet_hs_received = hs_mean_bytweet.to_frame().reset_index().sort_values(
    by='Hate_score', axis=0, ascending=False).rename(
    columns={'source_tweet': 'Tweet_ID', 'Hate_score': 'hs_received'})
tweet_hs_received

tweets_week_hsr = pd.merge(tweets_week, tweet_hs_received, on='Tweet_ID')
tweets_week_hsr_2 = tweets_week_hsr.groupby('User')['hs_received'].mean()
tweets_week_hsr_3 = tweets_week_hsr_2.to_frame().reset_index().sort_values(by='hs_received', axis=0, ascending=False).rename(
    columns={'User': 'screen_name', 'hs_received': f'hs_received_w{week}'})
# tweet of week1 and hate speech received
tweets_week_hsr_3.to_csv(f'data_collection_w{week}/tweets_w{week}_hsr.csv')


twitter_veracc = pd.read_csv('twitter_veracc.csv')
tweets_week_hsr_4 = pd.merge(twitter_veracc[[
                             'screen_name', 'gender', 'parliamentary_group', 'chamber']], tweets_week_hsr_3, on='screen_name')
tweets_week_hsr_4.to_csv(f'data_collection_w{week}/hsr_w{week}_depsen.csv')
