import sklearn.datasets as skd
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn import metrics
from sklearn.metrics import accuracy_score
import os

#Determination
catagories = ['Carpenter', 'Electration', 'painter', 'Plumber'] #The classifications
Training_set = skd.load_files('/home/venom/Documents/StemCapProject/Handy/flask application/handy/AI/CraftsnNames', categories=catagories) #The set of collected data

#Vectorization
#*tokenizing*
Vector = CountVectorizer() #defining the counting vectorizer function
X_train_tf = Vector.fit_transform(Training_set.data) #counting the training set --> Making every featuer *word* mapped to a unique numper 

#*frequancy*
tfidf_transfomer = TfidfTransformer() 
X_train_tfdf = tfidf_transfomer.fit_transform(X_train_tf) #getting the frequant words from the training set which has been tokinized

#creatinf the AI model
features = X_train_tfdf #The processed data from the dataset
categories = Training_set.target #The available categories in the dataset 

classifier = MultinomialNB().fit(features, categories)


#testing
#docs_new = ["I have a water leakage in the bathroom tape", "fixing the door and chair", "Painting the walls",  "Fixing the wiring bulbs and lamps"]
#X_new_counts = Vector.transform(docs_new)
#X_new_tfidf = tfidf_transfomer.transform(X_new_counts)
#predicted = classifier.predict(X_new_tfidf)

def run(desc):
	X_new_counts = Vector.transform(desc)
	X_new_tfidf = tfidf_transfomer.transform(X_new_counts)
	predicted = classifier.predict(X_new_tfidf)
	
	for d in desc:
		dn = desc.index(d)
		print(f""" {desc[dn]} : {Training_set.target_names[predicted[dn]]} """)
		return desc[dn], Training_set.target_names[predicted[dn]]
	

# docs_new, predicted = run(["I have a water leakage in the bathroom tape"])

### add to data set
def Modify(major, desc):
	PATH = '/home/venom/Documents/StemCapProject/Handy/flask application/handy/AI/CraftsnNames'
	CATEGORY = major
	PATH = os.path.join(PATH, CATEGORY)
	FILE = os.listdir(PATH)[0]
	PATH = os.path.join(PATH, FILE)
	print(PATH)
	with open(PATH, 'a+') as file_object:
		file_object.seek(0)
		data = file_object.read(100)
		if len(data) > 0:
			file_object.write("\n")
		file_object.write(f"{desc} \n")