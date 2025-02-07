# You must have spacy pip installed (or conda installed)
import spacy
nlp = spacy.load('en_core_web_sm')

# Stop words are the most common words in the language

print(nlp.Defaults.stop_words)
len(nlp.Defaults.stop_words)
nlp.vocab['is'].is_stop
nlp.vocab['mystery'].is_stop


# We can also add vocab to the stop words
nlp.Defaults.stop_words.add('btw')
nlp.vocab['btw'].is_stop = True
len(nlp.Defaults.stop_words)
nlp.vocab['btw'].is_stop


# We can remove vocab from the stop words
nlp.Defaults.stop_words.remove('her')
nlp.vocab['her'].is_stop = False
nlp.vocab['her'].is_stop





