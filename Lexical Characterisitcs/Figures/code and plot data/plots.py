import matplotlib.pyplot as plt
from DataTuning import *
import numpy as np
import seaborn as sns

# Code used for plotting top 10 hashtags, user mentions etc.
def plot_data(data, x_label, y_label, title, **kwargs):

    y_type = kwargs.pop('y_type', None)
    x_type = kwargs.pop('x_type', None)
    plot_type = kwargs.pop('plot_type', None)
    arr = kwargs.pop('arr', None)
    x = []
    y = []
    if arr:
        for i in reversed(data):
            x.append(i[0])
            y.append(i[1])
    else:
        for k, val in data.items():
            x.append(k)
            y.append(val)

    print(x)
    print(y)
    sns.set_style('darkgrid', {'axes.linewidth': 1, 'axes.edgecolor': 'black'})
    plt.figure(figsize=(10, 7))
    #plt.gca().set_color_cycle(['dodgerblue', 'darkorange', 'blue'])
    if y_type:
        plt.gca().set_yscale(y_type)
    if x_type:
        plt.gca().set_xscale(x_type)
    if plot_type == 'bar':
        plt.bar(x, y, color='dodgerblue')
    if plot_type == 'scatter':
        plt.scatter(x, y, color='dodgerblue')
    else:
        pass#plt.plot(x, y, marker='o', color='dodgerblue')

    plt.xlabel(x_label, size=15)
    plt.ylabel(y_label, size=15)
    plt.title(title)
    plt.xticks(fontsize=12) #rotation=70
    #plt.tick_params(labelright=True)
    #plt.setp(plt.gca().get_xticklabels(), rotation=20, horizontalalignment='right')
    plt.show()

#d = db_open('exp/results/annotator_stats.json')
#d = sorted(d, key=lambda x: x[1], reverse=True)
#plot_data(d, 'Classes', 'Number of Tweets', 'Labelled Data',plot_type='bar')  #plot_type='bar'


# 25 most common words
def tfive_common():
    x = []
    y = []
    data = db_open('exp/results/common/25_words_non_neg.json')
    al = db_open('exp/results/all_freq_non_neg.json')
    total = sum(al.values())
    for i in reversed(data):
        print(i)
        x.append(i[0])
        y.append(i[1])
    print(x[:5])
    print(y[:5])
    sns.set_style('darkgrid', {'axes.linewidth': 1, 'axes.edgecolor': 'black'})
    plt.figure(figsize=(8, 6))
    # plt.gca().set_color_cycle(['dodgerblue', 'darkorange', 'mediumblue', 'peru'])
    plt.plot(x, y, linewidth=2, color='dodgerblue', marker='o')

    #plt.gca().set_xscale("log")
    #plt.xlabel('Words', size=15)
    plt.ylabel('Quantity', size=15)
    #plt.legend(['Negative class words', 'Non Negative class words'], loc='upper left')
    plt.title('25 most common words - "Non-Negative" class')
    plt.xticks(fontsize=10, rotation=80)
    y = [x/total for x in y]
    a = plt.axes([0.25, 0.46, 0.4, 0.35])
    plt.bar(x, y,color='darkorange')# linestyle='--', marker='.',
    plt.xticks(rotation='vertical')
    plt.title('top 25 words % of whole class')
    plt.ylabel('Frequency')
    plt.show()


# CDF - word entropy
def entropy():
    ent_neg = db_open('exp/results/entropy_neg.json')
    ent_non_neg = db_open('exp/results/entropy_non_neg.json')
    print(np.sort(ent_neg))
    print(np.sort(ent_non_neg))
    sns.set_style('darkgrid', {'axes.linewidth': 1, 'axes.edgecolor':'black'})
    plt.figure(figsize=(8, 6))
    #plt.gca().set_color_cycle(['dodgerblue', 'darkorange', 'mediumblue', 'peru'])
    plt.plot(np.sort(ent_neg), np.linspace(0, 1, len(ent_neg), endpoint=False),linewidth=2, color='darkorange')
    plt.plot(np.sort(ent_non_neg), np.linspace(0, 1, len(ent_non_neg), endpoint=False),linewidth=2,linestyle='--', color='dodgerblue')

    plt.gca().set_xscale("log")
    plt.xlabel('Entropy', size=15)
    plt.ylabel('CDF', size=15)
    plt.legend(['"Negative" class words', '"Non-Negative" class words'], loc='lower right')
    plt.show()

# Databases for tweet and word lengths
len_neg = db_open('exp/results/len/all_length_word_neg.json')
len_non_neg = db_open('exp/results/len/all_length_word_non_neg.json')

