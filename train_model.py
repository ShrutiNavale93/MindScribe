import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import pickle

data = pd.read_csv("emotion_data.csv")

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(data["text"])
y = data["emotion"]

model = LogisticRegression()
model.fit(X, y)

pickle.dump(model, open("emotion_model.pkl", "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))

print("Model trained successfully")
