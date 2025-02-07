# You must have spacy pip installed (or conda installed)

import spacy
nlp = spacy.load('en_core_web_sm')


doc1 = nlp(u'I am a runner running in a race because I love to run since I ran today.')
for token in doc1:
    print(f"{token.text:{12}} {token.pos_:{6}} {token.lemma:<{22}} {token.lemma_}")




