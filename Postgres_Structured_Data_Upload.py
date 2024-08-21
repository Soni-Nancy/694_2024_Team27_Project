{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "1734a355",
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\n",
    "import numpy as np\n",
    "import ast\n",
    "import decimal\n",
    "import json\n",
    "from datetime import datetime\n",
    "from psycopg2 import connect, sql\n",
    "import os"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "a49f9a99",
   "metadata": {},
   "outputs": [],
   "source": [
    "pd.set_option('display.max_rows', 3000)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "id": "db3b691a",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Connect to the PostgreSQL database\n",
    "conn = connect(\n",
    "    host=\"localhost\",\n",
    "    database=\"postgres\",\n",
    "    user=\"postgres\",\n",
    "    password=\"******\"\n",
    ")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "id": "3cf58749",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Open a cursor to perform database operations\n",
    "cur = conn.cursor()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "id": "01bed301",
   "metadata": {},
   "outputs": [],
   "source": [
    "def create_table(file_path, table_name):\n",
    "\n",
    "    # check if the table exists\n",
    "    cur.execute(\"SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name=%s)\", (table_name,))\n",
    "    table_exists = cur.fetchone()[0]\n",
    "\n",
    "    # if the table exists, drop it\n",
    "    if table_exists:\n",
    "        cur.execute(\"DROP TABLE {}\".format(table_name))\n",
    "        conn.commit()\n",
    "        print(\"Table dropped successfully\")\n",
    "    \n",
    "    # open the SQL script file and read the contents\n",
    "    with open(file_path, 'r') as f:\n",
    "        query = f.read()\n",
    "    \n",
    "    # execute the SQL commands in the script file\n",
    "    cur.execute(query)\n",
    "    conn.commit()\n",
    "    print(\"Table created successfully\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "id": "cce0d3bf",
   "metadata": {},
   "outputs": [],
   "source": [
    "file_path = os.path.join(os.getcwd(),  'Partitioning.sql')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "id": "6808155c",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Table dropped successfully\n",
      "Table created successfully\n"
     ]
    }
   ],
   "source": [
    "create_table(file_path, 'twitter_users_partitioned')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "id": "32c7ae19",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Create an index on the \"name\" column\n",
    "cur.execute(\"CREATE INDEX name_idx_p ON twitter_users_partitioned (name);\")\n",
    "conn.commit()\n",
    "\n",
    "# Create a compound index on the \"followers_count\" and \"verified\" columns\n",
    "cur.execute(\"CREATE INDEX followers_verified_idx_p ON twitter_users_partitioned (followers_count DESC, verified DESC);\")\n",
    "conn.commit()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "id": "3c19ee3d",
   "metadata": {},
   "outputs": [],
   "source": [
    "users = []"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "id": "8c9350a4",
   "metadata": {},
   "outputs": [],
   "source": [
    "def insert_user_info(tweet):\n",
    "    try:\n",
    "        cur.execute(\"\"\"\n",
    "        INSERT INTO twitter_users_partitioned \n",
    "        (user_id, name, screen_name, date, twitter_join_date, location, description, \n",
    "        verified, followers_count, friends_count, listed_count, favourites_count, language)\n",
    "        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)\n",
    "    \"\"\", (tweet['user']['id'], tweet['user']['name'], tweet['user']['screen_name'], tweet['created_at'], \n",
    "          tweet['user']['created_at'], tweet['user']['location'], tweet['user']['description'], \n",
    "          tweet['user']['verified'], tweet['user']['followers_count'], tweet['user']['friends_count'], \n",
    "          tweet['user']['listed_count'], tweet['user']['favourites_count'], tweet['user']['lang']))\n",
    "        \n",
    "        users.append({'user_id': tweet['user']['id'], \n",
    "                      'name': tweet['user']['name'], \n",
    "                      'screen_name': tweet['user']['screen_name'], \n",
    "                      'date': tweet['created_at'],\n",
    "                      'twitter_join_date': tweet['user']['created_at'], \n",
    "                      'location': tweet['user']['location'], \n",
    "                      'description': tweet['user']['description'], \n",
    "                      'verified': tweet['user']['verified'], \n",
    "                      'followers_count': tweet['user']['followers_count'], \n",
    "                      'friends_count': tweet['user']['friends_count'],\n",
    "                      'listed_count': tweet['user']['listed_count'], \n",
    "                      'favourites_count': tweet['user']['favourites_count'],\n",
    "                      'language': tweet['user']['lang']})\n",
    "\n",
    "    except Exception as e:\n",
    "        print(e)\n",
    "        conn.rollback()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "id": "65aafe4e",
   "metadata": {},
   "outputs": [],
   "source": [
    "# define the input and output formats\n",
    "input_format = '%a %b %d %H:%M:%S %z %Y'\n",
    "output_format = '%Y-%m-%d %H:%M:%S %Z%z'"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "id": "7d1019c8",
   "metadata": {},
   "outputs": [],
   "source": [
    "def load_data(file_path):\n",
    "    # Load the JSON data from file\n",
    "    with open(file_path, \"r\") as f:\n",
    "        for line in f:\n",
    "            try:\n",
    "                tweet = json.loads(line)\n",
    "                tweet['created_at'] = datetime.strptime(tweet['created_at'], input_format).strftime(output_format)\n",
    "                tweet['user']['created_at'] = datetime.strptime(tweet['user']['created_at'], input_format).strftime(output_format)\n",
    "                # insert user entry into database\n",
    "                insert_user_info(tweet)\n",
    "                # if there is a retweet, get original user from retweet\n",
    "                if (tweet['text'].startswith('RT')):\n",
    "                    original_tweet = tweet[\"retweeted_status\"]\n",
    "                    insert_user_info(original_tweet)\n",
    "            except:\n",
    "                # if there is an error loading the json of the tweet, skip\n",
    "                continue"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 18,
   "id": "384b406a",
   "metadata": {},
   "outputs": [],
   "source": [
    "load_data(\"C:\\\\Users\\\\priya\\\\Documents\\\\Courses\\\\SPL of Data management\\\\Project\\\\corona-out-2\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 19,
   "id": "c9e50341",
   "metadata": {},
   "outputs": [],
   "source": [
    "load_data(\"C:\\\\Users\\\\priya\\\\Documents\\\\Courses\\\\SPL of Data management\\\\Project\\\\corona-out-3\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 20,
   "id": "66d54c13",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Partition 0: 15087 rows\n",
      "Partition 1: 142551 rows\n",
      "Partition 2: 29367 rows\n",
      "Partition 3: 5689 rows\n"
     ]
    }
   ],
   "source": [
    "# create a list to store the row counts\n",
    "row_counts = []\n",
    "\n",
    "# loop through the partitions\n",
    "for i in range(1,5):\n",
    "    # generate the partition name\n",
    "    partition_name = 'twitter_users_partitioned_' + str(i)\n",
    "\n",
    "    # count the rows in the partition\n",
    "    count_query = sql.SQL(\"SELECT COUNT(*) FROM {}\").format(sql.Identifier(partition_name))\n",
    "    cur.execute(count_query)\n",
    "    row_count = cur.fetchone()[0]\n",
    "    row_counts.append(row_count)\n",
    "\n",
    "# print the row counts\n",
    "for i, row_count in enumerate(row_counts):\n",
    "    print(\"Partition {}: {} rows\".format(i, row_count))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 21,
   "id": "bc5670c5",
   "metadata": {},
   "outputs": [],
   "source": [
    "conn.commit()\n",
    "cur.close()\n",
    "conn.close()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 22,
   "id": "83a91181",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Create a pandas DataFrame from the parsed data\n",
    "df_users = pd.DataFrame(users)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 23,
   "id": "b4120b8b",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>user_id</th>\n",
       "      <th>name</th>\n",
       "      <th>screen_name</th>\n",
       "      <th>date</th>\n",
       "      <th>twitter_join_date</th>\n",
       "      <th>location</th>\n",
       "      <th>description</th>\n",
       "      <th>verified</th>\n",
       "      <th>followers_count</th>\n",
       "      <th>friends_count</th>\n",
       "      <th>listed_count</th>\n",
       "      <th>favourites_count</th>\n",
       "      <th>language</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>1242817830946508801</td>\n",
       "      <td>juwelz v</td>\n",
       "      <td>juwelz_v</td>\n",
       "      <td>2020-04-12 18:27:25 UTC+0000</td>\n",
       "      <td>2020-03-25 14:17:28 UTC+0000</td>\n",
       "      <td>Lower East Side, Manhattan</td>\n",
       "      <td>Event Lyfe LLC .. Brand Ambassador: #visionary...</td>\n",
       "      <td>False</td>\n",
       "      <td>43</td>\n",
       "      <td>118</td>\n",
       "      <td>0</td>\n",
       "      <td>722</td>\n",
       "      <td>None</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>16144221</td>\n",
       "      <td>NUFF</td>\n",
       "      <td>nuffsaidny</td>\n",
       "      <td>Sun Apr 12 16:48:01 +0000 2020</td>\n",
       "      <td>Fri Sep 05 14:28:41 +0000 2008</td>\n",
       "      <td>None</td>\n",
       "      <td>instagram: @nuffsaidny 🇹🇹</td>\n",
       "      <td>False</td>\n",
       "      <td>17112</td>\n",
       "      <td>1515</td>\n",
       "      <td>874</td>\n",
       "      <td>15790</td>\n",
       "      <td>None</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>1225145123920588805</td>\n",
       "      <td>efe09</td>\n",
       "      <td>efe0927183508</td>\n",
       "      <td>2020-04-12 18:27:25 UTC+0000</td>\n",
       "      <td>2020-02-05 19:52:38 UTC+0000</td>\n",
       "      <td>None</td>\n",
       "      <td>Allah'ın en değerli eseri insandır.\\nCanı yana...</td>\n",
       "      <td>False</td>\n",
       "      <td>653</td>\n",
       "      <td>983</td>\n",
       "      <td>0</td>\n",
       "      <td>1255</td>\n",
       "      <td>None</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>1087735689091928064</td>\n",
       "      <td>Karanfil Lale</td>\n",
       "      <td>lale_karanfil</td>\n",
       "      <td>Sun Apr 12 18:02:41 +0000 2020</td>\n",
       "      <td>Tue Jan 22 15:36:12 +0000 2019</td>\n",
       "      <td>None</td>\n",
       "      <td>None</td>\n",
       "      <td>False</td>\n",
       "      <td>897</td>\n",
       "      <td>1120</td>\n",
       "      <td>1</td>\n",
       "      <td>2776</td>\n",
       "      <td>None</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4</th>\n",
       "      <td>101007632</td>\n",
       "      <td>Ravin Gupta</td>\n",
       "      <td>IamRaavin</td>\n",
       "      <td>2020-04-12 18:27:26 UTC+0000</td>\n",
       "      <td>2010-01-01 16:24:24 UTC+0000</td>\n",
       "      <td>india</td>\n",
       "      <td>Tweet is personal opinion and Retweet is not e...</td>\n",
       "      <td>False</td>\n",
       "      <td>499</td>\n",
       "      <td>537</td>\n",
       "      <td>2</td>\n",
       "      <td>4342</td>\n",
       "      <td>None</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "               user_id           name    screen_name  \\\n",
       "0  1242817830946508801       juwelz v       juwelz_v   \n",
       "1             16144221           NUFF     nuffsaidny   \n",
       "2  1225145123920588805          efe09  efe0927183508   \n",
       "3  1087735689091928064  Karanfil Lale  lale_karanfil   \n",
       "4            101007632    Ravin Gupta      IamRaavin   \n",
       "\n",
       "                             date               twitter_join_date  \\\n",
       "0    2020-04-12 18:27:25 UTC+0000    2020-03-25 14:17:28 UTC+0000   \n",
       "1  Sun Apr 12 16:48:01 +0000 2020  Fri Sep 05 14:28:41 +0000 2008   \n",
       "2    2020-04-12 18:27:25 UTC+0000    2020-02-05 19:52:38 UTC+0000   \n",
       "3  Sun Apr 12 18:02:41 +0000 2020  Tue Jan 22 15:36:12 +0000 2019   \n",
       "4    2020-04-12 18:27:26 UTC+0000    2010-01-01 16:24:24 UTC+0000   \n",
       "\n",
       "                     location  \\\n",
       "0  Lower East Side, Manhattan   \n",
       "1                        None   \n",
       "2                        None   \n",
       "3                        None   \n",
       "4                       india   \n",
       "\n",
       "                                         description  verified  \\\n",
       "0  Event Lyfe LLC .. Brand Ambassador: #visionary...     False   \n",
       "1                          instagram: @nuffsaidny 🇹🇹     False   \n",
       "2  Allah'ın en değerli eseri insandır.\\nCanı yana...     False   \n",
       "3                                               None     False   \n",
       "4  Tweet is personal opinion and Retweet is not e...     False   \n",
       "\n",
       "   followers_count  friends_count  listed_count  favourites_count language  \n",
       "0               43            118             0               722     None  \n",
       "1            17112           1515           874             15790     None  \n",
       "2              653            983             0              1255     None  \n",
       "3              897           1120             1              2776     None  \n",
       "4              499            537             2              4342     None  "
      ]
     },
     "execution_count": 23,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "df_users.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "28d7e6c3",
   "metadata": {},
   "outputs": [],
   "source": [
    "df_users['twitter_join_date'] = pd.to_datetime(df_users['twitter_join_date'])\n",
    "df_users.groupby(df_users['twitter_join_date'].dt.year)['twitter_join_date'].count()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "58c6cd8b",
   "metadata": {},
   "outputs": [],
   "source": [
    "df_users.groupby(df_users['date'].dt.hour)['date'].count()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "0e924d19",
   "metadata": {},
   "outputs": [],
   "source": [
    "df_users.groupby(df_users['date'].dt.year)['date'].count()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "0a80d942",
   "metadata": {},
   "outputs": [],
   "source": [
    "min_date = df_users['date'].min()\n",
    "max_date = df_users['date'].max()\n",
    "print(min_date)\n",
    "print(max_date)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "5641c069",
   "metadata": {},
   "outputs": [],
   "source": [
    "dates_2020 = df_users.groupby(pd.Grouper(key='date', freq='M'))['date'].count().loc['2020-01-01':'2020-05-25']\n",
    "dates_2020"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "0c31f350",
   "metadata": {},
   "outputs": [],
   "source": [
    "df_users.to_csv('../data/users.csv', index=False)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "f238b772",
   "metadata": {},
   "outputs": [],
   "source": []
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
