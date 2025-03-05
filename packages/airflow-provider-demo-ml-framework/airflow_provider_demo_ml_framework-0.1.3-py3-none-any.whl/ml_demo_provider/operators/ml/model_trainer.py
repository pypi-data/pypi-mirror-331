import os
from abc import ABC
from abc import abstractmethod
from datetime import datetime

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import explained_variance_score
from sklearn.metrics import f1_score
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import precision_score
from sklearn.metrics import r2_score
from sklearn.metrics import recall_score
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler


class ModelTrainer(ABC):
    """
    Abstract base class for all model trainers with MLflow integration and time-based validation.
    """

    def __init__(self, train_df, mlflow_experiment_name, cv_folds=5):
        """
        Initialize the model trainer.

        Parameters:
        -----------
        train_df : DataFrame
            DataFrame containing the data
        mlflow_experiment_name : str
            Name of the MLflow experiment to log to
        cv_folds : int
            Number of cross-validation folds for time series validation
        """
        self.train_df = train_df
        self.mlflow_experiment_name = mlflow_experiment_name
        self.cv_folds = cv_folds
        self.features = []  # To be defined in subclasses
        self.target = None  # To be defined in subclasses or set to None for unsupervised learning
        self.timestamp_col = 'WHEN_TIMESTAMP'

    def load_data(self):
        """
        Load and preprocess the dataset.

        Returns:
        --------
        pandas.DataFrame
            Preprocessed dataframe
        """
        df = self.train_df
        # Convert timestamp to datetime if it exists
        if self.timestamp_col in df.columns:
            df[self.timestamp_col] = pd.to_datetime(df[self.timestamp_col])
            # Sort by timestamp to ensure time-based order
            df = df.sort_values(self.timestamp_col)

        return df

    @abstractmethod
    def create_pipeline(self):
        """
        Create a model pipeline with preprocessing and model.

        Returns:
        --------
        sklearn.pipeline.Pipeline
            Model pipeline
        """
        pass

    @abstractmethod
    def evaluate_model(self, model, X_test, y_test=None, prefix=""):
        """
        Evaluate model performance and log metrics.

        Parameters:
        -----------
        model : sklearn.pipeline.Pipeline
            Trained model pipeline
        X_test : pandas.DataFrame
            Test features
        y_test : pandas.Series or None
            Test target (None for unsupervised learning)
        prefix : str
            Prefix for MLflow metric names

        Returns:
        --------
        dict
            Dictionary of evaluation metrics
        """
        pass

    def log_dataset_info(self, df):
        """
        Log dataset information to MLflow.

        Parameters:
        -----------
        df : pandas.DataFrame
            Dataset
        """
        mlflow.log_param("dataset_size", len(df))
        if self.timestamp_col in df.columns:
            mlflow.log_param("dataset_start_date", df[self.timestamp_col].min())
            mlflow.log_param("dataset_end_date", df[self.timestamp_col].max())

        # Log target distribution for supervised learning
        if self.target is not None and self.target in df.columns:
            if df[self.target].dtype in [np.int64, np.int32, np.int16, np.int8, np.bool_]:
                # For classification, log class distribution
                value_counts = df[self.target].value_counts(normalize=True)
                for value, count in value_counts.items():
                    mlflow.log_param(f"class_{value}_ratio", count)
            else:
                # For regression, log basic statistics
                mlflow.log_param(f"{self.target}_mean", df[self.target].mean())
                mlflow.log_param(f"{self.target}_median", df[self.target].median())
                mlflow.log_param(f"{self.target}_min", df[self.target].min())
                mlflow.log_param(f"{self.target}_max", df[self.target].max())

    def log_feature_distributions(self, df):
        """
        Log histograms of feature distributions.

        Parameters:
        -----------
        df : pandas.DataFrame
            Dataset with features
        """
        os.makedirs('artifacts', exist_ok=True)

        try:
            numerical_features = df[self.features].select_dtypes(include=np.number).columns.tolist()
            # TODO: Add mlflow.log_...
        except Exception as e:
            print(f"Warning: Could not generate feature distribution: {e}")

    def log_split_info(self, df, train_index, test_index, prefix="final"):
        """
        Log information about the train/test split.

        Parameters:
        -----------
        df : pandas.DataFrame
            Dataset
        train_index : array-like
            Indices for training set
        test_index : array-like
            Indices for test set
        prefix : str
            Prefix for MLflow parameter names
        """
        mlflow.log_param(f"{prefix}_train_size", len(train_index))
        mlflow.log_param(f"{prefix}_test_size", len(test_index))

        if self.timestamp_col in df.columns:
            mlflow.log_param(
                f"{prefix}_train_start_date", df.iloc[train_index][self.timestamp_col].min()
            )
            mlflow.log_param(
                f"{prefix}_train_end_date", df.iloc[train_index][self.timestamp_col].max()
            )
            mlflow.log_param(
                f"{prefix}_test_start_date", df.iloc[test_index][self.timestamp_col].min()
            )
            mlflow.log_param(
                f"{prefix}_test_end_date", df.iloc[test_index][self.timestamp_col].max()
            )

    def generate_time_based_splits(self, X):
        """
        Generate time-based train/test splits.

        Parameters:
        -----------
        X : pandas.DataFrame
            Feature data

        Returns:
        --------
        list of tuples
            List of (train_index, test_index) tuples
        """
        tscv = TimeSeriesSplit(n_splits=self.cv_folds)
        return list(tscv.split(X))

    def generate_cv_splits(self, X):
        """
        Generate cross-validation splits. This can be overridden by subclasses.
        uses time-based splits if timestamp column exists.

        Parameters:
        -----------
        X : pandas.DataFrame
            Feature data

        Returns:
        --------
        list of tuples
            List of (train_index, test_index) tuples
        """
        return self.generate_time_based_splits(X)

    def train(self):
        """
        Train model with cross-validation and MLflow tracking.

        Returns:
        --------
        model : sklearn.pipeline.Pipeline
            Trained model pipeline
        metrics : dict
            Dictionary of evaluation metrics from final test set
        """
        # Set MLflow experiment
        mlflow.set_experiment(self.mlflow_experiment_name)

        # Start MLflow run
        with mlflow.start_run(
            run_name=f"{self.__class__.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        ):
            # Log parameters
            mlflow.log_param("model_type", self.__class__.__name__)
            mlflow.log_param("cv_folds", self.cv_folds)

            # Load and prepare data
            df = self.load_data()
            self.log_dataset_info(df)

            X = df[self.features]
            y = df[self.target] if self.target is not None else None

            # Log feature distributions
            self.log_feature_distributions(df)

            # Create model pipeline
            pipeline = self.create_pipeline()

            # Generate cross-validation splits
            cv_splits = self.generate_cv_splits(X)

            # Perform cross-validation
            cv_metrics = []
            fold = 0

            for train_index, test_index in cv_splits:
                fold += 1
                X_train, X_test = X.iloc[train_index], X.iloc[test_index]

                # Handle supervised vs unsupervised learning
                if y is not None:
                    y_train, y_test = y.iloc[train_index], y.iloc[test_index]
                    # Train model on this fold
                    pipeline.fit(X_train, y_train)
                    # Evaluate on test fold
                    fold_metrics, _, _ = self.evaluate_model(
                        pipeline, X_test, y_test, prefix=f"fold_{fold}_"
                    )
                else:
                    # For unsupervised learning
                    pipeline.fit(X_train)
                    # Evaluate on test fold
                    fold_metrics, _, _ = self.evaluate_model(
                        pipeline, X_test, prefix=f"fold_{fold}_"
                    )

                cv_metrics.append(fold_metrics)

            # Calculate and log average CV metrics
            if cv_metrics:
                avg_metrics = {
                    metric: np.mean([fold[metric] for fold in cv_metrics if metric in fold])
                    for metric in cv_metrics[0]
                }
                for metric_name, metric_value in avg_metrics.items():
                    mlflow.log_metric(f"avg_{metric_name}", metric_value)

            # Use the last fold for final evaluation
            final_train_index, final_test_index = cv_splits[-1]
            X_train, X_test = X.iloc[final_train_index], X.iloc[final_test_index]

            # Log final split info
            self.log_split_info(df, final_train_index, final_test_index)

            # Train final model
            if y is not None:
                y_train, y_test = y.iloc[final_train_index], y.iloc[final_test_index]
                pipeline.fit(X_train, y_train)
                # Evaluate final model
                final_metrics, y_pred, extras = self.evaluate_model(
                    pipeline, X_test, y_test, prefix="final_"
                )
            else:
                pipeline.fit(X_train)
                # Evaluate final model
                final_metrics, y_pred, extras = self.evaluate_model(
                    pipeline, X_test, prefix="final_"
                )
                y_test = None

            # Log model
            mlflow_artifact = mlflow.sklearn.log_model(pipeline, "model")

            logged_model = (
                mlflow_artifact.model_uri
            )  #'runs:/0a3ef388bcd64b18a45cdc208af47de9/model'
            print(f"Model trained successfully. Metrics: {final_metrics}")
            return pipeline, final_metrics, logged_model


class SupervisedModelTrainer(ModelTrainer):
    """
    Abstract base class for supervised learning models (classification and regression).
    """

    def __init__(self, train_data, mlflow_experiment_name, target, features, cv_folds=5):
        """
        Initialize supervised model trainer.

        Parameters:
        -----------
        train_data : DataFrame
            train_data
        mlflow_experiment_name : str
            Name of the MLflow experiment
        target : str
            Name of the target column
        features : list
            List of feature column names
        cv_folds : int
            Number of cross-validation folds
        """
        super().__init__(train_data, mlflow_experiment_name, cv_folds)
        self.target = target
        self.features = features

    def log_feature_importance(self, model):
        """
        Log feature importance or coefficients if available.

        Parameters:
        -----------
        model : object
            Trained model
        """
        os.makedirs('artifacts', exist_ok=True)

        if hasattr(model, 'feature_importances_'):
            feature_importances = pd.DataFrame(
                {'feature': self.features, 'importance': model.feature_importances_}
            ).sort_values('importance', ascending=False)

            # Log feature importance as CSV
            feature_importances.to_csv('artifacts/feature_importance.csv', index=False)
            mlflow.log_artifact('artifacts/feature_importance.csv')

        elif hasattr(model, 'coef_'):
            coef = model.coef_
            if len(coef.shape) > 1 and coef.shape[0] == 1:
                coef = coef[0]  # For binary classification

            coefficients = pd.DataFrame(
                {'feature': self.features, 'coefficient': coef}
            ).sort_values('coefficient', ascending=False)

            # Log coefficients as CSV
            coefficients.to_csv('artifacts/feature_coefficients.csv', index=False)
            mlflow.log_artifact('artifacts/feature_coefficients.csv')

    def log_prediction_vs_actual(self, y_test, y_pred):
        """
        Log scatter plot of predicted vs actual values.

        Parameters:
        -----------
        y_test : array-like
            True target values
        y_pred : array-like
            Predicted target values
        """
        # TODO:  mlflow.log...
        pass


class ClassificationModelTrainer(SupervisedModelTrainer):
    """
    Abstract base class for classification models.
    """

    def evaluate_model(self, model, X_test, y_test, prefix=""):
        """
        Evaluate classification model performance and log metrics.

        Parameters:
        -----------
        model : sklearn.pipeline.Pipeline
            Trained model pipeline
        X_test : pandas.DataFrame
            Test features
        y_test : pandas.Series
            Test target
        prefix : str
            Prefix for MLflow metric names

        Returns:
        --------
        tuple
            (metrics dict, predictions, probabilities)
        """
        # Make predictions
        y_pred = model.predict(X_test)

        # For binary classification, get probabilities
        try:
            y_prob = model.predict_proba(X_test)[:, 1]
            has_probabilities = True
        except (AttributeError, IndexError):
            y_prob = None
            has_probabilities = False

        # Calculate metrics
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='weighted'),
            'recall': recall_score(y_test, y_pred, average='weighted'),
            'f1': f1_score(y_test, y_pred, average='weighted'),
        }

        # Add ROC AUC for binary classification
        if has_probabilities and len(np.unique(y_test)) == 2:
            metrics['roc_auc'] = roc_auc_score(y_test, y_prob)

        # Log metrics to MLflow
        for metric_name, metric_value in metrics.items():
            mlflow.log_metric(f"{prefix}{metric_name}", metric_value)

        return metrics, y_pred, y_prob

    def log_confusion_matrix(self, y_test, y_pred):
        """
        Generate and log confusion matrix.

        Parameters:
        -----------
        y_test : array-like
            True target values
        y_pred : array-like
            Predicted target values
        """
        cm = confusion_matrix(y_test, y_pred)
        # TODO: mlflow.log ...
        # cm_df = pd.DataFrame(confusion_matrix(y_test, y_pred))
        # os.makedirs('artifacts', exist_ok=True)
        # cm_df.to_csv('artifacts/confusion_matrix.csv', index=False)
        # mlflow.log_artifact('artifacts/confusion_matrix.csv')


