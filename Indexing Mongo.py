{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 3,
   "id": "82a78436-f9e9-4cf3-a1ba-fce94f128e8e",
   "metadata": {},
   "outputs": [],
   "source": [
    "import pymongo\n",
    "\n",
    "client = pymongo.MongoClient(\"mongodb+srv://dbms:dbms2024@cluster0.5byfqtj.mongodb.net/\")\n",
    "\n",
    "db=client.twitter"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "e14ef4b8-15cf-43da-8bed-f83f87870e33",
   "metadata": {},
   "outputs": [],
   "source": [
    "db['retweets_final'].create_index([('main_tweet_id',1)])\n",
    "db['retweets_final'].create_index([('main_tweet_id',1),('fmt_time',-1)])\n",
    "db['retweets_final'].create_index([('user_id',-1)])\n",
    "\n",
    "db.retweets_final.index_information()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "bb686446-932b-4049-8b84-38df99689711",
   "metadata": {},
   "outputs": [],
   "source": [
    "db['tweets_final'].create_index([('user_id',-1)])\n",
    "db['tweets_final'].create_index([('fmt_time',-1)])\n",
    "db['tweets_final'].create_index([('post_id',-1)])\n",
    "db['tweets_final'].create_index([('hashtags',text)])\n",
    "\n",
    "db.tweets_final.index_information()"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
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
   "version": "3.11.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
