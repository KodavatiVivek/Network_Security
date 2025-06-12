import os
import sys
import json

from dotenv import load_dotenv
from urllib.parse import quote_plus

# Load environment variables from a .env file
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

import certifi
import pymongo

# Internal project logging and exception modules
from Networksecurity.logging.logger import logging
from Networksecurity.exceptions.exception import NetworkSecurityException

# Get CA cert path for secure TLS connection
ca = certifi.where()

logging.info("Connecting to MongoDB securely...")
logging.info("ETL process started...")

class NetworkDataExtract:
    def __init__(self):
        try:
            # Placeholder constructor (can extend for future setup)
            pass
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def cv_to_json_converter(self, csv_file_path):
        """
        Convert a CSV file into JSON-like dictionary records.
        """
        logging.info(f"Converting CSV file {csv_file_path} to JSON format...")
        if not os.path.exists(csv_file_path):
            logging.error(f"CSV file {csv_file_path} does not exist.")
            raise NetworkSecurityException(f"CSV file {csv_file_path} does not exist.", sys)

        try:
            import pandas as pd
            df = pd.read_csv(csv_file_path)
            df.reset_index(drop=True, inplace=True)
            records = df.to_dict(orient='records')
            return records
        except Exception as e:
            logging.error(f"Error converting CSV to JSON: {e}")
            raise NetworkSecurityException(e, sys)

    def push_data_to_mongodb(self, database, records, collection):
        """
        Push the list of dictionary records into the specified MongoDB collection.
        """
        logging.info(f"Pushing data to MongoDB...")

        try:
            self.database = database
            self.collection = collection
            self.records = records

            import ssl
            # Create an SSL context for secure TLS connection (required by MongoDB Atlas)
            ssl_context = ssl.create_default_context(cafile=ca)
            ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2



            # Create MongoDB client using the SSL context
            self.mongo_client = pymongo.MongoClient(
                uri,
                tls=True,
                tlsCAFile=ca,
                
            )
            self.mongo_client.admin.command('ping')

            # Select database and collection
            logging.info(f"Configuring database: {self.database}, collection: {self.collection}")
            self.database = self.mongo_client[self.database]
            self.collection = self.database[self.collection]

            # Insert all records
            self.collection.insert_many(self.records)
            logging.info(f"Data pushed to MongoDB collection '{self.collection.name}' successfully.")
            return len(self.records)

        except Exception as e:
            logging.error(f"Error pushing data to MongoDB: {e}")
            raise NetworkSecurityException(e, sys)

# === Main script execution ===
if __name__ == "__main__":
    try:
        network_data_extractor = NetworkDataExtract()

        # Define path to CSV file
        csv_file_path = "Network_Data/phisingData.csv"

        # Convert CSV to JSON records
        records = network_data_extractor.cv_to_json_converter(csv_file_path)
        logging.info(f"Number of records to be pushed: {len(records)}")

        # MongoDB target
        database = "NetworkSecurity_Vivek"
        collection = "NetworkData_Records"

        # Push records into MongoDB
        count = network_data_extractor.push_data_to_mongodb(database, records, collection)
        logging.info(f"Total records pushed to MongoDB: {count}")
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        sys.exit(1)