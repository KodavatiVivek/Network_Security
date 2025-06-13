from Networksecurity.constants.training_pipeline import SAVED_MODEL_DIR, MODEL_FILE_NAME

import os
import sys

from Networksecurity.exceptions.exception import NetworkSecurityException
from Networksecurity.logging.logger import logging


class NetworkModel:
    def __init__(self,preprocessor,model):
        try:
            logging.info("Initializing NetworkModel with preprocessor and model.")
            self.preprocessor = preprocessor
            self.model = model
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    def predict(self,x):
        try:
            logging.info("Predicting using the NetworkModel.")
            x_transform = self.preprocessor.transform(x)
            y_hat = self.model.predict(x_transform)
            logging.info("Prediction completed successfully.")
            logging.info(f"Predicted values: {y_hat}")
            return y_hat
        except Exception as e:
            raise NetworkSecurityException(e,sys)