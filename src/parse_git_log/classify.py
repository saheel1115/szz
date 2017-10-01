import sys
import os
import re
import nltk
from sklearn import metrics  #clustering
from nltk.corpus import stopwords #filtering, stop words
from gensim import corpora, models, similarities, matutils #lda
#import enchant
from nltk.stem.wordnet import WordNetLemmatizer
from collections import Counter
from sklearn.cluster import KMeans
import operator
from collections import namedtuple
import argparse
import fnmatch

from nltk.classify.scikitlearn import SklearnClassifier
from sklearn.metrics import classification_report

from sklearn import svm

def dialogue_act_features(sentence):
    """
        Extracts a set of features from a message.
    """
    features = {}
    tokens = nltk.word_tokenize(sentence)
    for t in tokens:
        if not features.has_key(t.lower()):
            features[t.lower()] = 0

        features[t.lower()] += 1
    return features


def extractFeature(commits):

    lmtzr = WordNetLemmatizer()
    stoplist = stopwords.words('english') #+ ["fix", "bug", "error", "issue", "mistake", "blunder", "incorrect", "fault", "defect", "flaw", "bugfix", "bugfix:"]

    featuresets = []

    for co in commits:
        #print co
        if co is None:
            continue
        logStr = co.getLog().strip()

        imp_words = [lmtzr.lemmatize(word) for word in logStr.lower().split() \
            if ((word not in stoplist)) ]

        bug_desc = ' '.join([str(x) for x in imp_words])
        print "logStr = ", logStr
        print "bug_desc = ", bug_desc
        co.featureset = dialogue_act_features(bug_desc)

    return commits

'''
algo option: 1) LogisticRegression by default
             

'''
def runClassifier(train, test, algo='LogisticRegression'):

    train_features = []
    
    for co in train:
        train_features.append((co.featureset, co.isbug))
        

    test_features = []
    for c in test:
        if c is None:
            continue
        test_features.append(c.featureset)

    
    if algo == 'LogisticRegression':
        print 'LogisticRegression'
        try:
            from sklearn.linear_model.sparse import LogisticRegression
        except ImportError:     # separate sparse LR to be removed in 0.12
            from sklearn.linear_model import LogisticRegression
        
        classif = SklearnClassifier(LogisticRegression(C=1000))
    else:
        # if not logistic, assume SVM for now
        # SVM with a Linear Kernel and default parameters
        from sklearn.svm import LinearSVC
        print 'svm'
        classif = SklearnClassifier(LinearSVC())

    classif.train(train_features)

    try:
        p = classif.classify_many(test_features)
    except AttributeError:
        p = classif.batch_classify(test_features)
    
    test_commits = []

    for idx, val in enumerate(p):
        t = test[idx]
        t.isbug = val
        test_commits.append(t)

    return test_commits
