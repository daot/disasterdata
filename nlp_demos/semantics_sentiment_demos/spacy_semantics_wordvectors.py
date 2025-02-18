# Before we proceed, download either medium or large spacy english models:
# python -m spacy download en_core_web_md
# python -m spacy download en_core_web_lg
import spacy
nlp = spacy.load('en_core_web_lg')


# Demonstrating how word vectors can hold information about word similarity etc. 
from scipy import spatial
cosine_similarity = lambda vec1,vec2: 1-spatial.distance.cosine(vec1,vec2)
king = nlp.vocab['king'].vector
man = nlp.vocab['man'].vector
woman = nlp.vocab['woman'].vector


# king - man + woman ---> NEW VECTOR similar to queen, princess, highness, etc
new_vector = king - man + woman
computed_similarities = []

# For ALL the words in my vocab
for ID in nlp.vocab.vectors:
    word = nlp.vocab[ID]
    if word.has_vector:
        if word.is_lower:
            if word.is_alpha:
                similarity = cosine_similarity(new_vector, word.vector)
                computed_similarities.append((word, similarity))


# Sort them by similarity
computed_similarities = sorted(computed_similarities, key=lambda item:-item[1]) # Descending order


# Print the first 10 words
print([t[0].text for t in computed_similarities[:10]])


# Trying another one, doctor + teeth = dentist?
doctor = nlp.vocab['doctor'].vector
teeth = nlp.vocab['teeth'].vector
new_vector = doctor+teeth

computed_similarities = []

# For ALL the words in my vocab
for ID in nlp.vocab.vectors:
    word = nlp.vocab[ID]
    if word.has_vector:
        if word.is_lower:
            if word.is_alpha:
                similarity = cosine_similarity(new_vector, word.vector)
                computed_similarities.append((word, similarity))

computed_similarities = sorted(computed_similarities, key=lambda item:-item[1]) # Descending order
# Print the first 10 words
print([t[0].text for t in computed_similarities[:10]])


# And another one, horse + desert = camel?
horse = nlp.vocab['horse'].vector
desert = nlp.vocab['desert'].vector
new_vector = horse+desert

computed_similarities = []

# For ALL the words in my vocab
for ID in nlp.vocab.vectors:
    word = nlp.vocab[ID]
    if word.has_vector:
        if word.is_lower:
            if word.is_alpha:
                similarity = cosine_similarity(new_vector, word.vector)
                computed_similarities.append((word, similarity))

computed_similarities = sorted(computed_similarities, key=lambda item:-item[1]) # Descending order
# Print the first 10 words
print([t[0].text for t in computed_similarities[:10]])





