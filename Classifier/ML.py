import pandas as pd
import numpy as np
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.preprocessing import LabelEncoder
from collections import defaultdict
from nltk.corpus import wordnet as wn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import model_selection, naive_bayes, svm
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

from DataTuning import *
import csv
from nltk.util import ngrams
import random


path = 'training data/raw/'
#db_save(final, path + 'combined/' + 'final.json')


print('Preparing marked Tweets...')
final, st = prepare_dbs(path)
eq_final = balance_dataset(final)
print('Cleaning...')
cleaned = clean_tweets(eq_final)
db_save(cleaned, 'training data/processed/cleaned.json')
to_csv('training data/processed/cleaned.json', 'training data/processed/data2')

np.random.seed(500)

Corpus = pd.read_csv(r"training data\processed\data2.csv", encoding='latin1')
Corpus['text'].dropna(inplace=True)
Corpus['text'] = [word_tokenize(entry) for entry in Corpus['text']]

stats = {
    'nb': {
        'acc': [],
        'f1': [],
        'prec': [],
        'rec': []
    },
    'svm': {
        'acc': [],
        'f1': [],
        'prec': [],
        'rec': []
    },
    'lg': {
        'acc': [],
        'f1': [],
        'prec': [],
        'rec': []
    }
}

tag_map = defaultdict(lambda: wn.NOUN)
tag_map['J'] = wn.ADJ
tag_map['V'] = wn.VERB
tag_map['R'] = wn.ADV

print('Pre-processing corpus...')
for index,entry in enumerate(Corpus['text']):

    Final_words = []

    word_Lemmatized = WordNetLemmatizer()

    for word, tag in pos_tag(entry):
        # Removing stop words and non-alpha words
        if word not in stopwords.words('english') and word.isalpha():
            word_Final = word_Lemmatized.lemmatize(word,tag_map[tag[0]])
            Final_words.append(word_Final)
        # elif word in {'not', 'he', 'she', 'her', 'him'}:
        #    Final_words.append(word)

    # char n-grams lengths 1-4
    b = ' '.join(Final_words)
    char_unigrams = [b[i:i+1] for i in range(len(b)-1+1)]
    char_bigrams = [b[i:i+2] for i in range(len(b)-2+1)]
    char_trigrams = [b[i:i+3] for i in range(len(b)-3+1)]
    char_fourgrams = [b[i:i+4] for i in range(len(b)-4+1)]
    #char_fivegrams = [b[i:i+5] for i in range(len(b)-5+1)]
    final_ngrams = char_unigrams + char_bigrams + char_trigrams + char_fourgrams #+ char_fivegrams

    # word n-grams lengths 1-3
    #ngrams_lst = list(ngrams(Final_words, 2))
    #ngrams_lst += list(ngrams(Final_words, 3))
    #n_grams = [' '.join(x) for x in ngrams_lst]
    #Final_words += ngrams_lst

    Corpus.loc[index,'text_final'] = str(final_ngrams)
print('Training model...')

# Splitting corpus for 10 fold cross validation using for loop
x, y = Corpus['text_final'], Corpus['label']
run = 0
kfold = model_selection.KFold(10, True, 1)
for train_idx, test_idx in kfold.split(x, y):
    run += 1
    print('**************** Test No: ', run)
    Train_X, Test_X = x[train_idx], x[test_idx]
    Train_Y, Test_Y = y[train_idx], y[test_idx]