class RegressionModelTrainer(SupervisedModelTrainer):
    """
    Abstract base class for regression models.
    """

    def evaluate_model(self, model, X_test, y_test, prefix=""):
        """
        Evaluate regression model performance and log metrics.

        Parameters:
        -----------
        model : sklearn.pipeline.Pipeline
            Trained model pipeline
        X_test : pandas.DataFrame
            Test features
        y_test : pandas.Series
            Test target
        prefix : str
            Prefix for MLflow metric names

        Returns:
        --------
        tuple
            (metrics dict, predictions, None)
        """
        # Make predictions
        y_pred = model.predict(X_test)

        # Calculate metrics
        metrics = {
            'mse': mean_squared_error(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'mae': mean_absolute_error(y_test, y_pred),
            'r2': r2_score(y_test, y_pred),
            'explained_variance': explained_variance_score(y_test, y_pred),
        }

        # Log metrics to MLflow
        for metric_name, metric_value in metrics.items():
            mlflow.log_metric(f"{prefix}{metric_name}", metric_value)

        return metrics, y_pred, None

    def log_residuals_plot(self, y_test, y_pred):
        """
        Create and log residuals plot.

        Parameters:
        -----------
        y_test : array-like
            True target values
        y_pred : array-like
            Predicted target values
        """
        os.makedirs('artifacts', exist_ok=True)

        try:
            residuals = y_test - y_pred
            # TODO: mlflow.log...
        except Exception as e:
            print(f"Warning: Could not generate residuals plots: {e}")


class LogisticRegressionTrainer(ClassificationModelTrainer):
    """
    Trainer for Logistic Regression classification model.
    """

    def __init__(
        self,
        train_data,
        mlflow_experiment_name,
        target,
        features,
        cv_folds=5,
        max_iter=1000,
        C=1.0,
        class_weight=None,
    ):
        """
        Initialize Logistic Regression trainer.

        Parameters:
        -----------
        data_path : str
            Path to the CSV file
        mlflow_experiment_name : str
            Name of the MLflow experiment
        target : str
            Name of the target column
        features : list
            List of feature column names
        cv_folds : int
            Number of cross-validation folds
        max_iter : int
            Maximum number of iterations for the solver
        C : float
            Inverse of regularization strength
        class_weight : dict or 'balanced' or None
            Weights associated with classes
        """
        super().__init__(train_data, mlflow_experiment_name, target, features, cv_folds)
        self.max_iter = max_iter
        self.C = C
        self.class_weight = class_weight

    def create_pipeline(self):
        """
        Create a pipeline with preprocessing and Logistic Regression model.
        """
        mlflow.log_param("max_iter", self.max_iter)
        mlflow.log_param("C", self.C)
        mlflow.log_param("class_weight", str(self.class_weight))

        return Pipeline(
            [
                ('scaler', StandardScaler()),
                (
                    'model',
                    LogisticRegression(
                        random_state=42,
                        max_iter=self.max_iter,
                        C=self.C,
                        class_weight=self.class_weight,
                    ),
                ),
            ]
        )


class RandomForestClassifierTrainer(ClassificationModelTrainer):
    """
    Trainer for Random Forest classification model.
    """

    def __init__(
        self,
        train_data,
        mlflow_experiment_name,
        target,
        features,
        cv_folds=5,
        n_estimators=100,
        max_depth=10,
        min_samples_split=2,
        class_weight=None,
    ):
        """
        Initialize Random Forest classification trainer.

        Parameters:
        -----------
        train_data : DataFrame
            train_data
        mlflow_experiment_name : str
            Name of the MLflow experiment
        target : str
            Name of the target column
        features : list
            List of feature column names
        cv_folds : int
            Number of cross-validation folds
        n_estimators : int
            Number of trees in the forest
        max_depth : int
            Maximum depth of the trees
        min_samples_split : int
            Minimum number of samples required to split an internal node
        class_weight : dict or 'balanced' or None
            Weights associated with classes
        """
        super().__init__(train_data, mlflow_experiment_name, target, features, cv_folds)
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.class_weight = class_weight

    def create_pipeline(self):
        """
        Create a pipeline with preprocessing and Random Forest model.
        """
        mlflow.log_param("n_estimators", self.n_estimators)
        mlflow.log_param("max_depth", self.max_depth)
        mlflow.log_param("min_samples_split", self.min_samples_split)
        mlflow.log_param("class_weight", str(self.class_weight))

        return Pipeline(
            [
                ('scaler', StandardScaler()),
                (
                    'model',
                    RandomForestClassifier(
                        random_state=42,
                        n_estimators=self.n_estimators,
                        max_depth=self.max_depth,
                        min_samples_split=self.min_samples_split,
                        class_weight=self.class_weight,
                    ),
                ),
            ]
        )


class LinearRegressionTrainer(RegressionModelTrainer):
    """
    Trainer for Linear Regression model.
    """

    def __init__(self, train_data, mlflow_experiment_name, target, features, cv_folds=5):
        """
        Initialize Linear Regression trainer.

        Parameters:
        -----------
        data_path : str
            Path to the CSV file
        mlflow_experiment_name : str
            Name of the MLflow experiment
        target : str
            Name of the target column
        features : list
            List of feature column names
        cv_folds : int
            Number of cross-validation folds
        """
        super().__init__(train_data, mlflow_experiment_name, target, features, cv_folds)

    def create_pipeline(self):
        """
        Create a pipeline with preprocessing and Linear Regression model.
        """
        return Pipeline([('scaler', StandardScaler()), ('model', LinearRegression())])


class RandomForestRegressorTrainer(RegressionModelTrainer):
    """
    Trainer for Random Forest regression model.
    """

    def __init__(
        self,
        train_data,
        mlflow_experiment_name,
        target,
        features,
        cv_folds=5,
        n_estimators=100,
        max_depth=10,
        min_samples_split=2,
    ):
        """
        Initialize Random Forest regression trainer.

        Parameters:
        -----------
        train_data : DataFrame
            DataFrame with train_data
        mlflow_experiment_name : str
            Name of the MLflow experiment
        target : str
            Name of the target column
        features : list
            List of feature column names
        cv_folds : int
            Number of cross-validation folds
        n_estimators : int
            Number of trees in the forest
        max_depth : int
            Maximum depth of the trees
        min_samples_split : int
            Minimum number of samples required to split an internal node
        """
        super().__init__(train_data, mlflow_experiment_name, target, features, cv_folds)
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split

    def create_pipeline(self):
        """
        Create a pipeline with preprocessing and Random Forest regression model.
        """
        mlflow.log_param("n_estimators", self.n_estimators)
        mlflow.log_param("max_depth", self.max_depth)
        mlflow.log_param("min_samples_split", self.min_samples_split)

        return Pipeline(
            [
                ('scaler', StandardScaler()),
                (
                    'model',
                    RandomForestRegressor(
                        random_state=42,
                        n_estimators=self.n_estimators,
                        max_depth=self.max_depth,
                        min_samples_split=self.min_samples_split,
                    ),
                ),
            ]
        )


class ModelTrainerBuilder:
    # TODO: refactor
    def create_model_trainer(self, model_type, train_data, **kwargs):
        """
        Factory function to create the appropriate model trainer.

        Parameters:
        -----------
        model_type : str
            Type of model. Options:
                Classification: 'logistic', 'random_forest_classifier', 'gradient_boosting_classifier'
                Regression: 'linear', 'ridge', 'random_forest_regressor'
                Clustering: 'kmeans', 'dbscan'
        train_data : DataFrame
            DataFrame with training data
        **kwargs : dict
            Additional arguments for the trainer

        Returns:
        --------
        ModelTrainer
            Instance of appropriate model trainer
        """
        # Ensure required parameters are provided based on model type
        if model_type in [
            'logistic',
            'random_forest_classifier',
            'linear',
            'random_forest_regressor',
        ]:
            if 'target' not in kwargs:
                raise ValueError(f"'target' parameter is required for {model_type}")
            if 'features' not in kwargs:
                raise ValueError(f"'features' parameter is required for {model_type}")

        # Classification models
        if model_type == 'logistic':
            return LogisticRegressionTrainer(train_data, **kwargs)
        elif model_type == 'random_forest_classifier':
            return RandomForestClassifierTrainer(train_data, **kwargs)

        # Regression models
        elif model_type == 'linear':
            return LinearRegressionTrainer(train_data, **kwargs)
        elif model_type == 'random_forest_regressor':
            return RandomForestRegressorTrainer(train_data, **kwargs)

        else:
            raise ValueError(f"Model type '{model_type}' not supported.")