len_t_neg = db_open('exp/results/len/tweets_length_neg.json')
len_t_non_neg = db_open('exp/results/len/tweets_length_non_neg.json')


# CDF - word lengths
def length_words():

    sns.set_style('darkgrid', {'axes.linewidth': 1, 'axes.edgecolor':'black'})
    plt.figure(figsize=(8, 6))
    #plt.gca().set_color_cycle(['dodgerblue', 'darkorange', 'mediumblue', 'peru'])
    plt.plot(np.sort(len_neg), np.linspace(0, 1, len(len_neg), endpoint=False),linewidth=2, linestyle='--', color='darkorange')
    plt.plot(np.sort(len_non_neg), np.linspace(0, 1, len(len_non_neg), endpoint=False),linewidth=2, color='dodgerblue')

    #plt.plot(np.sort(median_numbers), np.linspace(0, 1, len(median_numbers), endpoint=False),linewidth=2)
    plt.gca().set_xscale("log")
    plt.xlabel('Length', size=15)
    plt.ylabel('CDF', size=15)
    plt.legend(['"Negative" class', '"Non-Negative" class'], loc='upper left')
    plt.title('Word Length Distribution')

    avg_neg = sum(len_neg) / len(len_neg)
    avg_non_neg = sum(len_non_neg) / len(len_non_neg)
    a = plt.axes([0.6, 0.3, 0.2, 0.3])
    plt.bar("Negative", avg_neg, color='darkorange', width=0.5, align='center')  # linestyle='--', marker='.',
    plt.bar("Non-Negative", avg_non_neg, color='dodgerblue', width=0.5, align='center')
    #plt.xticks(rotation='vertical')
    plt.title('Average word Length')
    plt.ylabel('Average')
    plt.show()

# CDF - tweet lengths
def length_tweets():
    sns.set_style('darkgrid', {'axes.linewidth': 1, 'axes.edgecolor':'black'})
    plt.figure(figsize=(8, 6))
    #plt.gca().set_color_cycle(['dodgerblue', 'darkorange', 'mediumblue', 'peru'])

    plt.plot(np.sort(len_t_neg), np.linspace(0, 1, len(len_t_neg), endpoint=False),linewidth=2, linestyle='--', color='darkorange')
    plt.plot(np.sort(len_t_non_neg), np.linspace(0, 1, len(len_t_non_neg), endpoint=False),linewidth=2, color='dodgerblue')
    #plt.plot(np.sort(median_numbers), np.linspace(0, 1, len(median_numbers), endpoint=False),linewidth=2)
    plt.gca().set_xscale("log")
    plt.xlabel('Length', size=15)
    plt.ylabel('CDF', size=15)
    plt.legend(['"Negative" class', '"Non-Negative" class'], loc='upper left')
    plt.title('Tweet Length Distribution')
    avg_neg = sum(len_t_neg) / len(len_t_neg)
    avg_non_neg = sum(len_t_non_neg) / len(len_t_non_neg)
    a = plt.axes([0.25, 0.4, 0.2, 0.3])
    plt.bar("Negative", avg_neg, color='darkorange', width=0.5, align='center')  # linestyle='--', marker='.',
    plt.bar("Non-Negative", avg_non_neg, color='dodgerblue', width=0.5, align='center')
    #plt.legend(['"Negative" class', '"Not Negative" class'])
    # plt.xticks(rotation='vertical')
    plt.title('Average Tweet Length')
    plt.ylabel('Average')
    plt.show()

# URLs
def url_plot():
    n = 540  # num of negative tweets with url
    p = 1389  # num of non-negative tweets with url
    n_t = 2114
    p_t = 3971
    ind = np.arange(2)
    sns.set_style('darkgrid', {'axes.linewidth': 1, 'axes.edgecolor': 'black'})
    plt.bar('Negative class', n_t / n_t, color='dodgerblue', width=0.3, label='Without URL')

    plt.bar('Non-Negative', p_t / p_t, color='dodgerblue', width=0.3)

    plt.bar('Negative class', n / n_t, color='darkorange', width=0.3, label='With URL')
    plt.bar('Non-Negative', p / p_t, color='darkorange', width=0.3)
    plt.legend(loc='upper center')
    plt.suptitle('URLs present in tweets', fontsize=12)
    plt.xlabel('Class', fontsize=12)
    plt.ylabel('Percentage %', fontsize=12)
    plt.show()


#tfive_common()
#length_tweets()
entropy()




