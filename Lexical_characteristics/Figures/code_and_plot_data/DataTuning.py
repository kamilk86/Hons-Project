import json
import os
import csv
import random

words_short = {
    "doesn't": 'does not',
    "can't": 'cannot',
    "won't": 'will not',
    "don't": 'do not',
    "i,ve": 'i have',
    "i'd": 'i would',
    "i'm": 'i am',
    "i'll": 'i will',
    "she's": 'she is',
    "he's": 'he is',
    "it's": 'it is',
    "there's": 'there is',
    "they're": 'they are',
    "we're": 'we are',
    "you're": 'you are',
    "couldn't": 'could not',
    "shouldn't": 'should not',
    "wouldn't": 'would not'
}


def db_save(data, filename):
    path, file = os.path.split(filename)
    if path:
        try:
            os.makedirs(path)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except OSError:
            if os.path.exists(path):
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
            else:
                raise
    else:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)


def db_open(filename):
    with open(filename, 'rb') as f:
        data = json.load(f)
    return data


def to_csv(src, dest):
    db = db_open(src)
    with open(dest + '.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['text', 'label'])
        for t in db:
            if t['negative']:
                writer.writerow([t['text'], '__label__2'])
            if not t['negative']:
                writer.writerow([t['text'], '__label__1'])


def get_unique_ids(source, **kwargs):
    """Gets only IDs from specified object database and removes any duplicates """
    path = kwargs.pop('path', None)
    if path:
        lst = db_open(source)   # If 'path' is True then open from file
        ids = [i['id'] for i in lst if 'id' in i]
    else:
        ids = [i['id'] for i in source if 'id' in i]

    unique_ids = list(set(ids))
    diff = len(ids) - len(unique_ids)
    print('Total unique IDs in list: ', len(unique_ids))
    print('Removed: ', diff)

    return unique_ids


def prepare_for_marking(source, ids_list, **kwargs):
    new = []
    rm = 0
    final = []
    path = kwargs.pop('path', None)
    if path:
        db = db_open(source)
    else:
        db = source

    prev_ids = db_open(ids_list)
    uniq_src_ids = get_unique_ids(db)

    for twt in db:
        if twt['id'] in uniq_src_ids:
            new.append(twt)
            uniq_src_ids.remove(twt['id'])
        else:
            rm += 1
    print('Duplicates found: ', rm)
    rm = 0
    for twt in new:
        if twt['id'] not in prev_ids:
            final.append(twt)
        else:
            rm += 1
    print('Similar Tweets found within previous databases: ', rm)
    print('Final amount: ', len(final))

    return final


def trim_db_file(org_path, dest_path):
    """Gets following parameters from tweet object: date, id, text, urls and saves database under specified path"""
    new_db = []
    old_db = db_open(org_path)
    for twt in old_db:
        urls = []
        # Gets urls from tweet object if present
        if twt['entities']['urls']:
            for url in twt['entities']['urls']:
                urls.append(url['expanded_url'])
        new_twt = {
            'created_at': twt['created_at'],
            'id': twt['id'],
            'text': twt['text'],
            'urls': urls
            }
        new_db.append(new_twt)
    print('Saving database for: ', dest_path)
    db_save(new_db, dest_path)


def trim_db_object(tweets):
    trimmed = []
    for twt in tweets:
        tweet = {'created_at': twt['created_at'],
                 'id': twt['id'],
                 'text': twt['full_text']}
        trimmed.append(tweet)

    return trimmed


def clean_tweets(src):
    """Removes user mentions, special characters, hash chars from hashtags and converts all text to lowercase"""
    neg = 0
    non_neg = 0
    neg_urls = 0
    non_neg_urls = 0
    neg_url_perc = 0
    non_neg_url_perc = 0
    if isinstance(src, str):
        db = db_open(src)
    else:
        db = src
    deleted = []
    for t in db:
        txt = t['text'].replace('\n', ' ').replace('"', ' ').replace('(', ' ').replace(')', ' ').replace(':', '').replace(',', ' ').replace('?', ' ').replace('*', '').replace('.', '').replace('!', '').replace('&', ' ').replace(';', ' ')# .replace("'", '')
        words = txt.split(' ')
        new_txt = []
        if t['negative']:
            neg += 1
        if not t['negative']:
            non_neg += 1
        for word in words:
            if not word.startswith('@') and not word.lower() == 'amp' and 'http' not in word: #
                if word.startswith('#'):
                    word = word.replace('#', '')
                new_txt.append(word.lower())
            for short in words_short.items():
                if word.lower() == short[0]:
                    if len(short[1]) > 1:
                        two = short[1].split(' ')
                        new_txt += two
                    else:
                        new_txt.append(short[1])

            if 'http' in word:
                if t['negative']:
                    neg_urls += 1
                if not t['negative']:
                    non_neg_urls += 1
        #print(t['text'])
        temp = [x for x in new_txt if x]
        t['text'] = ' '.join(temp)
        #print(t['text'])
    if neg_urls:
        neg_url_perc = neg_urls / neg * 100
    if non_neg_urls:
        non_neg_url_perc = non_neg_urls / non_neg * 100
    print('Negative: ', neg)
    print('Not Negative: ', non_neg)
    print('[*] clean_tweets: Deleted words: ', len(deleted))
    print('[*] clean_tweets: Negative URLs count: ', neg_urls, 'percentage of total: ', neg_url_perc)
    print('[*] clean_tweets: Not Negative URLs count: ', non_neg_urls, 'percentage of total: ', non_neg_url_perc)
    return db


def balance_dataset(filename, **kwargs):
    path = kwargs.pop('path', None)
    rand = kwargs.pop('rand', None)
    if path:
        db = db_open(filename)

    else:
        db = filename
    print('Items in database: ', len(db))
    if rand:
        random.shuffle(db)
    new = []
    label_1 = 0
    label_2 = 0

    for twt in db:
        if twt['negative']:
            new.append(twt)
            label_1 += 1
    for twt in db:
        if not twt['negative']:
            new.append(twt)
            label_2 += 1
            if label_2 == label_1:
                break
    print('Label 1: ', label_1)
    print('Label 2: ', label_2)
    return new


def prepare_dbs(path):

    final = []
    neg = 0
    non_neg = 0
    und = 0
    unr = 0
    err = 0

    run = 0
    for file in os.listdir(path):
        # run += 1

        if os.path.isfile(path + file) and not file.startswith('unique'):
            db = db_open(path + file)
            for txt in db:
                if 'negative' in txt:
                    if not txt['undecided'] and not txt['unrelated'] and not txt['error']:
                        new = {
                            'text': txt['text'],
                            'negative': txt['negative']
                        }
                        final.append(new)
                    if txt['negative']:
                        neg += 1
                    if not txt['negative'] and not txt['undecided'] and not txt['unrelated'] and not txt['error']:
                        non_neg += 1
                    if txt['undecided']:
                        und += 1
                    if txt['unrelated']:
                        unr += 1
                    if txt['error']:
                        err += 1

    print('Total marked: ', len(final))
    print('Negative: ', neg)
    print('Not Negative: ', non_neg)
    print('Undecided: ', und)
    print('Unrelated: ', unr)
    print('Error: ', err)
    stats = {
        'total': len(final),
        'negative': neg,
        'not negative': non_neg,
        'undecided': und,
        'unrelated': unr,
        'error': err
    }
    return final, stats
