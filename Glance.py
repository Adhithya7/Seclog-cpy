import nltk
import random
import pickle
import os

from nltk.tokenize import word_tokenize
from nltk.probability import ELEProbDist, FreqDist
from nltk import NaiveBayesClassifier
from nltk.util import ngrams
from nltk.classify.scikitlearn import SklearnClassifier
from nltk.classify import ClassifierI

from sklearn.naive_bayes import MultinomialNB, GaussianNB, BernoulliNB
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.svm import SVC, LinearSVC, NuSVC
from statistics import mode

homedir = os.environ['HOME']
pickle_path = homedir + '/mon/pix/pixapp/'

tokens1 = []
tokens = []
tokensrep = []
passwords = []
data = []
data1 = []
data2 = []
log_data = []
passwordsn = []
tokensn = []
all_words = []
                                                      
class VoteClassifier(ClassifierI):
    def __init__(self, *classifiers):
        self.classifiers = classifiers
    
    def classify(self, features):
        votes = []
        for c in self.classifiers:
            v = c.classify(features)
            votes.append(v)
        return votes[2]
    
    def confidence(self,features):
        votes = []
        for c in self.classifiers:
            v = c.classify(features)
            votes.append(v)
        votesn = votes.count(mode(votes))
        conf = (votesn / len(votes)) * 100
        return conf

def generate_ngrams(word, n, j):
    ngrams_list = ngrams(word, n) 
    ngrams_list = list(ngrams_list)
    for i in range(len(ngrams_list)):
        ngrams_list[i] = ''.join(ngrams_list[i])
        if (j==1):
            continue
        else:
            log_data.append(ngrams_list[i])
    return ngrams_list

def find_features(combo):
    words = set(combo)
    features = {}
    for w in words:
        features[w] = (w in log_data)
    return features

def detect_mod(text):
    feats = find_features(text)
    dtect1 = voted_classifier.classify(feats)
    dtect2 = voted_classifier.confidence(feats)
    return list((dtect1,dtect2))

token_data_f = open(pickle_path + 'tokenglance.pickle','rb')
tokens = pickle.load(token_data_f)
token_data_f.close()

log_data_f = open(pickle_path + 'logglance.pickle','rb')
log_data = pickle.load(log_data_f)
log_data_f.close()

feature_sets_f = open(pickle_path + 'glancefs.pickle','rb')
feature_sets = pickle.load(feature_sets_f)
feature_sets_f.close()

classifier_f = open(pickle_path + "nbglance.pickle","rb")
classifier = pickle.load(classifier_f)
classifier_f.close()

classifier_f = open(pickle_path + "mnbglance.pickle","rb")
MultinomialNB_classifier = pickle.load(classifier_f)
classifier_f.close()

classifier_f = open(pickle_path + "bnbglance.pickle","rb")
BernoulliNB_classifier = pickle.load(classifier_f)
classifier_f.close()
 
classifier_f = open(pickle_path + "sgdglance.pickle","rb")
SGDClassifier_classifier = pickle.load(classifier_f)
classifier_f.close()

classifier_f = open(pickle_path + "lsvcglance.pickle","rb")
LinearSVC_classifier = pickle.load(classifier_f)
classifier_f.close()

voted_classifier = VoteClassifier(classifier,
                                  MultinomialNB_classifier,
                                  BernoulliNB_classifier,
                                  SGDClassifier_classifier,
                                  LinearSVC_classifier) 

