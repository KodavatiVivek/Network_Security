from Networksecurity.exceptions.exception import NetworkSecurityException
from Networksecurity.entity.artifact_entity import ClassificationMetricArtifact
from sklearn.metrics import f1_score, precision_score, recall_score
from Networksecurity.logging.logger import logging


def get_classification_score(y_true, y_pred) -> ClassificationMetricArtifact:
    """
    Calculate classification metrics: F1 score, precision, and recall.

    Args:
        y_true (list or array-like): True labels.
        y_pred (list or array-like): Predicted labels.

    Returns:
        ClassificationMetricArtifact: An artifact containing the calculated metrics.
    """
    try:
        logging.info("Calculating classification metrics to evaualate model performance on test data and accuracy of model.")
        f1 = f1_score(y_true, y_pred, average='weighted')
        precision = precision_score(y_true, y_pred, average='weighted')
        recall = recall_score(y_true, y_pred, average='weighted')
        logging.info(f"F1 Score: {f1}, Precision: {precision}, Recall: {recall}")

        classication_metric= ClassificationMetricArtifact(
            f1_score=f1,
            precision_score=precision,
            recall_score=recall
        )
        logging.info("Classification metrics calculated successfully.")
        logging.info(f"Classification Metric Artifact: {classication_metric}")
        return classication_metric
    except Exception as e:
        raise NetworkSecurityException(e)