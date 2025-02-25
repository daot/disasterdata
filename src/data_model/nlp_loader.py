import spacy
import inflect

'''
before running make sure to do:
python -m spacy download en_core_web_sm
'''

# globals
_nlp = None
_p = None

def get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load('en_core_web_sm')
    return _nlp

def get_p():
    global _p
    if _p is None:
        # Prepare inflect stuff
        _p = inflect.engine()
    return _p







