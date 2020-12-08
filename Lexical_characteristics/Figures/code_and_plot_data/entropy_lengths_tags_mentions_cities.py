from DataTuning import *
from math import log2
import re


# Finds hashtags, user mentions etc. based on he forst char of the word
def get_words_by_first_char(char, lst):
    exp = char + '\w+[\s\.]'
    words = []
    for tweet in lst:
        temp = re.findall(exp, tweet)
        w_low = [w.lower() for w in temp]
        words += w_low
    print('Word count: ', len(words))
    return words


# Calculating entropy for all word frequencies
entropy_list = []
all_lengths = []
dic = db_open('exp/results/all_freq_non_neg.json') # opening word frequencies
print('Origianl Length: ', len(dic))
total = sum(dic.values())
for freq in dic.items():
    if len(freq[0]) > 2 or len(freq[0]) == 2 and freq[1] > 1:
        entropy = freq[1] / total * log2(total / freq[1])
        entropy_list.append(entropy)
        all_lengths.append(len(freq[0])) # get word length
print('Entropy list length: ', len(entropy_list))
print(entropy_list)
print('All lengths no of items: ', len(all_lengths))
db_save(entropy_list, 'exp/results/entropy_non_neg2.json')
# db_save(all_lengths, 'exp/results/len/all_length_word_non_neg.json')

"""
# Get Tweets length
db = db_open('exp/results/tweets_length_non_neg.json')

all_lengths = []

for t in db:
    all_lengths.append(len(t))

db_save(all_lengths,'exp/results/len/tweets_length_non_neg.json')
"""
# All code below is for checking location parameter in tweets against a list of cities
twts = db_open('exp/results/final_database.json')
cts = db_open('exp/all_city_locations.json')

for c in cts : # Removing state/country/odd names and one city name: 'newcastle upon tyne' as they were causing confusion
    if c in {'england', 'scotland', 'florida', 'alberta', 'california', 'columbia', 'ontario', 'earth', 'north', 'newcastle upon tyne'}:
        cts.remove(c)
#db_save(cts, 'exp/all_city_locations.json')
no_loc = 0
empty_loc = 0
neg = [x['location'].lower() for x in twts if 'location' in x and x['negative']] # getting locations from negative tweets
non_neg = [x['location'].lower() for x in twts if 'location' in x and not x['negative'] and not x['undecided'] and not x['unrelated'] and not x['error']] # getting locations from non-negative tweets
neg_cities = {} # cities from negative set
#non_neg_cities ={} # cities from non-neg set
for city in cts:
    for loc in neg:
        if re.search(r'\b' + city + r'\b', loc):
            count = neg_cities.get(city, 0)
            neg_cities[city] = count + 1

print(len(neg_cities))
print(neg_cities)
# Getting only top 10 cities
last10neg = sorted(neg_cities.items(), key=lambda x: x[1])[-10:]
print(last10neg)
#db_save(last10neg, 'exp/results/10_cities_neg.json')
