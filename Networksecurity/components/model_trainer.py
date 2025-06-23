import os
import sys

from Networksecurity.exceptions.exception import NetworkSecurityException  
from Networksecurity.logging.logger import logging

from Networksecurity.utils.main_utils.utils import load_numpy_array_data,save_numpy_array_data,evaluate_models
from Networksecurity.utils.main_utils.utils import load_object, save_object
from Networksecurity.utils.ml_utils.metrics.Classification import get_classification_score
from Networksecurity.utils.ml_utils.model.estimator import NetworkModel

from Networksecurity.entity.artifact_entity import DataTransformationArtifact,ModelTrainerArtifact
from Networksecurity.entity.config_entity import ModelTrainerConfig

#MAchine Learning Model Trainer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import r2_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
)

#MLFLOW
import mlflow

#import dagshub
#dagshub.init(repo_owner='KodavatiVivek', repo_name='Network_Security', mlflow=True)



class ModelTrainer:
    def __init__(self, model_trainer_config: ModelTrainerConfig, data_transformation_artifact: DataTransformationArtifact):
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
    
    def track_best_model_mlflow(self,best_model,classification_metric):
        try:
            # Start MLflow
            with mlflow.start_run():
                f1=classification_metric.f1_score
                recall=classification_metric.recall_score
                precision=classification_metric.precision_score
                
                mlflow.log_metric("f1_score",f1)
                mlflow.log_metric("recall_score",recall)
                mlflow.log_metric("precision_score",precision)
                mlflow.sklearn.log_model(best_model,"model")

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def train_model(self, x_train, y_train,x_test, y_test):
        """
        Train the model using the provided training data.
        
        Args:
            x_train (np.ndarray): Training features.
            y_train (np.ndarray): Training labels.
            x_test (np.ndarray): Testing features.
            y_test (np.ndarray): Testing labels.
        
        Returns:
            model: The trained model.
        """
        try:
            logging.info("Training the model with different algorithms to find the best one.")
            models = {
                "LogisticRegression": LogisticRegression(verbose=1),
                "KNeighborsClassifier": KNeighborsClassifier(),
                "DecisionTreeClassifier": DecisionTreeClassifier(),
                "RandomForestClassifier": RandomForestClassifier(verbose=1, n_jobs=-1),
                "GradientBoostingClassifier": GradientBoostingClassifier(verbose=1),
                "AdaBoostClassifier": AdaBoostClassifier()
            }
            params = {
                "LogisticRegression": {
                    "C": [0.001, 0.01, 0.1, 1, 10, 100],
                    "max_iter": [50, 100, 200]
                },
                "KNeighborsClassifier": {
                    "n_neighbors": [3, 5, 7, 9],
                    "weights": ['uniform', 'distance']
                },
                "DecisionTreeClassifier": {
                    "criterion": ["gini", "entropy"],
                    "max_depth": [None, 10, 20, 30]
                },
                "RandomForestClassifier": {
                    "n_estimators": [50, 100, 200],
                    "max_depth": [None, 10, 20],
                    "min_samples_split": [2, 5]
                },
                "GradientBoostingClassifier": {
                    "n_estimators": [50, 100],
                    "learning_rate": [0.01, 0.1],
                    "max_depth": [3, 5]
                },
                "AdaBoostClassifier": {
                    "n_estimators": [50, 100],
                    "learning_rate": [0.01, 0.1]
                }
            }

            models:dict = evaluate_models(
                X_train=x_train, 
                y_train=y_train, 
                X_test=x_test, 
                y_test=y_test, 
                models=models, 
                param=params
            )

            # Get the best model based on the evaluation
            best_model_score = max(model_data["score"] for model_data in models.values())
            best_model_name = max(models, key=lambda name: models[name]["score"])
            best_model = models[best_model_name]["model"]
            logging.info(f"Best model found: {best_model_name} with score: {best_model_score}")
            # Train the best model on the training data
            y_train_pred = best_model.predict(x_train)
            classification_train_metric = get_classification_score(y_true=y_train, y_pred=y_train_pred)
            logging.info(f"Training completed for model: {best_model_name} with training metrics: {classification_train_metric}")
            self.track_best_model_mlflow(best_model,classification_train_metric)

            # TRack the experiments with mlflow
            y_test_pred = best_model.predict(x_test)
            classification_test_metric = get_classification_score(y_true=y_test, y_pred=y_test_pred)
            logging.info(f"Testing completed for model: {best_model_name} with testing metrics: {classification_test_metric}")
            # Save the best model
            self.track_best_model_mlflow(best_model,classification_test_metric)

            #Loading the preproccessort pickle file
            preprocessor = load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)

            model_dir_path= os.path.dirname(self.model_trainer_config.trained_model_file_path)
            os.makedirs(model_dir_path, exist_ok=True)

            # TO get New data prediction we use Network odel
            network_model = NetworkModel(preprocessor=preprocessor, model=best_model)
            save_object(file_path=self.model_trainer_config.trained_model_file_path, obj=network_model)
            logging.info(f"Model saved at: {self.model_trainer_config.trained_model_file_path}")

            save_object("final_model/model.pkl",best_model)
            

            #Model Trainer Artifact
            model_trainer_artifact = ModelTrainerArtifact(
                trained_model_file_path=self.model_trainer_config.trained_model_file_path,
                train_metric_artifact=classification_train_metric,
                test_metric_artifact=classification_test_metric
            )
            logging.info(f"Model Trainer Artifact created: {model_trainer_artifact}")
            return model_trainer_artifact
            


        except Exception as e:
            raise NetworkSecurityException(e, sys) from e



        
    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        try:
            logging.info("Initiating model training process.")
            
            # Load transformed data
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.transformed_test_file_path
            
            logging.info(f"Loading training and Testing data and conversting it into numpy array.")
            train_arr= load_numpy_array_data(file_path=train_file_path)
            test_arr = load_numpy_array_data(file_path=test_file_path)

            # Split data into features and target variable
            logging.info("Splitting train data into features and target variable.")
            x_train = train_arr[:, :-1]  # All columns except the last one
            y_train = train_arr[:, -1]    # Last column as target variable
            logging.info("Splitting test data into features and target variable.")
            x_test = test_arr[:, :-1]      # All columns except the last one
            y_test = test_arr[:, -1]        # Last column as target variable

            

        
            # Create and return ModelTrainerArtifact
            model_trainer_artifact = self.train_model(x_train=x_train, y_train=y_train,x_test=x_test, y_test=y_test)
            logging.info("Model training completed successfully.")
            return model_trainer_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e


