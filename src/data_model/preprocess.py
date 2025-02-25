from nlp_loader import nlp,tt,p
import string
import emoji
import re

stop = set(nlp.Defaults.stop_words)

def spacy_tokenize(text):
    return [t.text for t in nlp(text)]

def strip_punct(text):
    text = re.sub('[^A-Za-z0-9 ]+','', text)
    return text

def bsk_preprocessor(text, stop=stop):
    text = text.lower()
    text = re.sub(r"http\S+", "", text)  # remove urls
    text = re.sub(r"\@\w+|\#", "", text)  # remove user mentions and strip hashtags
    tokens = spacy_tokenize(text)

    final_tokens = []
    for t in tokens:
        if t.isspace() or len(t)==0: # don't add empty strings
            continue
        # convert emojis to their descriptions
        if t in emoji.EMOJI_DATA:
            final_tokens.append(re.sub('_', ' ', emoji.demojize(t).strip(':')))
        # convert numbers to text
        elif t.isnumeric():
            final_tokens.append(p.number_to_words(t))
        # skip stopwords and empty strings, include anything else
        elif t and t not in stop:
            temp = strip_punct(t)
            if temp:
                final_tokens.append(strip_punct(t))
    return " ".join(final_tokens)

# Remove empty spots in the data and empty strings
def clean_dataframe(df):
    df.dropna(inplace=True)
    blanks = []
    for i,lb,post in df.itertuples():
        if post.isspace():
            blanks.append(i)
    df.drop(blanks,inplace=True)
    return df

# Get the named entities that are locations from a document
def locations(text):
    doc = nlp(text)
    locs = []
    for ent in doc.ents:
        if ent.label_ == "GPE" or ent.label_ == "LOC":
            locs.append(ent.text)
    if len(locs)==0:
        locs.append("None")
    return locs

def preprocess_dataframe(df):
    df = clean_dataframe(df) # remove blanks and empty strings
    df['cleaned'] = df['text'].apply(bsk_preprocessor) # Use this one to train the data
    return df
