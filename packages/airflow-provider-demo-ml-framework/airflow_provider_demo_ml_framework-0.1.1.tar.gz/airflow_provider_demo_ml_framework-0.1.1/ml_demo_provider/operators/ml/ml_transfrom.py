from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import pandas as pd


class MLTransfrom(ABC):
    """
    Abstract base class for dataset storage in ML pipelines.
    Provides versioning and pandas dataframe support.
    """

    @abstractmethod
    def save_dataframe(
        self,
        dataset_name: str,
        df: pd.DataFrame,
        version: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Save a pandas dataframe to storage with versioning support.

        Args:
            dataset_name: Name of the dataset
            df: Pandas dataframe to save
            version: Optional specific version string. If None, auto-generated.
            metadata: Optional dictionary of metadata about the dataset

        Returns:
            str: Version identifier of the saved dataset
        """
        pass

    @abstractmethod
    def load_dataframe(self, dataset_name: str, version: Optional[str] = None) -> pd.DataFrame:
        """
        Load a pandas dataframe from storage.

        Args:
            dataset_name: Name of the dataset
            version: Optional specific version to load. If None, loads latest.

        Returns:
            pd.DataFrame: The loaded dataframe
        """
        pass

    @abstractmethod
    def list_versions(self, dataset_name: str) -> List[Dict[str, Any]]:
        """
        List all available versions of a dataset.

        Args:
            dataset_name: Name of the dataset

        Returns:
            List[Dict]: List of version details with metadata
        """
        pass

    @abstractmethod
    def get_metadata(self, dataset_name: str, version: Optional[str] = None) -> Dict[str, Any]:
        """
        Get metadata for a specific dataset version.

        Args:
            dataset_name: Name of the dataset
            version: Optional specific version. If None, gets latest.

        Returns:
            Dict: Metadata for the specified dataset version
        """
        pass

    @abstractmethod
    def delete_version(self, dataset_name: str, version: str) -> bool:
        """
        Delete a specific version of a dataset.

        Args:
            dataset_name: Name of the dataset
            version: Version to delete

        Returns:
            bool: True if successful, False otherwise
        """
        pass
