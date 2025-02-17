import numpy as np
import pandas as pd


# Read in the data frame
df = pd.read_csv('./lahaina-label.tsv',sep='\t')
df.head()


# Remove the empty points
df.dropna(inplace=True)


blanks = []
for i,lb,msg in df.itertuples():
    if msg.isspace():
        blanks.append(i)


df.drop(blanks,inplace=True)


# How many of each type
df['sentiment'].value_counts()


# Split the data to train and test sets
from sklearn.model_selection import train_test_split
X = df['text']
y = df['sentiment']
 X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.3,random_state=30)


# Create pipeline
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
text_clf = Pipeline([('tfidf',TfidfVectorizer()),('clf',LinearSVC())])


# Fit it to our training data
text_clf.fit(X_train,y_train)


# Measure the model's performance
predictions = text_clf.predict(X_test)
from sklearn.metrics import confusion_matrix,classification_report,accuracy_score
print('Performance with default LinearSVC:')
print(confusion_matrix(y_test,predictions))
print(classification_report(y_test,predictions))
print(accuracy_score(y_test,predictions))


# Try adjusting parameters
text_clf = Pipeline([('tfidf',TfidfVectorizer(sublinear_tf=True)),('clf',LinearSVC())])
text_clf.fit(X_train,y_train)
predictions = text_clf.predict(X_test)
print('Performance with TfidfVectorizer sublinear tf = True:')
print(confusion_matrix(y_test,predictions))
print(classification_report(y_test,predictions))
print(accuracy_score(y_test,predictions))


# Try adjusting parameters
from sklearn.svm import SVC
text_clf = Pipeline([('tfidf',TfidfVectorizer(sublinear_tf=True)),('clf',SVC())])
text_clf.fit(X_train,y_train)
predictions = text_clf.predict(X_test)
print('Performance with TfidfVectorizer sublinear tf = True and SVC:')
print(confusion_matrix(y_test,predictions))
print(classification_report(y_test,predictions))
print(accuracy_score(y_test,predictions))


# Try adjusting parameters
text_clf = Pipeline([('tfidf',TfidfVectorizer(sublinear_tf=True)),('clf',SVC(class_weight='balanced'))])
text_clf.fit(X_train,y_train)
predictions = text_clf.predict(X_test)
print('Performance with TfidfVectorizer sublinear tf = True and SVC class weight balanced:')
print(confusion_matrix(y_test,predictions))
print(classification_report(y_test,predictions))
print(accuracy_score(y_test,predictions))


# Try adjusting parameters
text_clf = Pipeline([('tfidf',TfidfVectorizer(sublinear_tf=True)),('clf',LinearSVC(class_weight='balanced'))])
text_clf.fit(X_train,y_train)
predictions = text_clf.predict(X_test)
print('Performance with TfidfVectorizer sublinear tf = True and LinearSVC class weight = balanced')
print(confusion_matrix(y_test,predictions))
print(classification_report(y_test,predictions))
print(accuracy_score(y_test,predictions))


# Test the prediction on new text
def predict_disaster(msg):
    prediction = text_clf.predict(msg)
    print('The category of this text is: ' + prediction[0])


example_post = ["Have you ever seen a dog swim?"]
print(example_post[0])
predict_disaster(example_post)


example_post = ["The fire destroyed everything..."]
print(example_post[0])
predict_disaster(example_post)





