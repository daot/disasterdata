# Use conda install scikit-learn or pip install scikit-learn
import numpy as np
import pandas as pd # This library allows us to read in csv files


df = pd.read_csv('../TextFiles/smsspamcollection.tsv',sep='\t') # Sep parameter since this is a tsv or tab separated values
df.head() # Display the first 5 rows
df.isnull().sum() # Check for missing data; if any values are not 0 we know we are missing some data
len(df) # Check how many rows are in the data set
df['label'].unique() # Get the label types in this dataset
df['label'].value_counts() # Count how many of each label type are in the dataset


# Now let's split into test data and training data
# Not yet looking at the text, only looking at numerical data in the dataset
from sklearn.model_selection import train_test_split


# y is our label
y = df['label']

# X is our feature data
X = df[['length','punct']] # Note the use of double brackets, passing a list of columns

# Split the feature data and labels
# Note that we can repeat the same split by using the same random_state value
X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.3,random_state=42) 


X_train.shape # Returns the number of rows and columns
X_test.shape


# Training a model from scikit learn
from sklearn.linear_model import LogisticRegression
lr_model = LogisticRegression(solver='lbfgs')


# Fit to the training data
# Note we don't need to set it equal to any variable
lr_model.fit(X_train,y_train)


# Testing the accuracy of our model
from sklearn import metrics
predictions = lr_model.predict(X_test)


# We need to compare the predictions against y_test
# Print a confusion matrix
print(metrics.confusion_matrix(y_test,predictions))


# You can make the confusion matrix less confusing by adding labels:
df = pd.DataFrame(metrics.confusion_matrix(y_test,predictions), index=['ham','spam'], columns=['ham','spam'])


# Can also print out classification report:
print(metrics.classification_report(y_test, predictions))


# Printing out the accuracy (not as useful as other metrics depending on the dataset)
print(metrics.accuracy_score(y_test, predictions))


# Now let's try training another model
from sklearn.naive_bayes import MultinomialNB
nb_model = MultinomialNB()
# Same syntax as before, fit it to the training data
nb_model.fit(X_train, y_train)


predictions = nb_model.predict(X_test)
print(metrics.confusion_matrix(y_test, predictions))


# And trying another one
from sklearn.svm import SVC


svc_model = SVC(gamma='auto')
svc_model.fit(X_train, y_train)
predictions = svc_model.predict(X_test)
print(metrics.confusion_matrix(y_test, predictions))





