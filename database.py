from pymongo import MongoClient
import json
import bson
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix
import sys
import logging

class Database:
    db_url = "mongodb+srv://dali:dali2908@medicall.x4hyrxq.mongodb.net/?retryWrites=true&w=majority"
    cluster_name = "sensors"
    collection_name = "patients"
    predictor_filepath = './data/qt_dataset.csv'
    db = 0
    collection = 0
    predictor = 0

    def __init__(self):
        try : 
            cluster = MongoClient(self.db_url)
        except : 
            logging.error("Cannot connect to Mongo Database. Please check connection and retry. \n")
            sys.exit(1)

        self.db = cluster[self.cluster_name]
        self.collection = self.db[self.collection_name]
        self.initPredictor()

    def insert_one(self, obj : dict):
        req = self.format_request(obj)
        self.collection.insert_one(req)

    def initPredictor(self):
        df = pd.read_csv(self.predictor_filepath)
        df.set_index('ID',inplace=True)
        df['Result'].replace(['Positive','Negative'],[1,0],inplace=True)
        x = df.drop('Result',axis=1)
        y = df['Result']
        x_train,x_test,y_train,y_test = train_test_split(x,y,test_size=0.3)
        #We choose kernel='rbf'
        self.predictor = SVC(C=5, gamma='auto')
        self.predictor.fit(x_train,y_train)

    def predictSickness(self, data):
        d = {'Oxy': [data["oxy"]], 'Pulse': [data["pulse"]], 'Temp': [data["temp"]]}
        df = pd.DataFrame(data=d)
        result = self.predictor.predict(df)[0]
        if(result):
            return "Our AI model thinks this patient is sick."
        else:
            return "Our AI model thinks this patient is healthy."

    def format_request(self, data) -> dict:
        user = data['user']
        sensors = data['sensors']
        post = {
            "_id": bson.ObjectId(),
            "age": user["age"],
            "name": user["name"],
            "sex": user["sex"],
            "email": user["email"],
            "phone": user["phone"],
            "temp": sensors["temp"],
            "oxy": sensors["oxy"],
            "pulse": sensors["pulse"],
            "height": sensors["height"],
            "prediction" : self.predictSickness(sensors)
        }
        return post