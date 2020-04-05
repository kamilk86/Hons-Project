from TwitterAPIwrapper import SearchTwitter
from DataTuning import *
import time
import os
import traceback
# import tldextract
from auth_details import auth_details


tweets_endpoint = '1.1/search/tweets.json'
users_endpoint = '1.1/users/search.json'
lookup_url = '1.1/users/lookup.json'
timeline_endpoint = '1.1/statuses/user_timeline.json'
tweet_lookup_endpoint = '1.1/statuses/lookup.json'


#path = 'C:\\Users\\Kamil\\PycharmProjects\\crawler\\'
#brexit_terms = ['Brexit', '#Brexit', '"Article 50"', '"article 50"', '#hardbrexit', '"Hard Brexit"', '"hard brexit"', '#softbrexit', '"Soft Brexit"', '"soft brexit"', 'brexitdeal', '"leave eu"', '"Leave eu"', '"Leave EU"', '"leave EU"', '#GetBrexitDone', '#stopbrexit', '#antibrexit', '#revokearticle', '#BackBoris', '#LeaveMeansLeave', 'brexit deal']


api = SearchTwitter(auth_details)


# Checks remaining requests for given API endpoint
def check_limits(endpoint_path, remaining_limit):
    w_count = 0
    endpoint_name = endpoint_path.split('/')[1]
    data = api.get_limits(endpoint_name)
    obj = json.loads(data)
    remaining = obj['resources'][endpoint_name][endpoint_path]['remaining']
    print('Remaining requests for: ' + endpoint_path + ' = ' + str(remaining))
    while remaining < remaining_limit:
        print('No. of remaining requests for this endpoint too low to continue')
        print('Waiting 5 mins…')
        w_count += 1
        time.sleep(300)
        print('Checking remaining requests')
        data = api.get_limits(endpoint_name)
        obj = json.loads(data)
        remaining = obj['resources'][endpoint_name][endpoint_path]['remaining']
        print('Remaining requests for: ' + endpoint_path + ' =  ' + str(remaining))
        if w_count > 30:
            print('ERROR. TOO MANY RUNS!')
            break


# Searches tweets by city
def get_tweets_by_city(city_list_path, dest_path, terms, **kwargs):

    run_limit = kwargs.pop('runs', None)
    single = kwargs.pop('single', None)
    all_tweets = []
    run = 0
    grand_tot = 0
    cities = db_open(city_list_path)
    for city in cities:
        run += 1
        check_limits('/search/tweets', len(terms) + 1)
        tweets = []
        if city['city'] == 'London':
            radius = '20km'
        elif city['city'] == 'Manchester':
            radius = '10km'
        else:
            radius = '6km'

        geo_str = ','.join([city['lat'], city['lng'], radius])
        print(city['city'])

        for term in terms:
            tweet_data = api.search(tweets_endpoint, q=term + ' -filter:retweets', count='100', lang='en', tweet_mode='extended', geocode=geo_str)
            temp = json.loads(tweet_data)
            if 'statuses' in temp:
                tweets += temp['statuses']
            time.sleep(0.5)
        grand_tot += len(tweets)
        all_tweets += tweets
        if not single:
            print('Total Tweets for: ', city['city'], ' = ', len(tweets))
            print('Saving database for: ', city['city'])
            db_save(tweets, dest_path + city['city'] + '.json')
        if run_limit:
            if run == run_limit:
                print('---TEST SUMMARY---')
                print('Total Tweets found for all cities: ', grand_tot)
                return
    if single:
        db_save(all_tweets, dest_path + 'all cities.json')
    print('---SUMMARY---')
    print('Total Tweets found for all cities: ', grand_tot)


