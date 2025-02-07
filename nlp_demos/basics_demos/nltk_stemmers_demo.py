# Be sure to pip install nltk before trying

import nltk

# Stemmers: essentially chopping off part of the word to read the "root" word
from nltk.stem.porter import PorterStemmer

p_stemmer = PorterStemmer()
words = ['run', 'runner', 'ran', 'runs', 'easily', 'fairly', 'fairness']
for word in words:
    print(f"{word} ---> {p_stemmer.stem(word)}")


from nltk.stem.snowball import SnowballStemmer
s_stemmer = SnowballStemmer(language='english')
for word in words:
    print(f"{word} ---> {s_stemmer.stem(word)}")





