import hashlib
import io
import json
import os
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import pandas as pd
from minio import Minio
from minio.error import S3Error

from ml_demo_provider.operators.ml.dataset_storage import DatasetStorage


class MinioDatasetStorage(DatasetStorage):
    """
    Implementation of DatasetStorage using Minio for object storage.
    """

    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket_name: str = "ml-datasets",
        secure: bool = True,
    ):
        """
        Initialize MinioDatasetStorage.

        Args:
            endpoint: Minio server endpoint (e.g., 'minio.example.com:9000')
            access_key: Access key for Minio
            secret_key: Secret key for Minio
            bucket_name: Bucket to store datasets in
            secure: Whether to use HTTPS
        """
        self.client = Minio(
            endpoint=endpoint, access_key=access_key, secret_key=secret_key, secure=secure
        )
        self.bucket_name = bucket_name

        # Ensure bucket exists
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)

    def _generate_version(self, df: pd.DataFrame) -> str:
        """Generate a version hash based on dataframe content and timestamp."""
        timestamp = datetime.now().isoformat()
        df_hash = hashlib.md5(pd.util.hash_pandas_object(df).values).hexdigest()
        return f"{df_hash[:8]}_{timestamp}"

    def _get_dataset_path(self, dataset_name: str, version: str) -> str:
        """Generate the object path for a dataset version."""
        return f"{dataset_name}/{version}/data.parquet"

    def _get_metadata_path(self, dataset_name: str, version: str) -> str:
        """Generate the object path for dataset metadata."""
        return f"{dataset_name}/{version}/metadata.json"

    def _get_versions_path(self, dataset_name: str) -> str:
        """Generate the object path for dataset versions index."""
        return f"{dataset_name}/_versions.json"

    def _update_versions_index(
        self, dataset_name: str, version: str, metadata: Dict[str, Any]
    ) -> None:
        """Update the versions index file with new version information."""
        versions = []

        # Try to get existing versions index
        try:
            response = self.client.get_object(
                self.bucket_name, self._get_versions_path(dataset_name)
            )
            versions = json.loads(response.read().decode('utf-8'))
        except S3Error:
            # Index doesn't exist yet
            pass

        # Add new version to index
        version_info = {
            "version": version,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata,
        }

        # Add new version at the beginning (latest first)
        versions.insert(0, version_info)

        # Save updated index
        versions_json = json.dumps(versions).encode('utf-8')
        self.client.put_object(
            bucket_name=self.bucket_name,
            object_name=self._get_versions_path(dataset_name),
            data=io.BytesIO(versions_json),
            length=len(versions_json),
            content_type="application/json",
        )

    def save_dataframe(
        self,
        dataset_name: str,
        df: pd.DataFrame,
        version: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Save a pandas dataframe to Minio storage."""
        # Generate version if not provided
        if version is None:
            version = self._generate_version(df)

        # Default metadata if not provided
        if metadata is None:
            metadata = {}

        # Add basic info to metadata
        metadata.update(
            {
                "rows": len(df),
                "columns": list(df.columns),
                "dtypes": {col: str(df[col].dtype) for col in df.columns},
                "created_at": datetime.now().isoformat(),
            }
        )

        # Save dataframe as parquet
        buffer = io.BytesIO()
        df.to_parquet(buffer)
        buffer.seek(0)
        data_size = buffer.getbuffer().nbytes

        self.client.put_object(
            bucket_name=self.bucket_name,
            object_name=self._get_dataset_path(dataset_name, version),
            data=buffer,
            length=data_size,
            content_type="application/octet-stream",
        )

        # Save metadata
        metadata_json = json.dumps(metadata).encode('utf-8')
        self.client.put_object(
            bucket_name=self.bucket_name,
            object_name=self._get_metadata_path(dataset_name, version),
            data=io.BytesIO(metadata_json),
            length=len(metadata_json),
            content_type="application/json",
        )

        # Update versions index
        self._update_versions_index(dataset_name, version, metadata)

        return version

    def load_dataframe(self, dataset_name: str, version: Optional[str] = None) -> pd.DataFrame:
        """Load a pandas dataframe from Minio storage."""
        # If version not specified, get latest
        if version is None:
            versions = self.list_versions(dataset_name)
            if not versions:
                raise ValueError(f"No versions found for dataset '{dataset_name}'")
            version = versions[0]["version"]  # Get latest (first in list)

        # Get the data object
        try:
            response = self.client.get_object(
                bucket_name=self.bucket_name,
                object_name=self._get_dataset_path(dataset_name, version),
            )

            # Read parquet directly from response stream
            df = pd.read_parquet(io.BytesIO(response.read()))
            return df

        except S3Error as e:
            raise ValueError(
                f"Error loading dataset '{dataset_name}' version '{version}': {str(e)}"
            )

    def list_versions(self, dataset_name: str) -> List[Dict[str, Any]]:
        """List all available versions of a dataset."""
        try:
            response = self.client.get_object(
                bucket_name=self.bucket_name, object_name=self._get_versions_path(dataset_name)
            )
            return json.loads(response.read().decode('utf-8'))
        except S3Error:
            # If versions index doesn't exist, return empty list
            return []

    def get_metadata(self, dataset_name: str, version: Optional[str] = None) -> Dict[str, Any]:
        """Get metadata for a specific dataset version."""
        # If version not specified, get latest
        if version is None:
            versions = self.list_versions(dataset_name)
            if not versions:
                raise ValueError(f"No versions found for dataset '{dataset_name}'")
            version = versions[0]["version"]  # Get latest (first in list)

        try:
            response = self.client.get_object(
                bucket_name=self.bucket_name,
                object_name=self._get_metadata_path(dataset_name, version),
            )
            return json.loads(response.read().decode('utf-8'))
        except S3Error as e:
            raise ValueError(
                f"Error getting metadata for dataset '{dataset_name}' version '{version}': {str(e)}"
            )

    def delete_version(self, dataset_name: str, version: str) -> bool:
        """Delete a specific version of a dataset."""
        try:
            # Remove data and metadata objects
            self.client.remove_object(
                self.bucket_name, self._get_dataset_path(dataset_name, version)
            )
            self.client.remove_object(
                self.bucket_name, self._get_metadata_path(dataset_name, version)
            )

            # Update versions index
            versions = self.list_versions(dataset_name)
            updated_versions = [v for v in versions if v["version"] != version]

            # Save updated index
            if versions != updated_versions:
                versions_json = json.dumps(updated_versions).encode('utf-8')
                self.client.put_object(
                    bucket_name=self.bucket_name,
                    object_name=self._get_versions_path(dataset_name),
                    data=io.BytesIO(versions_json),
                    length=len(versions_json),
                    content_type="application/json",
                )

            return True
        except S3Error:
            return False
