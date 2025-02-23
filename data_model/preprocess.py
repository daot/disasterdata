from nlp_loader import nlp,tt,p
import string
import emoji
import re

punct = set(string.punctuation + '''…'"`’”“''' + '')
stop = set(nlp.Defaults.stop_words)


def strip_punct(text):
    text = re.sub('[^A-Za-z0-9 ]+','', text)
    return text


def bsk_preprocessor(text, punct=punct, stop=stop):
    text = text.lower()
    tokens = tt.tokenize(text)

    # pre-split the hashtags
    tokens = [t.strip('#') if t.startswith('#') else t for t in tokens]

    # remove user mentions and urls
    tokens = [t for t in tokens if not (t.startswith('@') or t.startswith('http'))]

    final_tokens = []
    for t in tokens:
        # convert emojis to their descriptions
        if t in emoji.EMOJI_DATA:
            final_tokens.append(re.sub('_', ' ', emoji.demojize(t).strip(':')))
        # remove single punctuations
        elif t in punct:
            pass
        # convert numbers to text
        elif t.isnumeric():
            final_tokens.append(p.number_to_words(t))
        # skip stopwords and empty strings, include anything else
        elif t and t not in stop:
            final_tokens.append(strip_punct(t))
    return ' '.join(final_tokens)

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
    return locs

def preprocess_dataframe(df):
    df = clean_dataframe(df) # remove blanks and empty strings
    df['locations'] = df['text'].apply(locations) # Get the locations
    df['cleaned'] = df['text'].apply(bsk_preprocessor) # Use this one to train the data
    return df
