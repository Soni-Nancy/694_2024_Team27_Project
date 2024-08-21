{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {},
   "outputs": [],
   "source": [
    "import json\n",
    "import pandas\n",
    "import time\n",
    "import ast\n",
    "import os\n",
    "from time import strftime\n",
    "from time import gmtime\n",
    "from datetime import datetime\n",
    "import pymongo\n",
    "from pymongo import MongoClient"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {},
   "outputs": [],
   "source": [
    "client = MongoClient(\"mongodb+srv://priyankanagasuri:**********@cluster1.dfkwly1.mongodb.net/\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "metadata": {},
   "outputs": [],
   "source": [
    "db = client.get_database(\"twitter_db\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "metadata": {},
   "outputs": [],
   "source": [
    "# check if the collection exists\n",
    "if \"tweets_data\" in db.list_collection_names():\n",
    "    db.drop_collection(\"tweets_data\")\n",
    "else:\n",
    "    print('The collection does not exist.')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Adding hashtags present in the tweet to the \"tweets_final\" collection\n",
    "def add_hash(data):\n",
    "    hashtags=[]\n",
    "    if data[\"truncated\"]:\n",
    "        hash1=data[\"extended_tweet\"][\"entities\"][\"hashtags\"]\n",
    "        for i in hash1:\n",
    "            hashtags.append(i[\"text\"])\n",
    "    else:\n",
    "        hash1=data[\"entities\"][\"hashtags\"]\n",
    "        for i in hash1:\n",
    "            hashtags.append(i[\"text\"])\n",
    "    return hashtags"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Calculating and adding priority rate to the \"tweets_final\" collection\n",
    "def get_engagement(data):\n",
    "    active_rate=data[\"favorite_count\"]+data[\"retweet_count\"]+data[\"quote_count\"]+data[\"reply_count\"]\n",
    "    active_rate=round(active_rate*1000/(data[\"user\"][\"followers_count\"]+1),4)\n",
    "    return active_rate"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Total Time 00:49:18\n"
     ]
    }
   ],
   "source": [
    "\n",
    "# Loading the corona-out-2 data file\n",
    "with open(\"corona-out-2\", \"r\") as f1:\n",
    "    strt=time.time()\n",
    "    i=0\n",
    "    j=0\n",
    "    lists=[]\n",
    "    for line in f1:\n",
    "        i+=1\n",
    "        try:\n",
    "            data = json.loads(line)\n",
    "            if (data['text'].startswith('RT')):\n",
    "                #adding retweet in retweets_finial collections\n",
    "                if (db.retweets_final.count_documents({\"post_id\":data['id_str']})==0 and \"retweeted_status\" in data.keys()):\n",
    "                    temp1={\"Time_stamp\":data[\"created_at\"],\"post_id\":data['id_str'],\"user_id\":data[\"user\"][\"id_str\"],\"Account_name\":data['user']['name'],\"retweets_count\":data[\"retweet_count\"],\n",
    "                      \"Likes\":data['favorite_count'],\"tweet\":data['text'],\"main_tweet_id\":data['retweeted_status']['id_str'],\n",
    "                         \"comments_count\":data[\"reply_count\"], \"quotes_count\":data[\"quote_count\"]}\n",
    "                    dt = datetime.strptime(data[\"created_at\"], \"%a %b %d %H:%M:%S %z %Y\")\n",
    "                    temp1[\"fmt_time\"] = float(dt.timestamp())\n",
    "                    db.retweets_final.insert_one(temp1)\n",
    "                \n",
    "                #adding quoted tweet in tweets collection\n",
    "                if (data['is_quote_status'] and db.tweets_final.count_documents({\"post_id\":data['quoted_status']['id_str']})==0 and \"quoted_status\" in data.keys()):    #check if tweet is quoted\n",
    "                    temp={\"Time_stamp\":data[\"quoted_status\"][\"created_at\"],\"post_id\":data['quoted_status']['id_str'],  \"user_id\":data['quoted_status']['user']['id_str'], \"Account_Name\":data['quoted_status']['user']['name'],\n",
    "                          \"retweets_count\":data['quoted_status'][\"retweet_count\"],   \"Likes\":data['quoted_status']['favorite_count'],\n",
    "                          \"quoted_id\": \"NULL\",  \"comments_count\":data[\"quoted_status\"][\"reply_count\"], \"quotes_count\":data[\"quoted_status\"][\"quote_count\"]}\n",
    "                    temp[\"tweet\"]=data['quoted_status']['text'] if not data[\"quoted_status\"][\"truncated\"] else data[\"quoted_status\"][\"extended_tweet\"][\"full_text\"]\n",
    "                    temp[\"hashtags\"]=add_hash(data[\"quoted_status\"])\n",
    "                    temp[\"priority\"]=get_engagement(data[\"quoted_status\"])\n",
    "                    dt = datetime.strptime(data[\"quoted_status\"][\"created_at\"], \"%a %b %d %H:%M:%S %z %Y\")\n",
    "                    temp[\"fmt_time\"] = float(dt.timestamp())\n",
    "                    db.tweets_final.insert_one(temp)\n",
    "                \n",
    "                #adding retweeted tweet in tweets collection\n",
    "                if (db.tweets_final.count_documents({\"post_id\":data['retweeted_status']['id_str']})==0 and \"retweeted_status\" in data.keys()):\n",
    "                    temp={\"Time_stamp\":data[\"retweeted_status\"][\"created_at\"],\"post_id\":data['retweeted_status']['id_str'],\"user_id\":data['retweeted_status']['user']['id_str'],\"Account_Name\":data['retweeted_status']['user']['name'],\n",
    "                          \"retweets_count\":data['retweeted_status'][\"retweet_count\"],\"Likes\":data['retweeted_status']['favorite_count'],\n",
    "                          \"tweet\":data['retweeted_status']['text'],\"quoted_id\": data['quoted_status']['id_str'] if data['is_quote_status'] else \"NULL\",\n",
    "                         \"comments_count\":data[\"retweeted_status\"][\"reply_count\"], \"quotes_count\":data[\"retweeted_status\"][\"quote_count\"]}\n",
    "                    temp[\"tweet\"]=data['retweeted_status']['text'] if not data[\"retweeted_status\"][\"truncated\"] else data[\"retweeted_status\"][\"extended_tweet\"][\"full_text\"]\n",
    "                    temp[\"hashtags\"]=add_hash(data[\"retweeted_status\"])                    \n",
    "                    temp[\"priority\"]=get_engagement(data[\"retweeted_status\"])\n",
    "                    dt = datetime.strptime(data[\"retweeted_status\"][\"created_at\"], \"%a %b %d %H:%M:%S %z %Y\")\n",
    "                    temp[\"fmt_time\"] = float(dt.timestamp())\n",
    "                    db.tweets_final.insert_one(temp)\n",
    "                \n",
    "            else:\n",
    "                 #adding quoted tweet in tweets collection\n",
    "                if (data['is_quote_status']):    #check if tweet is quoted\n",
    "                    if(db.tweets_final.count_documents({\"post_id\":data['quoted_status']['id_str']})==0 and \"quoted_status\" in data.keys()):   #check if present in data\n",
    "                        temp={\"Time_stamp\":data[\"quoted_status\"][\"created_at\"],\"post_id\":data['quoted_status']['id_str'],\"user_id\":data['quoted_status']['user']['id_str'],\"Account_Name\":data['quoted_status']['user']['name'],\n",
    "                          \"retweets_count\":data['quoted_status'][\"retweet_count\"],\"Likes\":data['quoted_status']['favorite_count'],\n",
    "                          \"quoted_id\": \"NULL\",\"comments_count\":data[\"quoted_status\"][\"reply_count\"], \"quotes_count\":data[\"quoted_status\"][\"quote_count\"]}\n",
    "                        temp[\"tweet\"]=data['quoted_status']['text'] if not data[\"quoted_status\"][\"truncated\"] else data[\"quoted_status\"][\"extended_tweet\"][\"full_text\"]\n",
    "                        temp[\"hashtags\"]=add_hash(data[\"quoted_status\"])\n",
    "                        temp[\"priority\"]=get_engagement(data[\"quoted_status\"])\n",
    "                        dt = datetime.strptime(data[\"quoted_status\"][\"created_at\"], \"%a %b %d %H:%M:%S %z %Y\")\n",
    "                        temp[\"fmt_time\"] = float(dt.timestamp())\n",
    "                        db.tweets_final.insert_one(temp)\n",
    "                \n",
    "                #adding simple tweet in tweets collection\n",
    "                if (db.tweets_final.count_documents({\"post_id\":data['id_str']})==0):\n",
    "                    temp={\"Time_stamp\":data[\"created_at\"],\"post_id\":data['id_str'],\"user_id\":data['user']['id_str'],\"retweets_count\":data[\"retweet_count\"],\"Account_Name\":data['user']['name'],\n",
    "                      \"Likes\":data['favorite_count'],\"quoted_id\": data['quoted_status']['id_str'] if data['is_quote_status'] else \"NULL\",\n",
    "                       \"comments_count\":data[\"reply_count\"], \"quotes_count\":data[\"quote_count\"]}\n",
    "                    temp[\"tweet\"]=data['text'] if not data[\"truncated\"] else data[\"extended_tweet\"][\"full_text\"]\n",
    "                    temp[\"hashtags\"]=add_hash(data)\n",
    "                    temp[\"priority\"]=get_engagement(data)\n",
    "                    dt = datetime.strptime(data[\"created_at\"], \"%a %b %d %H:%M:%S %z %Y\")\n",
    "                    temp[\"fmt_time\"] = float(dt.timestamp())\n",
    "                    db.tweets_final.insert_one(temp)\n",
    "        except:\n",
    "            j+=1\n",
    "            lists.append(line)\n",
    "            continue\n",
    "    end=time.time()\n",
    "    print(\"Total Time\",strftime(\"%H:%M:%S\", gmtime(end-strt)))\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Total Time 04:59:22\n"
     ]
    }
   ],
   "source": [
    "# Loading the corona-out-3 data file\n",
    "with open(\"corona-out-3\", \"r\") as f1:\n",
    "    strt=time.time()\n",
    "    i=0\n",
    "    j=0\n",
    "    lists=[]\n",
    "    for line in f1:\n",
    "        i+=1\n",
    "        try:\n",
    "            data = json.loads(line)\n",
    "            if (data['text'].startswith('RT')):\n",
    "                #adding retweet in retweets collections\n",
    "                if (db.retweets_final.count_documents({\"post_id\":data['id_str']})==0 and \"retweeted_status\" in data.keys()):\n",
    "                    temp1={\"Time_stamp\":data[\"created_at\"],\"post_id\":data['id_str'],\"user_id\":data[\"user\"][\"id_str\"],\"Account_name\":data['user']['name'],\"retweets_count\":data[\"retweet_count\"],\n",
    "                      \"Likes\":data['favorite_count'],\"tweet\":data['text'],\"main_tweet_id\":data['retweeted_status']['id_str'],\n",
    "                         \"comments_count\":data[\"reply_count\"], \"quotes_count\":data[\"quote_count\"]}\n",
    "                    dt = datetime.strptime(data[\"created_at\"], \"%a %b %d %H:%M:%S %z %Y\")\n",
    "                    temp1[\"fmt_time\"] = float(dt.timestamp())\n",
    "                    db.retweets_final.insert_one(temp1)\n",
    "                \n",
    "                #adding quoted tweet in tweets collection\n",
    "                if (data['is_quote_status'] and db.tweets_final.count_documents({\"post_id\":data['quoted_status']['id_str']})==0 and \"quoted_status\" in data.keys()):    #check if tweet is quoted\n",
    "                    temp={\"Time_stamp\":data[\"quoted_status\"][\"created_at\"],\"post_id\":data['quoted_status']['id_str'],  \"user_id\":data['quoted_status']['user']['id_str'], \"Account_Name\":data['quoted_status']['user']['name'],\n",
    "                          \"retweets_count\":data['quoted_status'][\"retweet_count\"],   \"Likes\":data['quoted_status']['favorite_count'],\n",
    "                          \"quoted_id\": \"NULL\",  \"comments_count\":data[\"quoted_status\"][\"reply_count\"], \"quotes_count\":data[\"quoted_status\"][\"quote_count\"]}\n",
    "                    temp[\"tweet\"]=data['quoted_status']['text'] if not data[\"quoted_status\"][\"truncated\"] else data[\"quoted_status\"][\"extended_tweet\"][\"full_text\"]\n",
    "                    temp[\"hashtags\"]=add_hash(data[\"quoted_status\"])\n",
    "                    temp[\"priority\"]=get_engagement(data[\"quoted_status\"])\n",
    "                    dt = datetime.strptime(data[\"quoted_status\"][\"created_at\"], \"%a %b %d %H:%M:%S %z %Y\")\n",
    "                    temp[\"fmt_time\"] = float(dt.timestamp())\n",
    "                    db.tweets_final.insert_one(temp)\n",
    "                \n",
    "                #adding retweeted tweet in tweets collection\n",
    "                if (db.tweets_final.count_documents({\"post_id\":data['retweeted_status']['id_str']})==0 and \"retweeted_status\" in data.keys()):\n",
    "                    temp={\"Time_stamp\":data[\"retweeted_status\"][\"created_at\"],\"post_id\":data['retweeted_status']['id_str'],\"user_id\":data['retweeted_status']['user']['id_str'],\"Account_Name\":data['retweeted_status']['user']['name'],\n",
    "                          \"retweets_count\":data['retweeted_status'][\"retweet_count\"],\"Likes\":data['retweeted_status']['favorite_count'],\n",
    "                          \"tweet\":data['retweeted_status']['text'],\"quoted_id\": data['quoted_status']['id_str'] if data['is_quote_status'] else \"NULL\",\n",
    "                         \"comments_count\":data[\"retweeted_status\"][\"reply_count\"], \"quotes_count\":data[\"retweeted_status\"][\"quote_count\"]}\n",
    "                    temp[\"tweet\"]=data['retweeted_status']['text'] if not data[\"retweeted_status\"][\"truncated\"] else data[\"retweeted_status\"][\"extended_tweet\"][\"full_text\"]\n",
    "                    temp[\"hashtags\"]=add_hash(data[\"retweeted_status\"])                    \n",
    "                    temp[\"priority\"]=get_engagement(data[\"retweeted_status\"])\n",
    "                    dt = datetime.strptime(data[\"retweeted_status\"][\"created_at\"], \"%a %b %d %H:%M:%S %z %Y\")\n",
    "                    temp[\"fmt_time\"] = float(dt.timestamp())\n",
    "                    db.tweets_final.insert_one(temp)\n",
    "                \n",
    "            else:\n",
    "                 #adding quoted tweet in tweets collection\n",
    "                if (data['is_quote_status']):    #check if tweet is quoted\n",
    "                    if(db.tweets_final.count_documents({\"post_id\":data['quoted_status']['id_str']})==0 and \"quoted_status\" in data.keys()):   #check if present in data\n",
    "                        temp={\"Time_stamp\":data[\"quoted_status\"][\"created_at\"],\"post_id\":data['quoted_status']['id_str'],\"user_id\":data['quoted_status']['user']['id_str'],\"Account_Name\":data['quoted_status']['user']['name'],\n",
    "                          \"retweets_count\":data['quoted_status'][\"retweet_count\"],\"Likes\":data['quoted_status']['favorite_count'],\n",
    "                          \"quoted_id\": \"NULL\",\"comments_count\":data[\"quoted_status\"][\"reply_count\"], \"quotes_count\":data[\"quoted_status\"][\"quote_count\"]}\n",
    "                        temp[\"tweet\"]=data['quoted_status']['text'] if not data[\"quoted_status\"][\"truncated\"] else data[\"quoted_status\"][\"extended_tweet\"][\"full_text\"]\n",
    "                        temp[\"hashtags\"]=add_hash(data[\"quoted_status\"])\n",
    "                        temp[\"priority\"]=get_engagement(data[\"quoted_status\"])\n",
    "                        dt = datetime.strptime(data[\"quoted_status\"][\"created_at\"], \"%a %b %d %H:%M:%S %z %Y\")\n",
    "                        temp[\"fmt_time\"] = float(dt.timestamp())\n",
    "                        db.tweets_final.insert_one(temp)\n",
    "                \n",
    "                #adding simple tweet in tweets collection\n",
    "                if (db.tweets_final.count_documents({\"post_id\":data['id_str']})==0):\n",
    "                    temp={\"Time_stamp\":data[\"created_at\"],\"post_id\":data['id_str'],\"user_id\":data['user']['id_str'],\"retweets_count\":data[\"retweet_count\"],\"Account_Name\":data['user']['name'],\n",
    "                      \"Likes\":data['favorite_count'],\"quoted_id\": data['quoted_status']['id_str'] if data['is_quote_status'] else \"NULL\",\n",
    "                       \"comments_count\":data[\"reply_count\"], \"quotes_count\":data[\"quote_count\"]}\n",
    "                    temp[\"tweet\"]=data['text'] if not data[\"truncated\"] else data[\"extended_tweet\"][\"full_text\"]\n",
    "                    temp[\"hashtags\"]=add_hash(data)\n",
    "                    temp[\"priority\"]=get_engagement(data)\n",
    "                    dt = datetime.strptime(data[\"created_at\"], \"%a %b %d %H:%M:%S %z %Y\")\n",
    "                    temp[\"fmt_time\"] = float(dt.timestamp())\n",
    "                    db.tweets_final.insert_one(temp)\n",
    "        except:\n",
    "            j+=1\n",
    "            lists.append(line)\n",
    "            continue\n",
    "    end=time.time()\n",
    "    print(\"Total Time\",strftime(\"%H:%M:%S\", gmtime(end-strt)))\n",
    "    print(\"Number of errors\",j)\n",
    "    print(list)"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.12.3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
