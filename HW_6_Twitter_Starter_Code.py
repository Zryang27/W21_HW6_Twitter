#########################################
##### Name:        Zhaorui Yang     #####
##### Uniqname:          zryang     #####
#########################################

from requests_oauthlib import OAuth1
import json
import requests
import secrets
#import hw6_secrets_starter as secrets # file that contains your OAuth credentials

CACHE_FILENAME = "twitter_cache.json"
CACHE_DICT = {}

client_key = secrets.TWITTER_API_KEY
client_secret = secrets.TWITTER_API_SECRET
access_token = secrets.TWITTER_ACCESS_TOKEN
access_token_secret = secrets.TWITTER_ACCESS_TOKEN_SECRET

oauth = OAuth1(client_key,
            client_secret=client_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret)

def test_oauth():
    ''' Helper function that returns an HTTP 200 OK response code and a 
    representation of the requesting user if authentication was 
    successful; returns a 401 status code and an error message if 
    not. Only use this method to test if supplied user credentials are 
    valid. Not used to achieve the goal of this assignment.'''

    url = "https://api.twitter.com/1.1/account/verify_credentials.json"
    auth = OAuth1(client_key, client_secret, access_token, access_token_secret)
    authentication_state = requests.get(url, auth=auth).json()
    return authentication_state


def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close()


def construct_unique_key(baseurl, params):
    ''' constructs a key that is guaranteed to uniquely and
    repeatably identify an API request by its baseurl and params

    AUTOGRADER NOTES: To correctly test this using the autograder, use an underscore ("_")
    to join your baseurl with the params and all the key-value pairs from params
    E.g., baseurl_key1_value1

    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dict
        A dictionary of param:value pairs

    Returns
    -------
    string
        the unique key as a string
    '''
    #TODO Implement function
    param_strings = []
    connector = '_'
    for k in params.keys():
    #    param_strings.append((f'{k}_{params[k]}').lower())
        param_strings.append(f'{k}_{params[k]}')
    param_strings.sort()
    unique_key = baseurl + connector +  connector.join(param_strings)
    return unique_key


def make_request(baseurl, params):
    '''Make a request to the Web API using the baseurl and params

    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dictionary
        A dictionary of param:value pairs

    Returns
    -------
    dict
        the data returned from making the request in the form of
        a dictionary
    '''
    #TODO Implement function
    response = requests.get(baseurl, params=params, auth=oauth)
    results = response.json()
    #tweets_data = results['statuses']
    #return tweets_data
    return results


def make_request_with_cache(baseurl, hashtag, count):
    '''Check the cache for a saved result for this baseurl+params:values
    combo. If the result is found, return it. Otherwise send a new
    request, save it, then return it.

    AUTOGRADER NOTES: To test your use of caching in the autograder, please do the following:
    If the result is in your cache, print "fetching cached data"
    If you request a new result using make_request(), print "making new request"

    Do no include the print statements in your return statement. Just print them as appropriate.
    This, of course, does not ensure that you correctly retrieved that data from your cache,
    but it will help us to see if you are appropriately attempting to use the cache.

    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    hashtag: string
        The hashtag to search for
    count: integer
        The number of results you request from Twitter

    Returns
    -------
    dict
        the results of the query as a dictionary loaded from cache
        JSON
    '''
    #TODO Implement function
    CACHE_DICT = open_cache()
    params = {'q': hashtag, 'count': count}
    unique_key = construct_unique_key(baseurl, params)
    if unique_key in CACHE_DICT:
        print("fetching cached data")
        tweet_data = CACHE_DICT[unique_key]
    else:
        print("making new request")
        tweet_data = make_request(baseurl, params)
        CACHE_DICT[unique_key] = tweet_data
        save_cache(CACHE_DICT)
    return tweet_data


def find_most_common_cooccurring_hashtag(tweet_data, hashtag_to_ignore):
    ''' Finds the hashtag that most commonly co-occurs with the hashtag
    queried in make_request_with_cache().

    Parameters
    ----------
    tweet_data: dict
        Twitter data as a dictionary for a specific query
    hashtag_to_ignore: string
        the same hashtag that is queried in make_request_with_cache()
        (e.g. "#MarchMadness2021")

    Returns
    -------
    string
        the hashtag that most commonly co-occurs with the hashtag
        queried in make_request_with_cache()

    '''
    # TODO: Implement function
    ht_dict = {}
    #for tweet in tweet_data:
    for tweet in tweet_data['statuses']:
        for cohashtag in tweet['entities']['hashtags']:
            if cohashtag['text'].lower() != hashtag_to_ignore[1:len(hashtag_to_ignore)].lower():
                if cohashtag['text'].lower() in ht_dict:
                    ht_dict[cohashtag['text'].lower()] = ht_dict[cohashtag['text'].lower()]+1
                else:
                    ht_dict[cohashtag['text'].lower()] = 1
    tuple_list_sorted = sorted(ht_dict.items(), key=lambda item: item[1], reverse=True)
    #return "#"+tuple_list_sorted[0][0]
    return tuple_list_sorted[0][0]
    ''' Hint: In case you're confused about the hashtag_to_ignore
    parameter, we want to ignore the hashtag we queried because it would
    definitely be the most occurring hashtag, and we're trying to find
    the most commonly co-occurring hashtag with the one we queried (so
    we're essentially looking for the second most commonly occurring
    hashtags).'''


if __name__ == "__main__":
    if not client_key or not client_secret:
        print("You need to fill in CLIENT_KEY and CLIENT_SECRET in secret_data.py.")
        exit()
    if not access_token or not access_token_secret:
        print("You need to fill in ACCESS_TOKEN and ACCESS_TOKEN_SECRET in secret_data.py.")
        exit()

    CACHE_DICT = open_cache()
    baseurl = "https://api.twitter.com/1.1/search/tweets.json"
    hashtag = "#MarchMadness2021"
    count = 100

    tweet_data = make_request_with_cache(baseurl, hashtag, count)
    most_common_cooccurring_hashtag = find_most_common_cooccurring_hashtag(tweet_data,
                                                                        hashtag)
    print("The most commonly cooccurring hashtag with {} is {}.".format(hashtag,
                                                most_common_cooccurring_hashtag))
