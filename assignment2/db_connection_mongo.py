#-------------------------------------------------------------------------
# AUTHOR: Armin Erika Polanco
# FILENAME: db_connection_mongo.py
# SPECIFICATION: Performing specific MongoDB CRUD operations
# FOR: CS 4250 - Assignment #2
# TIME SPENT: 3 hours
#-----------------------------------------------------------*/

#IMPORTANT NOTE: DO NOT USE ANY ADVANCED PYTHON LIBRARY TO COMPLETE THIS CODE SUCH AS numpy OR pandas. You have to work here only with
# standard arrays

#importing some Python libraries
from pymongo import MongoClient
import string

def connectDataBase():

    # Create a database connection object using pymongo
    client = MongoClient("mongodb://localhost:27017/")
    db = client["assignmentDB"]  
    collection = db["documents"]  
    
    return collection 

def createDocument(col, docId, docText, docTitle, docDate, docCat):

    # Create a dictionary (document) to count how many times each term appears in the document.
    # Use space " " as the delimiter character for terms and remember to lowercase them.
    translator = str.maketrans('', '', string.punctuation)
    terms = docText.lower().translate(translator).split()

    # Create a list of dictionaries (documents) with each entry including a term, its occurrences, and its num_chars. Ex: [{term, count, num_char}]
    term_data = {}
    for term in terms:
        if term in term_data:
            term_data[term]["count"] += 1
        else:
            term_data[term] = {
                "term": term,
                "count": 1,
                "num_chars": len(term)  
            }
    terms_list = [{"term": m, "count": n["count"], "num_chars": n["num_chars"]} for m, n in term_data.items()]

    # Producing a final document as a dictionary including all the required fields
    document = {
        "_id": docId,
        "text": docText,
        "title": docTitle,
        "date": docDate,
        "category": docCat,
        "terms": terms_list  # Insert the terms list
    }

    # Insert the document
    col.insert_one(document)

def deleteDocument(col, docId):

    # Delete the document from the database
    result = col.delete_one({"_id": docId})

def updateDocument(col, docId, docText, docTitle, docDate, docCat):

    # Delete the document
    deleteDocument(col, docId)

    # Create the document with the same id
    createDocument(col, docId, docText, docTitle, docDate, docCat)

def getIndex(col):

    # Query the database to return the documents where each term occurs with their corresponding count. Output example:
    # {'baseball':'Exercise:1','summer':'Exercise:1,California:1,Arizona:1','months':'Exercise:1,Discovery:3', ...}
    # We are simulating an inverted index here in memory.
    inverted_index = {}
    documents = col.find()
    
    for doc in documents:
        title = doc['title']  
        for term_entry in doc['terms']:
            term = term_entry['term']
            count = term_entry['count']
            
            if term in inverted_index:
                inverted_index[term] += f",{title}:{count}" 
            else:
                inverted_index[term] = f"{title}:{count}"
    
    sorted_inverted_index = {k: inverted_index[k] for k in sorted(inverted_index)}
    
    return sorted_inverted_index