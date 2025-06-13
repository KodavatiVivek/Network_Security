from Networksecurity.exceptions.exception import NetworkSecurityException
from Networksecurity.logging.logger import logging

from Networksecurity.entity.config_entity import DataIngestionConfig
from Networksecurity.entity.artifact_entity import DataIngestionArtifact

import os
import sys 
import pandas as pd
import numpy as np
import pymongo
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv
import certifi
from urllib.parse import quote_plus
import ssl


load_dotenv('.env')

# Securely parse credentials for MongoDB (handle special characters)
username = quote_plus(os.getenv("MON_MAIL"))
password = quote_plus(os.getenv("MON_PASS"))

# Exit if credentials are not found
if not username or not password:
    print("Error: Environment variables MON_MAIL and MON_PASS must be set")
    sys.exit(1)

# MongoDB connection URI (MongoDB Atlas)
uri = f"mongodb+srv://vivekchowdary678:{password}@cluster0.cpdb7m9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

ca = certifi.where()

class DataIngestion:
    def __init__(self,data_ingestion_config:DataIngestionConfig):
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    def export_collection_as_dataframe(self):
        """
        Read data from MongoDB and return as a DataFrame.
        """
        try:
            logging.info("Exporting collection as DataFrame")
            database_name = self.data_ingestion_config.database_name
            collection_name = self.data_ingestion_config.collection_name
            logging.info(f"Connecting to MongoDB database: {database_name}, collection: {collection_name}")
            self.mongo_client = pymongo.MongoClient(uri, tlsCAFile=ca,tls=True)
            collection = self.mongo_client[database_name][collection_name]

            logging.info("Fetching data from MongoDB collection")
            # Fetching data from the collection and converting it to a DataFrame
            logging.info("Converting MongoDB collection to DataFrame")

            df = pd.DataFrame(list(collection.find()))
            if "_id" in df.columns.to_list():
                df = df.drop(columns=["_id"], axis=1)

            df.replace({"na": np.nan}, inplace=True)
            return df
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def export_data_into_feature_store(self, dataframe: pd.DataFrame):
        try:
            logging.info("Exporting data into Feature Store")
            feature_store_file_path = self.data_ingestion_config.feature_store_file_path
            # Creating directory if it does not exist   
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path, exist_ok=True)
            logging.info(f"Saving DataFrame to {feature_store_file_path}")
            dataframe.to_csv(feature_store_file_path, index=False, header=True)
            return dataframe
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def split_data_as_train_test(self, dataframe: pd.DataFrame):
        try:
            logging.info("Splitting data into train and test sets")
            train_set, test_set = train_test_split(
                dataframe, test_size=self.data_ingestion_config.train_test_split_ratio
            )
            logging.info("Train-test split completed successfully")

            # Creating directories for train and test files
            dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)
            os.makedirs(dir_path, exist_ok=True)

            logging.info("Exporting train and test files")
            train_set.to_csv(
                self.data_ingestion_config.training_file_path, index=False, header=True
            )
            test_set.to_csv(
                self.data_ingestion_config.testing_file_path, index=False, header=True
            )

            return DataIngestionArtifact(
                trained_file_path=self.data_ingestion_config.training_file_path,
                test_file_path=self.data_ingestion_config.testing_file_path
            )
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
        
    def initiate_data_ingestion(self):
        try:
            df= self.export_collection_as_dataframe()
            logging.info("Exported collection as DataFrame successfully")
            df = self.export_data_into_feature_store(dataframe=df)
            logging.info("Data exported into feature store successfully")
            self.split_data_as_train_test(dataframe=df)
            logging.info("Data split into train and test sets successfully")
            data_ingestion_artifact = DataIngestionArtifact(
                trained_file_path=self.data_ingestion_config.training_file_path,
                test_file_path=self.data_ingestion_config.testing_file_path
            )

            logging.info("Data ingestion completed successfully")
            return data_ingestion_artifact
            
        except Exception as e:
            raise NetworkSecurityException(f"Failed to connect to MongoDB: {e}", sys)

