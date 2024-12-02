#-------------------------------------------------------------------------
# AUTHOR: Armin Erika Polanco
# FILENAME: search_engine.py
# SPECIFICATION: Search Engine w/ Inverted Index
# FOR: CS 4250 - Assignment #4, Question 5
# TIME SPENT: 2 hours
#-----------------------------------------------------------*/

import re
import pymongo
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['search_engine']
documents_collection = db['documents']
terms_collection = db['terms']

# Sample Documents
documents = [
    "After the medication, headache and nausea were reported by the patient.",
    "The patient reported nausea and dizziness caused by the medication.",
    "Headache and dizziness are common effects of this medication.",
    "The medication caused a headache and nausea, but no dizziness was reported."
]

# Preprocessing Function
def preprocess(text):
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)  
    # Tokenize into words
    tokens = text.split()
    unigrams = tokens
    # Create bigrams
    bigrams = [' '.join(tokens[i:i+2]) for i in range(len(tokens)-1)]
    # Create trigrams
    trigrams = [' '.join(tokens[i:i+3]) for i in range(len(tokens)-2)]
    return unigrams + bigrams + trigrams

# Indexing Documents
documents_collection.drop()
terms_collection.drop()

for doc_id, content in enumerate(documents, 1):
    terms = preprocess(content)
    documents_collection.insert_one({"_id": doc_id, "content": content})
    for pos, term in enumerate(terms):
        terms_collection.update_one(
            {"term": term},
            {"$addToSet": {"docs": {"doc_id": int(doc_id), "pos": int(pos)}}},
            upsert=True
        )

# Build TF-IDF matrix
vectorizer = TfidfVectorizer(lowercase=True, tokenizer=preprocess, token_pattern=None, stop_words=None)
tfidf_matrix = vectorizer.fit_transform(documents)
feature_names = vectorizer.get_feature_names_out()

# Inverted Index with TF-IDF
for term_idx, term in enumerate(feature_names):
    term_docs = tfidf_matrix[:, term_idx].nonzero()[0]
    term_data = []
    for doc_id in term_docs:
        tfidf_value = float(tfidf_matrix[doc_id, term_idx])  # Convert TF-IDF to float
        term_data.append({"doc_id": int(doc_id + 1), "tfidf": tfidf_value})
    terms_collection.update_one(
        {"term": term},
        {"$set": {"pos": int(term_idx), "docs": term_data}},
        upsert=True
    )

# Query and Rank Documents
def rank_documents(query):
    query_vector = vectorizer.transform([query]).toarray()[0]
    results = []

    for doc in documents_collection.find():
        doc_vector = tfidf_matrix[doc["_id"] - 1].toarray()[0]
        dot_product = np.dot(query_vector, doc_vector)
        query_magnitude = np.linalg.norm(query_vector)
        doc_magnitude = np.linalg.norm(doc_vector)
        if query_magnitude == 0 or doc_magnitude == 0:
            cosine_similarity = 0
        else:
            cosine_similarity = dot_product / (query_magnitude * doc_magnitude)
        results.append((doc["content"], cosine_similarity))

    return sorted(results, key=lambda x: x[1], reverse=True)

# Example Queries
queries = {
    "q1": "Nausea and dizziness",
    "q2": "effects",
    "q3": "Nausea was reported",
    "q4": "dizziness",
    "q5": "the medication"
}

for q_id, query in queries.items():
    print(f"Results for {q_id}: {query}")
    for doc, score in rank_documents(query):
        print(f"{doc}, {score:.2f}")
    print()