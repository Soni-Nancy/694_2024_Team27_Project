-- create the partitioning function
CREATE OR REPLACE FUNCTION my_extract_hour(ts timestamp with time zone)
RETURNS integer AS $$
BEGIN
  RETURN extract(hour FROM ts);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- create the table with partitioning
CREATE TABLE IF NOT EXISTS public.twitter_users_partitioned (
    user_id character varying(255) COLLATE pg_catalog."default" NOT NULL,
    name text COLLATE pg_catalog."default",
    screen_name text COLLATE pg_catalog."default",
    "date" timestamp with time zone NOT NULL,
    twitter_join_date date,
    location text COLLATE pg_catalog."default",
    description text COLLATE pg_catalog."default",
    verified boolean,
    followers_count integer,
    friends_count integer,
    listed_count integer,
    favourites_count integer,
    language text COLLATE pg_catalog."default"
) PARTITION BY RANGE(my_extract_hour("date"));

CREATE TABLE public.twitter_users_partitioned_1 PARTITION OF public.twitter_users_partitioned FOR VALUES FROM (0) TO (6);
CREATE TABLE public.twitter_users_partitioned_2 PARTITION OF public.twitter_users_partitioned FOR VALUES FROM (6) TO (12);
CREATE TABLE public.twitter_users_partitioned_3 PARTITION OF public.twitter_users_partitioned FOR VALUES FROM (12) TO (18);
CREATE TABLE public.twitter_users_partitioned_4 PARTITION OF public.twitter_users_partitioned FOR VALUES FROM (18) TO (24);