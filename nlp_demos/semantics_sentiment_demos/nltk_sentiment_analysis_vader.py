# Using VADER to analyze sentiment
import nltk
nltk.download('vader_lexicon')


from nltk.sentiment.vader import SentimentIntensityAnalyzer
sid = SentimentIntensityAnalyzer()


# Use VADER sid to analyze some example text
string = "We're finally getting some rain, at least."
string2 = "We need help NOW!! Waters rising fast, we are scared."
print(sid.polarity_scores(string))
print(sid.polarity_scores(string2))


# Apply VADER to a file with amazon reviews:
import pandas as pd
df = pd.read_csv('../TextFiles/amazonreviews.tsv',sep='\t')


df['label'].value_counts()
df.dropna(inplace=True)
blanks = []
for i,lb,rv in df.itertuples():
    if type(rv) == str:
        if rv.isspace():
            blanks.append(i)
df.drop(blanks, inplace=True)


# Check polarity score for the first item in the list
sid.polarity_scores(df.iloc[0]['review'])


# Add polarity scores to the data frame like this:
df['scores'] = df['review'].apply(lambda review: sid.polarity_scores(review))
df.head()

# Create a separate column for the compound score
df['compound'] = df['scores'].apply(lambda d: d['compound'])
df.head()

# Now let's see how the compound score from VADER compares with the known labels
df['comp_score'] = df['compound'].apply(lambda c: 'pos' if c >=0 else 'neg')
df.head()


from sklearn.metrics import accuracy_score,confusion_matrix,classification_report
print(accuracy_score(df['label'], df['comp_score']))
print(confusion_matrix(df['label'], df['comp_score']))
print(classification_report(df['label'], df['comp_score']))





