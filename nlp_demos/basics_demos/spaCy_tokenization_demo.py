# You must have spacy pip installed (or conda installed)


import spacy
nlp = spacy.load('en_core_web_sm') # This is the small english core version, there is also lg version
doc = nlp(u'Tesla is looking at buying U.S. startup for $6 million')
for token in doc:
    print(token.text,token.pos_,token.dep_)


doc2 = nlp(u"Tesla isn't looking into startups anymore.")
for token in doc2:
    print(token.text,token.pos_,token.dep_)


doc3 = nlp(u'Although commmonly attributed to John Lennon from his song "Beautiful Boy", \
the phrase "Life is what happens to us while we are making other plans" was written by \
cartoonist Allen Saunders and published in Reader\'s Digest in 1957, when Lennon was 17.')
life_quote = doc3[16:30]
print(life_quote)


doc4 = nlp(u"This is the first sentence. This is another sentence. This is the last sentence.")
for sentence in doc4.sents:
    print(sentence)


# Tokenization Basics

mystring = '"We\'re moving to L.A.!"'
print(mystring)
doc = nlp(mystring)
for token in doc:
    print(token.text)


doc2 = nlp(u'We\'re here to help! Send snail-mail, email support@oursite.com, or visit us at https://www.oursite.com!')
for t in doc2:
    print(t.text)


doc3 = nlp(u'A 5km NYC cab ride costs $10.30')
for t in doc3:
    print(t)



doc4 = nlp(u"Let's visit St. Louis in the U.S. next year.")
for t in doc4:
    print(t)
len(doc4)


doc5 = nlp(u'Apple to build a Hong Kong factory for $6 million')
for token in doc5:
    print(token.text, end=" | ")

for entity in doc5.ents:
    print(entity)
    print(entity.label_)
    print(str(spacy.explain(entity.label_)))
    print('\n')


doc6 = nlp(u"Autonomous cars shift insurance liability toward manufacturers.")
for chunk in doc6.noun_chunks:
    print(chunk)


# Tokenization Visualization

from spacy import displacy

doc = nlp(u"Over the last quarter, Apple sold nearly 20 thousand iPods for a profit of $6 million.")
displacy.render(doc, style='ent')





