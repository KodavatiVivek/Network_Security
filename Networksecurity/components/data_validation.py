from Networksecurity.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact
from Networksecurity.entity.config_entity import DataValidationConfig
from Networksecurity.exceptions.exception import NetworkSecurityException 
from Networksecurity.logging.logger import logging 
from Networksecurity.constants.training_pipeline import SCHEMA_FILE_PATH
from Networksecurity.utils.main_utils.utils import read_yaml_file, write_yaml_file

#Data drift detection using Kolmogorov-Smirnov test 
from scipy.stats import ks_2samp

import pandas as pd
import os,sys

class DataValidation:
    def __init__(self,data_ingestion_artifact:DataIngestionArtifact,
                 data_validation_config:DataValidationConfig):
        
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        try:
            logging.info(f"Reading data from {file_path}")
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def validate_number_of_columns(self, dataframe: pd.DataFrame) -> bool:
        try:
            number_of_columns = self._schema_config.get("columns", [])
            logging.info(f"Required number of columns: {len(number_of_columns)}")
            logging.info(f"Data frame has columns: {len(dataframe.columns)}")
            return len(dataframe.columns) == len(number_of_columns)
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def validate_numeric_columns(self, dataframe: pd.DataFrame) -> bool:
        try:
            numeric_columns = self._schema_config.get("numerical_columns", [])
            logging.info(f"Numeric columns defined in schema: {numeric_columns}")
            for column in numeric_columns:
                if column not in dataframe.columns:
                    logging.error(f"Column {column} is missing in the DataFrame.")
                    return False
                if not pd.api.types.is_numeric_dtype(dataframe[column]):
                    logging.error(f"Column {column} is not numeric.")
                    return False
            return True
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def detect_dataset_drift(self, base_df: pd.DataFrame, current_df: pd.DataFrame, threshold=0.05) -> bool:
        try:
            status = True
            report = {}
            for column in base_df.columns:
                d1 = base_df[column]
                d2 = current_df[column]
                is_same_dist = ks_2samp(d1, d2)
                is_found = threshold <= is_same_dist.pvalue
                if not is_found:
                    status = False
                report.update({column: {
                    "p_value": float(is_same_dist.pvalue),
                    "drift_status": is_found
                }})
            
            drift_report_file_path = self.data_validation_config.drift_report_file_path
            
            # Create directory if it does not exist
            os.makedirs(os.path.dirname(drift_report_file_path), exist_ok=True)
            
            # Write the drift report to a YAML file
            write_yaml_file(file_path=drift_report_file_path, content=report)
            
            return status
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            logging.info("Starting data validation process.")

            # Train and Test file path 
            train_file_path = self.data_ingestion_artifact.trained_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path

            #Train and Test file dataframe
            train_df = self.read_data(train_file_path)
            test_df = self.read_data(test_file_path)
            
            
            
            # Validate number of columns
            is_valid_columns_train = self.validate_number_of_columns(train_df)
            if not is_valid_columns_train:
                raise NetworkSecurityException("Number of columns in the current dataset does not match the schema.",sys)
            
            is_valid_columns_test = self.validate_number_of_columns(test_df)
            if not is_valid_columns_test:
                raise NetworkSecurityException("Number of columns in the current dataset does not match the schema.",sys)
            
            is_numeric_columns_train = self.validate_numeric_columns(train_df)
            if not is_numeric_columns_train:
                raise NetworkSecurityException("Number of numerical columns in the current dataset does not match the schema.",sys)
            
            is_numeric_columns_test = self.validate_numeric_columns(test_df)
            if not is_numeric_columns_test:
                raise NetworkSecurityException("Number of numerical columns in the current dataset does not match the schema.",sys)
            
            # Detect dataset drift
            is_drifted = self.detect_dataset_drift(train_df, test_df)
            if not is_drifted:
                logging.info("No drift detected between train and test datasets.")
            else:
                logging.warning("Drift detected between train and test datasets.")

            # Save valid train and test dataframes
            logging.info("Saving valid train and test dataframes.")
            dir_name_valid_path= os.path.dirname(self.data_validation_config.valid_train_file_path)
            os.makedirs(dir_name_valid_path, exist_ok=True)    
            
            train_df.to_csv(self.data_validation_config.valid_train_file_path, index=False, header=True)
            test_df.to_csv(self.data_validation_config.valid_test_file_path, index=False, header=True)
            logging.info("Valid train and test dataframes saved successfully.")
            # Save invalid train and test dataframes if needed  
            
            # Create and return DataValidationArtifact
            data_validation_artifact = DataValidationArtifact(
                validation_status= is_drifted,
                valid_train_file_path=self.data_validation_config.valid_train_file_path,
                valid_test_file_path=self.data_validation_config.valid_test_file_path,
                drift_report_file_path=self.data_validation_config.drift_report_file_path,
                invalid_test_file_path=None,
                invalid_train_file_path=None
            )
            
            logging.info("Data validation completed successfully.")
            return data_validation_artifact
        
        except Exception as e:
            raise NetworkSecurityException(e, sys)