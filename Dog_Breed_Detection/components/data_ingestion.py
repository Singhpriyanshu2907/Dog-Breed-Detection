import os
import sys
import zipfile
import requests
from Dog_Breed_Detection.logger import logging
from Dog_Breed_Detection.exception import AppException
from Dog_Breed_Detection.entity.config_entity import DataIngestionConfig
from Dog_Breed_Detection.entity.artifacts_entity import DataIngestionArtifact

class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig = DataIngestionConfig()):
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise AppException(e, sys)

    def download_data(self) -> str:
        """
        Fetch data from the provided URL and save it as a zip file.
        """
        try:
            dataset_url = self.data_ingestion_config.data_download_url
            zip_download_dir = self.data_ingestion_config.data_ingestion_dir
            os.makedirs(zip_download_dir, exist_ok=True)

            data_file_name = "dataset.zip"
            zip_file_path = os.path.join(zip_download_dir, data_file_name)

            logging.info(f"Downloading dataset from {dataset_url} into file {zip_file_path}")

            # Download the dataset in chunks
            response = requests.get(dataset_url, stream=True)
            response.raise_for_status()  # Check for HTTP errors

            with open(zip_file_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)

            logging.info(f"Dataset successfully downloaded to {zip_file_path}")
            return zip_file_path

        except Exception as e:
            raise AppException(e, sys)

    def extract_zip_file(self, zip_file_path: str) -> str:
        """
        Extracts the zip file into the feature store directory.
        """
        try:
            feature_store_path = self.data_ingestion_config.feature_store_file_path
            os.makedirs(feature_store_path, exist_ok=True)

            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(feature_store_path)

            logging.info(f"Extracted zip file: {zip_file_path} into directory: {feature_store_path}")
            return feature_store_path

        except Exception as e:
            raise AppException(e, sys)

    def initiate_data_ingestion(self) -> DataIngestionArtifact:
        """
        Orchestrates the data ingestion process: downloading and extracting the dataset.
        """
        logging.info("Initiating data ingestion...")
        try:
            # Download the dataset
            zip_file_path = self.download_data()

            # Extract the dataset
            feature_store_path = self.extract_zip_file(zip_file_path)

            # Create the artifact
            data_ingestion_artifact = DataIngestionArtifact(
                data_zip_file_path=zip_file_path,
                feature_store_path=feature_store_path
            )

            logging.info(f"Data ingestion completed successfully. Artifact: {data_ingestion_artifact}")
            return data_ingestion_artifact

        except Exception as e:
            raise AppException(e, sys)
