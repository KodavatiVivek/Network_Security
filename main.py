"""import pymongo
import certifi
from urllib.parse import quote_plus
from dotenv import load_dotenv
import os

load_dotenv()

username = quote_plus(os.getenv("MON_MAIL"))
password = quote_plus(os.getenv("MON_PASS"))

uri = f"mongodb+srv://{username}:{password}@cluster0.cpdb7m9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

try:
    client = pymongo.MongoClient(uri, tls=True, tlsCAFile=certifi.where())
    print("Pinging MongoDB...")
    client.admin.command('ping')
    print("✅ MongoDB Atlas connection successful!")
except Exception as e:
    print("❌ Connection failed:", e)"""

from Networksecurity.components.data_ingestion import DataIngestion
from Networksecurity.entity.config_entity import DataIngestionConfig, TrainingPipelineConfig, DataValidationConfig, DataTransformationConfig, ModelTrainerConfig

from Networksecurity.components.data_validation import DataValidation
from Networksecurity.entity.artifact_entity import DataIngestionArtifact

from Networksecurity.components.data_transformation import DataTransformation
from Networksecurity.entity.artifact_entity import DataTransformationArtifact

from Networksecurity.components.model_trainer import ModelTrainer
from Networksecurity.entity.artifact_entity import ModelTrainerArtifact



from Networksecurity.logging.logger import logging
from Networksecurity.exceptions.exception import NetworkSecurityException
import sys

if __name__ == "__main__":
    try:
        logging.info("Starting Data Ingestion process")
        training_pipeline_config = TrainingPipelineConfig()
        data_ingestion_config = DataIngestionConfig(training_pipeline_config=training_pipeline_config)
        

        data_ingestion = DataIngestion(data_ingestion_config=data_ingestion_config)
        logging.info("Exporting collection as DataFrame")
       
        data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
        logging.info("Data Ingestion Artifact created successfully")
        print(data_ingestion_artifact)
        print("Data Ingestion completed successfully")


        logging.info("Data Ingestion process completed successfully")
        logging.info("Exiting Data Ingestion process")
        logging.info("Starting Data Validation process")
        data_validation_config = DataValidationConfig(training_pipeline_config=training_pipeline_config)
        data_validation = DataValidation(data_ingestion_artifact=data_ingestion_artifact,
                                         data_validation_config=data_validation_config)
        logging.info("Validating data")
        data_validation_artifact=data_validation.initiate_data_validation()
        print(data_validation_artifact)
        logging.info("Data Validation completed successfully")  
        logging.info("Exiting Data Validation process")

        logging.info("Starting Data Transformation process")
        data_transformation_config = DataTransformationConfig(training_pipeline_config=training_pipeline_config)
        logging.info("Creating Data Transformation object")
        data_transformation = DataTransformation(data_validation_artifact=data_validation_artifact,
                                                 data_transformation_config=data_transformation_config)
        logging.info("Satrted data transformation")
        data_transformation_artifact=data_transformation.initiate_data_transformation()
        logging.info("Data Transformation completed successfully")
        logging.info("Exiting Data Transformation process")

        logging.info("Starting Model Training process")
        model_trainer_config = ModelTrainerConfig(training_pipeline_config=training_pipeline_config)
        model_trainer = ModelTrainer(model_trainer_config=model_trainer_config,
                                     data_transformation_artifact=data_transformation_artifact)
        model_trainer_artifact = model_trainer.initiate_model_trainer()
        logging.info("Model Training process completed successfully")

    except Exception as e:
        logging.error(f"An error occurred during Data Ingestion: {e}")
        raise NetworkSecurityException(e,sys) 