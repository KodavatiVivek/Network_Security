import os
import sys

from Networksecurity.exceptions.exception import NetworkSecurityException
from Networksecurity.logging.logger import logging

from Networksecurity.components.data_ingestion import DataIngestion
from Networksecurity.components.data_validation import DataValidation
from Networksecurity.components.data_transformation import DataTransformation
from Networksecurity.components.model_trainer import ModelTrainer

from Networksecurity.entity.config_entity import (
    DataIngestionConfig,
    DataValidationConfig,
    DataTransformationConfig,
    ModelTrainerConfig,
    TrainingPipelineConfig
)

from Networksecurity.entity.artifact_entity import (
    DataIngestionArtifact,
    DataValidationArtifact,
    DataTransformationArtifact,
    ModelTrainerArtifact
)

from Networksecurity.utils.main_utils.utils import load_object

class TrainingPipeline:
    def __init__(self):
        try:
            self.training_pipeline_config = TrainingPipelineConfig()
        except Exception as e:
            logging.error(e)
            raise NetworkSecurityException(e)
    
    def start_data_ingestion(self):
        try:
            self.data_ingestion_config = DataIngestionConfig(training_pipeline_config=self.training_pipeline_config)
            logging.info("Starting data ingestion.")
            data_ingestion = DataIngestion(data_ingestion_config=self.data_ingestion_config)
            data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
            logging.info(f"Data ingestion completed.{data_ingestion_artifact}")
            return data_ingestion_artifact
        except Exception as e:
            raise NetworkSecurityException(e)
    
    def start_data_validation(self, data_ingestion_artifact: DataIngestionArtifact):
        try:
            logging.info("Starting Data Validation process")
            self.data_validation_config = DataValidationConfig(training_pipeline_config=self.training_pipeline_config)
            data_validation = DataValidation(data_ingestion_artifact=data_ingestion_artifact,
                                         data_validation_config=self.data_validation_config)
            logging.info("Validating data")
            data_validation_artifact=data_validation.initiate_data_validation()
        
            logging.info(f"Data Validation completed successfully:{data_validation_artifact}")  
            logging.info("Exiting Data Validation process")
            return data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException(e)
    
    def start_data_transformation(self, data_validation_artifact: DataValidationArtifact):
        try:
            logging.info("Starting data transformation")
            self.data_transformation_config = DataTransformationConfig(training_pipeline_config=self.training_pipeline_config)
            data_transformation = DataTransformation(data_validation_artifact=data_validation_artifact,
                                                     data_transformation_config=self.data_transformation_config)
            logging.info("Transforming data")
            data_transformation_artifact = data_transformation.initiate_data_transformation()
            logging.info(f"Data TRansformation is sucessfull : {data_transformation_artifact}")
            return data_transformation_artifact
        except Exception as e:  
            raise NetworkSecurityException(e)
    
    def start_model_training(self,data_transformation_artifact:DataTransformationArtifact)->ModelTrainerArtifact:
        try:
            logging.info("Starting model training")
            self.model_trainer_config:ModelTrainerConfig = ModelTrainerConfig(training_pipeline_config=self.training_pipeline_config)
            logging.info("Started ")

            model_trainer= ModelTrainer(data_transformation_artifact=data_transformation_artifact,
                                        model_trainer_config=self.model_trainer_config)
            logging.info("Training model")
            model_trainer_artifact = model_trainer.initiate_model_trainer()

            return model_trainer_artifact
        except Exception as e:
            raise NetworkSecurityException(e)
        
    def run_pipeline(self):
        try:
            data_ingestion_artifact = self.start_data_ingestion()
            data_validation_config=self.start_data_validation(data_ingestion_artifact=data_ingestion_artifact)
            data_transformation_artifact = self.start_data_transformation(data_validation_artifact=data_validation_config)
            model_trainer_artifact = self.start_model_training(data_transformation_artifact=data_transformation_artifact)
        except Exception as e:
            raise NetworkSecurityException(e)
    

    