#Train_X, Test_X, Train_Y, Test_Y = model_selection.train_test_split(Corpus['text_final'],Corpus['label'],test_size=0.1)

    # Encodes string labels as numbers
    Encoder = LabelEncoder()
    Train_Y = Encoder.fit_transform(Train_Y)
    Test_Y = Encoder.fit_transform(Test_Y)

    # Using TF-IDf to vectorize tokens
    Tfidf_vect = TfidfVectorizer()#max_features=500
    Tfidf_vect.fit(Train_X)

    Train_X_Tfidf = Tfidf_vect.transform(Train_X)
    Test_X_Tfidf = Tfidf_vect.transform(Test_X)

    # Naive Bayes
    Naive = naive_bayes.MultinomialNB()
    Naive.fit(Train_X_Tfidf,Train_Y)

    predictions_NB = Naive.predict(Test_X_Tfidf)

    # Getting Metrics for NB
    nb_acc = accuracy_score(predictions_NB, Test_Y)
    nb_f = f1_score(predictions_NB, Test_Y)
    nb_prec = precision_score(predictions_NB, Test_Y)
    nb_rec = recall_score(predictions_NB, Test_Y)

    print("Naive Bayes Accuracy Score -> ",nb_acc*100)
    print('Naive Bayes F-score -> ', nb_f*100)
    print('Naive Bayes Precision Score -> ', nb_prec*100)
    print('Naive Bayes Recall -> ', nb_rec*100)

    # Appending achieved NB metrics to database
    stats['nb']['acc'].append(nb_acc)
    stats['nb']['f1'].append(nb_f)
    stats['nb']['prec'].append(nb_prec)
    stats['nb']['rec'].append(nb_rec)
    print('---------------------------------------')
    #print('Predictions: ', predictions_NB)

    # Support Vector Machines
    SVM = svm.SVC(C=1.0, kernel='linear', degree=3, gamma='auto')
    SVM.fit(Train_X_Tfidf,Train_Y)
    #print('SVM core: ', SVM.score(Test_X_Tfidf, Test_Y))

    # Getting Metrics for SVM
    predictions_SVM = SVM.predict(Test_X_Tfidf)
    svm_acc = accuracy_score(predictions_SVM, Test_Y)
    svm_f =  f1_score(predictions_SVM, Test_Y)
    svm_prec = precision_score(predictions_SVM, Test_Y)
    svm_rec = recall_score(predictions_SVM, Test_Y)

    print("SVM Accuracy Score -> ",svm_acc*100)
    print('SVM F-score -> ', svm_f*100)
    print('SVM Precision Score -> ', svm_prec*100)
    print('SVM Recall -> ', svm_rec*100)

    # Appending achieved SVM metrics to database
    stats['svm']['acc'].append(svm_acc)
    stats['svm']['f1'].append(svm_f)
    stats['svm']['prec'].append(svm_prec)
    stats['svm']['rec'].append(svm_rec)
    print('---------------------------------------')

    # Logistic Regression
    l_reg = LogisticRegression()
    l_reg.fit(Train_X_Tfidf, Train_Y)

    # Getting Metrics for LR
    predictions_l_reg = l_reg.predict(Test_X_Tfidf)
    lg_acc = accuracy_score(predictions_l_reg, Test_Y)
    lg_f = f1_score(predictions_l_reg, Test_Y)
    lg_prec = precision_score(predictions_l_reg, Test_Y)
    lg_rec = recall_score(predictions_l_reg, Test_Y)

    print("Logistic Regression Accuracy Score -> ", lg_acc*100)
    print('Logistic Regression F-score -> ', lg_f*100)
    print('Logistic Regression Precision Score -> ', lg_prec*100)
    print('Logistic Regression Recall -> ', lg_rec*100)

    # Appending achieved LR metrics to database
    stats['lg']['acc'].append(lg_acc)
    stats['lg']['f1'].append(lg_f)
    stats['lg']['prec'].append(lg_prec)
    stats['lg']['rec'].append(lg_rec)
    break


# Calculating and adding average stats to classifier stats
for alg in stats:
    stats[alg]['avg'] = {
        'acc': sum(stats[alg]['acc']) / 10,
        'f1': sum(stats[alg]['f1']) / 10,
        'prec': sum(stats[alg]['prec']) / 10,
        'rec': sum(stats[alg]['rec']) / 10
    }
#db_save(stats, 'exp/results/stats_t2.json')
# Saving final stats for all evaluations with each algorithm
#db_save(stats, 'exp/results/classifier_char.json')