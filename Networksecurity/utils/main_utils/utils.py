import yaml
from Networksecurity.exceptions.exception import NetworkSecurityException
from Networksecurity.logging.logger import logging
import os,sys
import numpy as np
#import dill
import pickle

from sklearn.metrics import r2_score
from sklearn.model_selection import GridSearchCV

def read_yaml_file(file_path: str) -> dict:
    try:
        logging.info(f"Reading YAML file from: {file_path}")
        with open(file_path, "rb") as yaml_file:
            return yaml.safe_load(yaml_file)
        logging.info(f"Successfully read YAML file: {file_path}")
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
def write_yaml_file(file_path: str, content: object, replace: bool = False) -> None:
    try:
        if replace:
            if os.path.exists(file_path):
                os.remove(file_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as file:
            yaml.dump(content, file)
    except Exception as e:
        raise NetworkSecurityException(e, sys)

def save_numpy_array_data(file_path: str, array: np.ndarray) -> None:
    try:
        logging.info(f"Saving numpy array to: {file_path}")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as file_obj:
            # Using np.save to save the numpy array
            # dill.dump(array, file)  # If you want to use dill for serialization
            # Instead, using pickle for compatibility with numpy arrays
            np.save(file_obj, array)
        logging.info(f"Successfully saved numpy array to: {file_path}")
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
def load_numpy_array_data(file_path: str) -> np.array:
    """
    load numpy array data from file
    file_path: str location of file to load
    return: np.array data loaded
    """
    try:
        with open(file_path, "rb") as file_obj:
            return np.load(file_obj)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e

def save_object(file_path: str, obj: object) -> None:
    try:
        logging.info(f"Saving object to: {file_path}")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as file_obj:
            # Using pickle to save the object
            pickle.dump(obj, file_obj)
        logging.info(f"Successfully saved object to: {file_path}")
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e

def load_object(file_path: str) -> object:
    try:
        logging.info(f"Loading object from: {file_path}")
        if not os.path.exists(file_path):
            raise Exception(f"The file: {file_path} does not exist")
        with open(file_path, "rb") as file_obj:
            return pickle.load(file_obj)
        logging.info(f"Successfully loaded object from: {file_path}")
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e

def evaluate_models(X_train, y_train, X_test, y_test, models: dict, param: dict) -> dict:
    """
    Evaluate multiple models using GridSearchCV to find the best hyperparameters.
    X_train: Training features
    y_train: Training target variable
    X_test: Testing features
    y_test: Testing target variable
    models: dict of models to evaluate
    param: dict of hyperparameters for each model
    return: dict of best models with their corresponding hyperparameters and scores
    """
    best_models = {}
    for model_name, model in models.items():
        # Initialize GridSearchCV with the model and hyperparameters
        grid_search = GridSearchCV(estimator=model, param_grid=param[model_name], cv=3, n_jobs=-1, verbose=1)
        logging.info(f"Starting GridSearchCV for model: {model_name}")
        # Fit the model to the training data
        grid_search.fit(X_train, y_train)
        # Get the best model and its score
        best_model = grid_search.best_estimator_
        best_score = grid_search.best_score_
        model.set_params(**grid_search.best_params_)
        logging.info(f"Best parameters for {model_name}: {grid_search.best_params_}")
        #Train the model
        model.fit(X_train, y_train)
        logging.info(f"Model {model_name} trained successfully with best parameters.")
        # Predict on the test set
        y_train_pred = best_model.predict(X_train)
        y_test_pred = best_model.predict(X_test)

        # Calculate R2 score for the test set
        test_score_r2 = r2_score(y_test, y_test_pred)
        train_score = r2_score(y_train, y_train_pred)

        # Store the best model and its score
        best_models[model_name] = {
            "model": best_model,
            "score": best_score,
            "train_score": train_score,
            "test_score": test_score_r2,
        }
        logging.info(f"Model: {model_name}, Best Score: {best_score}, Test Score: {test_score_r2}")
    logging.info("Completed model evaluation.")
    return best_models
