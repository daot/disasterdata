
import spacy
nlp = spacy.load('en_core_web_sm')

# A function to print out named entities in a given doc object
def show_ents(doc):
    if doc.ents:
        for ent in doc.ents:
            print(f"{ent.text} - {ent.label_} - {spacy.explain(ent.label_)}")
    else:
        print("No entities found")


# A doc with no entities
doc = nlp(u"Hi, how are you?")
print(doc.text)
show_ents(doc)


# A doc that does have entities
doc = nlp(u"May I go to Washington, DC next May to see the Washington Monument?")
print(doc.text)
show_ents(doc)


# Another example
doc = nlp(u"May I have 500 dollars of Microsoft stock?")
print(doc.text)
show_ents(doc)


# In some cases we may want to add a named entity to be recognized
doc = nlp(u"Tesla to build a U.K. factory for $6 million.")
print(doc.text)
show_ents(doc) # Note that right now spacy does not recognize Tesla as an entity


from spacy.tokens import Span
ORG = doc.vocab.strings[u"ORG"]
new_ent = Span(doc,0,1,label=ORG) # Name of doc object, start position of the span, stop position of the span, and label of entity
doc.ents = list(doc.ents) + [new_ent] 


show_ents(doc)



# Now how to add multiple options
doc = nlp(u'Our company plans to introduce a new vacuum cleaner. '
          u'If successful, the vacuum-cleaner will be our first product.')
print(doc.text)
show_ents(doc)


# Import and create a phrase matcher object
from spacy.matcher import PhraseMatcher
matcher = PhraseMatcher(nlp.vocab)


phrase_list = ['vacuum cleaner', 'vacuum-cleaner']
phrase_patterns = [nlp(text) for text in phrase_list]


matcher.add('newproduct',phrase_patterns)
found_matches = matcher(doc)


from spacy.tokens import Span
# Add them as a product
PROD = doc.vocab.strings[u"PRODUCT"]
new_ents = [Span(doc,match[1],match[2],label=PROD) for match in found_matches]


# Add to the existing entities for our doc object
doc.ents = list(doc.ents) + new_ents
print(doc.text)
show_ents(doc)


# If we want to check how often certain labels appear in a document
doc = nlp(u"I originally paid $29.95 for this toy, but it is now marked down by 10 dollars.")
print(doc.text)
money_mentions = len([ent for ent in doc.ents if ent.label_=="MONEY"])
print(f"MONEY occurrences: {money_mentions}")





