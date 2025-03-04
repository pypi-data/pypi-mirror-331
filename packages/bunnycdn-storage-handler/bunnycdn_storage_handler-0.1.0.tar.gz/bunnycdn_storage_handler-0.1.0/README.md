# BunnyCDN Storage Python Client

A Python client for interacting with BunnyCDN Storage API. This package provides a simple interface to upload, download, and manage files on BunnyCDN Storage.

## Installation

```bash
pip install bunnycdn-storage-handler
```

## Usage

```python
from bunnycdn_storage import BunnyCDNStorage

# Initialize the client
storage = BunnyCDNStorage()

# Upload a file
cdn_url = storage.upload_file("path/in/storage/", file_content, "filename.txt")

# Download a file
status = storage.download_file("path/to/file.txt", "local/destination/path")

# Check if file exists
exists = storage.object_exists("path/to/file.txt")

# Delete a file
status = storage.delete_object("path/to/file.txt")
```

## Features

- Upload files to BunnyCDN Storage
- Download files from BunnyCDN Storage
- Check if files exist
- Delete files from storage
- Automatic CDN URL generation

## Configuration

The client requires the following configuration:
- API Key
- Storage Zone Name
- Pull Zone Name

## License

This project is licensed under the MIT License - see the LICENSE file for details. 