# Removing duplicates from tweets by city
def remove_duplicates(org_path, dest_path):
    tot = 0
    org_tot = 0
    count = 0
    tot_ids = []
    for city in os.listdir(org_path):
        filename = os.path.splitext(city)[0]
        new = []
        count += 1
        tweets = db_open(org_path + filename)
        ids = [x['id'] for x in tweets]
        org_ids = set(ids)
        tot += len(ids)
        org_tot += len(org_ids)
        print('City: ', filename)
        print('Total Tweets: ', len(ids))
        print('Original Tweets: ', len(org_ids))
        print('No Removed: ', len(ids)-len(org_ids))
        for twt_id in org_ids:
            new.append((next(x for x in tweets if x['id'] == twt_id)))
        print('[*] Saving file: ', filename)
        db_save(new, dest_path + filename)

    print('----SUMMARY-----')
    print('Number of cities: ', count)
    print('Total for all cities: ', tot)
    print('Total actual: ', org_tot)
    print('Total removed: ', tot-org_tot)
    print('Total actual after check: ', len(set(tot_ids)))


# Retrieves extended version of tweets
def get_extended_tweets(org_path, dest_path):
    run = 0
    req = 0
    check_limits('/statuses/lookup', 500)
    for file in os.listdir(org_path):

        filename = os.path.splitext(file)[0]
        print('Run no: ', run)
        print('File: ', filename)

        if req >= 400:
            check_limits('/statuses/lookup', 450)
            req = 0
        run += 1

        db = db_open(org_path + filename)
        ids = [x['id'] for x in db]
        tweets = []
        if len(ids) > 100:
            hundreds = int((str(len(ids) / 100)).split('.')[0])
            rem = len(ids) % 100
            for i in range(1, hundreds+2):
                if 1 <= i <= hundreds:
                    start = (i-1) * 100
                    part_ids = ids[start:i*100]
                elif i > hundreds and rem:
                    part_ids = ids[(i-1)*100:]
                else:
                    break
                ids_str = ','.join(str(i) for i in part_ids)
                tweets_obj = api.search(tweet_lookup_endpoint, id=ids_str, tweet_mode='extended')
                temp = json.loads(tweets_obj)
                tweets += temp
                time.sleep(0.5)
                if rem:
                    req += (hundreds + 1)
                else:
                    req += hundreds
        else:
            ids_str = ','.join(str(i) for i in ids)
            tweets_obj = api.search(tweet_lookup_endpoint, id=ids_str, tweet_mode='extended')
            temp = json.loads(tweets_obj)
            tweets += temp
            time.sleep(0.5)
            req += 1

        ids2 = [x['id'] for x in tweets]

        for tweet_id in ids:
            if tweet_id not in ids2:
                tweets.append(next(x for x in db if x['id'] == tweet_id))

        print('Org db: ', len(db))
        print('Final db: ', len(tweets))

        print('[*] Saving file: ', filename)
        db_save(tweets, dest_path + filename)


# Removes unnecessary information from a database of tweets
def trim_all_dbs(org_path, dest_path):
    count = 0
    for file in os.listdir(org_path):
        count += 1
        file_name = os.path.splitext(file)[0]
        trim_db_file(org_path + file_name, dest_path + file_name)
    print('Total database files trimmed: ', count)


# Searches tweets by geo-location
def search_tweets_by_location(terms, geo_list, dest_path, **kwargs):
    trimmed_tweets = []
    run_limit = kwargs.pop('runs', None)
    print('Run limit', run_limit)
    run = 0
    for location in geo_list:
        run += 1
        full_tweets = []
        check_limits('/search/tweets', len(terms)+1)
        for term in terms:
            query = term + ' -filter:retweets'
            try:
                tweets_obj = api.search(tweets_endpoint, q=query, count='100', lang='en', tweet_mode='extended', geocode=location)
                temp = json.loads(tweets_obj)
                full_tweets += temp['statuses']
                time.sleep(0.5)
            except Exception as e:
                print('Error occurred while evaluating location: ', location)
                print('Restart from above location')
                print('Error: ', e)
                print('Saving database...')
                db_save(trimmed_tweets, dest_path)

        trim_temp = trim_db_object(full_tweets)
        trimmed_tweets += trim_temp
        if run == run_limit:
            print('Tweets found: ', len(trimmed_tweets))
            print('Saving database')
            db_save(trimmed_tweets, dest_path)
            return
    print('Tweets found: ', len(trimmed_tweets))
    print('Saving database')
    db_save(trimmed_tweets, dest_path)


