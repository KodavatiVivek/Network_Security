from Networksecurity.exceptions.exception import NetworkSecurityException
from Networksecurity.logging.logger import logging as logger

import os
import sys
import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from Networksecurity.constants.training_pipeline import TARGET_COLUMN,DATA_TRANSFORMATION_IMPUTER_PARAMS

from Networksecurity.entity.config_entity import DataTransformationConfig   
from Networksecurity.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact, DataTransformationArtifact
from Networksecurity.utils.main_utils.utils import save_numpy_array_data, load_numpy_array_data, save_object

class DataTransformation:
    def __init__(self, data_validation_artifact: DataValidationArtifact, data_transformation_config: DataTransformationConfig):
        try:
            self.data_transformation_config = data_transformation_config
            self.data_validation_artifact = data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        try:
            logger.info(f"Reading data from: {file_path}")
            df = pd.read_csv(file_path)
            logger.info(f"Data read successfully from: {file_path}")
            return df
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
    
    def get_data_Preprocessor_object(cls) -> Pipeline:
        """
        Create a data transformation pipeline with KNNImputer and StandardScaler
        ARgs:
            cls: The class itself, used for static method access.DataTransformation
        Returns:    
            Pipeline: A scikit-learn Pipeline object that includes KNNImputer and StandardScaler.
        ."""
        try:
            logger.info("Creating data transformation pipeline.")
            # Create a KNNImputer for handling missing values
            imputer: KNNImputer = KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS)
            logger.info("KNNImputer created with parameters: %s", DATA_TRANSFORMATION_IMPUTER_PARAMS)
            # Create a StandardScaler for feature scaling
            #scaler = StandardScaler()

            # Create a pipeline with the imputer and scaler
            processor:Pipeline = Pipeline(steps=[
                ('imputer', imputer),
            ])
            logger.info("Data transformation pipeline created successfully.")
            return processor
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
    
    def initiate_data_transformation(self)-> DataTransformationArtifact:
        try:
            logger.info("Starting data transformation process.")
            train_df = DataTransformation.read_data(self.data_validation_artifact.valid_train_file_path)
            test_df = DataTransformation.read_data(self.data_validation_artifact.valid_test_file_path)

            logger.info("Data transformation process started.")
            logger.info("Transforming training and testing data.")
            logger.info(f"Diving X_train and y_train from train_df with shape: {train_df.shape}")

            # Separate features and target variable
            X_train = train_df.drop(columns=[TARGET_COLUMN],axis=1)
            y_train = train_df[TARGET_COLUMN]
            y_train=y_train.replace(-1,0)  # Replace -1 with 0 in the target variable

            logger.info(f"Diving X_test and y_test from test_df with shape: {test_df.shape}")

            X_test = test_df.drop(columns=[TARGET_COLUMN])
            y_test = test_df[TARGET_COLUMN]
            y_test=y_test.replace(-1,0)  # Replace -1 with 0 in

            logger.info("KNN Imputer and Standard Scaler will be applied to the data.")

            # Impute missing values using KNNImputer
            logger.info("Calling the preprocessor object")
            preprocessor = self.get_data_Preprocessor_object()
            logger.info("Preprocessor object created successfully jsuing fit method.")
            preprocessor_object = preprocessor.fit(X_train)
            logger.info("Fitting the preprocessor to the training data and transforming both train and test data.")
    
            X_train_imputed = preprocessor_object.transform(X_train)
            X_test_imputed = preprocessor_object.transform(X_test)

            logger.info("Imputation completed for both training and testing data.")

            train_arr= np.c_[X_train_imputed, np.array(y_train)]
            test_arr = np.c_[X_test_imputed, np.array(y_test)]
            logger.info("Concatenated training and testing data with target variable as numpy arrays.")

            # Save the transformed data
            save_numpy_array_data(self.data_transformation_config.transformed_train_file_path, array=train_arr)
            save_numpy_array_data(self.data_transformation_config.transformed_test_file_path, array=test_arr)

            save_object(self.data_transformation_config.transformed_object_file_path, preprocessor_object)

            # Save the preprocessor
            save_object("final_model/preprocessor.pkl", preprocessor_object)

            logger.info("Transformed data saved successfully.")
            logger.info("Creating DataTransformationArtifact with transformed file paths.")

            data_transformation_artifact = DataTransformationArtifact(
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path,
                transformed_object_file_path=self.data_transformation_config.transformed_object_file_path
            )

            logger.info("Data transformation process completed successfully.")
            return data_transformation_artifact

            
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e