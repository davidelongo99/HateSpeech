from hs_functions import check_replys
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



