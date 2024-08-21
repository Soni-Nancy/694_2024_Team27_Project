import time
import json as json_module
from collections import OrderedDict

class SearchCache:
    def __init__(self, max_size=100, ttl=3600, filepath="cache.json"):
        """
        Initializes the cache with a maximum size and time-to-live (ttl) values.

        Args:
        - max_size (int): Maximum number of items that the cache can hold.
        - ttl (int): Time-to-live of each cache entry in seconds.
        """
        self.max_size = max_size
        self.ttl = ttl
        # initialize an ordered dictionary that will be used as the cache
        self.cache = OrderedDict()
        # checkpoint file to save cache data
        self.checkpoint_file = filepath
        
        try:
            # load cache data from checkpoint file on disk
            with open(self.checkpoint_file, "r") as f:
                self.cache = OrderedDict(json_module.load(f))
        except FileNotFoundError:
            # if checkpoint file does not exist, create new file and cache
            with open(self.checkpoint_file, "w") as f:
                json_module.dump({}, f)
        except (FileNotFoundError, json_module.JSONDecodeError):
            # if checkpoint file is corrupted, delete and create new cache
            print("Cache file is corrupted.")
            self.cache.clear()
            print("Creating new cache.")
            self.save_checkpoint()

    def __contains__(self, key):
        """
        Returns a boolean value indicating if a key is present in the cache.

        Args:
        - key (str): Key to look up in the cache.

        Returns:
        - bool: True if the key is present in the cache, False otherwise.
        """
        return key in self.cache

    def __getitem__(self, key):
        """
        Retrieves the value and timestamp from the cache for a given key.

        Args:
        - key (str): Key to look up in the cache.

        Returns:
        - Any: Value associated with the given key.

        Raises:
        - KeyError: If the cache entry has expired.
        """
        # retrieve the value and timestamp from the cache for a given key
        try:
            value, timestamp = self.cache[key]
        except KeyError:
            print(f"Cache entry with key '{key}' not found.")
            return None
        # check if the cache entry has expired by comparing its timestamp with the current time
        if time.time() - timestamp > self.ttl:
            # remove the expired cache entry
            self.cache.pop(key)
            # print an error message indicating the cache entry has expired
            print(f"Cache entry with key '{key}' has expired.")
            return None
        # move the accessed cache entry to the end of the ordered dictionary
        self.cache.move_to_end(key)
        # return the value associated with the given key
        return value


    def __setitem__(self, key, value):
        """
        Adds or updates a cache entry for the given key with its corresponding value and timestamp.

        Args:
        - key (str): Key to add or update in the cache.
        - value (Any): Value to associate with the given key in the cache.
        """
        # check if the given key is already present in the cache
        if key in self.cache:
            # move the existing cache entry to the end of the ordered dictionary
            self.cache.move_to_end(key)
        # adds a new cache entry for the given key with its corresponding value and timestamp
        self.cache[key] = (value, time.time())
        # check if the cache has exceeded its maximum size
        if len(self.cache) > self.max_size:
            # remove the least recently used cache entry (i.e., the first item in the ordered dictionary)
            self.cache.popitem(last=False)
            
    def remove(self, key):
        """
        Removes a cache entry for a given key.

        Args:
        - key (str): Key to remove from the cache.
        """
        if key in self.cache:
            self.cache.pop(key)

    def clear(self):
        """
        Clears the entire cache.
        """
        self.cache.clear()
        print("Cache cleared!")

    def save_checkpoint(self):
        """
        Saves the current state of the cache to a file on disk.

        Args:
        - filepath (str): Path to the file to save the cache to.
        """
        with open(self.checkpoint_file, "w") as f:
            # write the current time as a comment
            f.write(f"# Checkpoint created on {time.ctime()}\n")
            # write each key-value pair in the cache to the file as a separate line
            for key, (value, timestamp) in self.cache.items():
                f.write(f"{key}={value}({timestamp})\n")
        print("Checkpoint saved!")

    def restore(self, filepath):
        """
        Restores the state of the cache from a file on disk.

        Args:
        - filepath (str): Path to the file to restore the cache from.
        """
        with open(filepath, "r") as f:
            # read each line from the file
            for line in f:
                # ignore comment lines (i.e., lines that start with a "#")
                if line.startswith("#"):
                    continue
                # parse the key, value, and timestamp from the line
                key_value, timestamp_str = line.strip().split("(")
                key, value = key_value.split("=")
                timestamp = float(timestamp_str[:-1])
                # check if the cache entry has expired by comparing its timestamp with the current time
                if time.time() - timestamp > self.ttl:
                    # remove the expired cache entry
                    self.cache.pop(key)
                    # print an error message indicating the cache entry has expired
                    print(f"Cache entry with key '{key}' has expired.")
                else:
                    # add the non-expired cache entry to the cache
                    self.cache[key] = (value, timestamp)

    def get_keys(self):
        return list(self.cache.keys())

    def get_values(self):
        return list(self.cache.values())

    def get_items(self):
        return list(self.cache.items())

