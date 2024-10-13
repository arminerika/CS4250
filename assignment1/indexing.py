#-------------------------------------------------------------------------
# AUTHOR: Armin Erika Polanco
# FILENAME: title of the source file
# SPECIFICATION: description of the program
# FOR: CS 4250 - Assignment #1
# TIME SPENT: how long it took you to complete the assignment
#-----------------------------------------------------------*/

#Importing some Python libraries
import csv
import math

documents = []

#Reading the data in a csv file
with open('assignment1/collection.csv', 'r') as csvfile:
  reader = csv.reader(csvfile)
  for i, row in enumerate(reader):
         if i > 0:  # skipping the header
            documents.append (row[0])

#Conducting stopword removal for pronouns/conjunctions. Hint: use a set to define your stopwords.
stopWords = {'I', 'and', 'She', 'They', 'her', 'their'}

for i, doc in enumerate(documents):
  for j, stop in enumerate(stopWords):
    documents[i] = documents[i].replace(stop,"").strip()
    
print(documents)

#Conducting stemming. Hint: use a dictionary to map word variations to their stem.
steeming = {
  "cats": "cat",
  "dogs": "dog",
  "loves": "love",
}

for i, doc in enumerate(documents):
  for j, stem in enumerate(steeming.keys()):
    documents[i] = documents[i].replace(stem,steeming[stem]).strip()
    
print(documents)

#Identifying the index terms.
terms = []
tokens = []

for i, doc in enumerate(documents):
  tokens.append(doc.split(" "))
  while '' in tokens[i]:
    tokens[i].remove('')
  for token in tokens[i]:
    if token not in terms:
      terms.append(token)

print(terms)

#Building the document-term matrix by using the tf-idf weights.
docTermMatrix = []

for i, doc in enumerate(tokens):
  TF = []
  IDF = []
  TF_IDF = []
  for term in terms:
    TF = doc.count(term) / len(tokens[i])
    tokenSet = list(map(set, tokens)) 
    wordsDocList = list(map(list, tokenSet)) 
    DF = sum(x.count(term) for x in wordsDocList)
    IDF = math.log(len(tokens) / DF, 10)
    TF_IDF.append(TF * IDF)
  docTermMatrix.append(TF_IDF)

#Printing the document-term matrix.
print(docTermMatrix)
