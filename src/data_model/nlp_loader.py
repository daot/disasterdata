import spacy
import inflect
import nltk

'''
before running make sure to do:
python -m spacy download en_core_web_sm
'''

# Prepare spacy stuff
nlp = spacy.load('en_core_web_sm')

# Prepare inflect stuff
p = inflect.engine()

# NLTK stuff
tt = nltk.tokenize.TweetTokenizer()