# Retrieves unique tweet ids from multiple database files
def get_unique_ids_multifile(path):
    total_files = []
    for file in os.listdir(path):
        if not file.startswith('unique'):
            db = db_open(path + file)
            total_files += db

    unique_ids = get_unique_ids(total_files)
    db_save(unique_ids, path + 'unique ids all.json')



geo_list = ['55.735640,-119.610626,1000km', '54.971268,-101.441180,1000km', '49.753486,-76.959958,1000km', '45.490719,-114.503112,1000km', '38.102247,-114.341699,1000km',
            '42.534544,-99.278191,1000km', '34.294260,-99.232754,1000km', '42.216458,-89.489847,1000km', '33.562510,-86.551903,1000km', '38.244801,-77.683639,1000km',
                   '51.503614,-0.208737,150km', '50.861354,-3.246317,150km', '53.951024,-1.962953,150km', '56.022123,-3.773372,150km',
                   '57.341869,-3.277874,150km', '54.441099,-7.331622,150km', '52.655814,-8.097001,200km']

geo_dict = {
    'canada': ['55.735640,-119.610626',
               '54.971268,-101.441180',
               '49.753486,-76.959958'],
    'us': ['45.490719,-114.503112',
           '38.102247,-114.341699',
           '42.534544,-99.278191',
           '34.294260,-99.232754',
           '42.216458,-89.489847',
           '33.562510,-86.551903',
           '38.244801,-77.683639'],
    'uk': ['51.503614,-0.208737',
           '50.861354,-3.246317',
           '53.951024,-1.962953',
           '56.022123,-3.773372',
           '57.341869,-3.277874',
           '54.441099,-7.331622',
           '52.655814,-8.097001']
}
# keywords used for searching tweets
immigrant_terms = ['migrant', 'foreigner', '#multiculturalism', '#defendeurope', 'deport', '#DeportThemALL', '#refugeesNOTwelcome', '#remigration', '#RefugeesNotWelcome', 'immigrant', '"illegal immigration"', 'immigration', '#immigrationreform', '#immigrationplan', '#illegalimmigration', '#antiimmigration']
hashtag_terms = ['#defendeurope', '#NotWelcome', '#CanadaIsFull', '#WeWillNotBeEurope', '#IrelandbelongstotheIrish', '#ScotlandForScots', '#Banislam', '#StopTheInvasion', '#antiimmigration', '#IllegalAliens', '#NoMoreRefugees', '#Deport_them', '#DeportThemAll']


#prepared = prepare_for_marking('training data/all cities.json', 'training data/raw/unique ids all.json', path=True)
#trimmed = trim_db_object(prepared)
#db_save(trimmed, 'training data/raw/3 partially marked.json')

#get_unique_ids_multifile('training data/raw/')

"""
ids = get_unique_ids('exp/all_marked.json', path=True)
#rem 70
runs = 0
full_tweets = []
tot = 0
for run in range(83):
    if run < 82:
        start = run * 100
        end = (run + 1) * 100
        part_ids = ids[start:end]

    if run == 82:
        part_ids = ids[8200:]

    print('Part length: ', len(part_ids))

    ids_str = ','.join(str(i) for i in part_ids)
    temp = api.search(tweet_lookup_endpoint, id=ids_str, tweet_mode='extended')
    full_tweets += json.loads(temp)
    time.sleep(0.5)

print(len(full_tweets))
db_save(full_tweets, 'exp/full.json')
"""

