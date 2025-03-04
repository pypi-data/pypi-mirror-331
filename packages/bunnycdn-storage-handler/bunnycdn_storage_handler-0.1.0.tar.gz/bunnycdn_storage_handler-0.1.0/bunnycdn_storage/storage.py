import os
import requests
from pathlib import Path
from typing import Union, BinaryIO

class BunnyCDNStorage:
    """
    A client for interacting with BunnyCDN Storage API.
    
    This class provides methods to upload, download, and manage files on BunnyCDN Storage.
    """

    def __init__(self, api_key: str = None, storage_zone: str = None, pull_zone: str = None):
        """
        Initialize the BunnyCDN Storage client.
        
        Args:
            api_key (str, optional): BunnyCDN Storage API key. Defaults to environment variable BUNNYCDN_API_KEY.
            storage_zone (str, optional): Storage zone name. Defaults to environment variable BUNNYCDN_STORAGE_ZONE.
            pull_zone (str, optional): Pull zone name. Defaults to environment variable BUNNYCDN_PULL_ZONE.
        """
        self.apikey = api_key or os.getenv('BUNNYCDN_API_KEY')
        self.storage_zone = storage_zone or os.getenv('BUNNYCDN_STORAGE_ZONE')
        self.pull_zone = pull_zone or os.getenv('BUNNYCDN_PULL_ZONE')

        self.base_url = f'https://storage.bunnycdn.com/{self.storage_zone}/'
        self.headers = {
            'AccessKey': self.apikey,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def download_file(self, file_path: str, destination_path: str) -> Union[int, Exception]:
        """
        Download a file from BunnyCDN Storage.
        
        Args:
            file_path (str): Path to the file in BunnyCDN Storage.
            destination_path (str): Local path where the file should be saved.
            
        Returns:
            Union[int, Exception]: HTTP status code on success, Exception on failure.
        """
        file_url = f'{self.base_url}{file_path}'
        file_name = file_url.split("/")[-1]
        download_path = Path(destination_path, file_name)

        try:
            response = requests.get(file_url, headers=self.headers, stream=True)
            response.raise_for_status()
            with open(download_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            return response.status_code
        except Exception as error:
            return error

    def upload_file(self, storage_path: str, file_content: Union[bytes, BinaryIO], file_name: str) -> Union[str, Exception]:
        """
        Upload a file to BunnyCDN Storage.
        
        Args:
            storage_path (str): Path in storage where the file should be uploaded.
            file_content (Union[bytes, BinaryIO]): Content of the file to upload.
            file_name (str): Name of the file in storage.
            
        Returns:
            Union[str, Exception]: CDN URL on success, Exception on failure.
        """
        try:
            storage_url = f'{self.base_url}{storage_path}{file_name}'
            response = requests.put(storage_url, data=file_content, headers=self.headers)
            cdn_url = f'https://{self.pull_zone}.b-cdn.net/{storage_path}{file_name}'
            response.raise_for_status()
            return cdn_url
        except Exception as error:
            return error

    def object_exists(self, file_path: str) -> bool:
        """
        Check if a file exists in BunnyCDN Storage.
        
        Args:
            file_path (str): Path to the file in storage.
            
        Returns:
            bool: True if file exists, False otherwise.
        """
        file_url = f'{self.base_url}{file_path}'
        response = requests.get(file_url, headers=self.headers)
        return response.status_code == 200

    def delete_object(self, file_path: str) -> Union[int, Exception]:
        """
        Delete a file from BunnyCDN Storage.
        
        Args:
            file_path (str): Path to the file in storage.
            
        Returns:
            Union[int, Exception]: HTTP status code on success, Exception on failure.
        """
        try:
            file_url = f'{self.base_url}{file_path}'
            response = requests.delete(file_url, headers=self.headers)
            response.raise_for_status()
            return response.status_code
        except Exception as error:
            return error 