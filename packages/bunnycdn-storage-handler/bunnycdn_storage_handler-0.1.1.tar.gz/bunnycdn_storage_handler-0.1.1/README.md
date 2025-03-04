# BunnyCDN Storage Python Client

A Python client for interacting with BunnyCDN Storage API. This package provides a simple interface to upload, download, and manage files on BunnyCDN Storage.

## Installation

```bash
pip install bunnycdn-storage-handler
```

## Configuration

Before using the client, you need to set up your API key, storage zone, and pull zone. You can do this in one of the following ways:

### Method 1: Environment Variables

Set the following environment variables in your system:

- `BUNNYCDN_API_KEY`: Your BunnyCDN API key.
- `BUNNYCDN_STORAGE_ZONE`: Your BunnyCDN storage zone name.
- `BUNNYCDN_PULL_ZONE`: Your BunnyCDN pull zone name.

You can set environment variables in your terminal like this:

```bash
export BUNNYCDN_API_KEY='your_api_key'
export BUNNYCDN_STORAGE_ZONE='your_storage_zone'
export BUNNYCDN_PULL_ZONE='your_pull_zone'
```

### Method 2: Direct Initialization

Alternatively, you can pass the API key and zone names directly when initializing the `BunnyCDNStorage` client:

```python
from bunnycdn_storage import BunnyCDNStorage

# Initialize the client with your credentials
storage = BunnyCDNStorage(
    api_key='your_api_key',
    storage_zone='your_storage_zone',
    pull_zone='your_pull_zone'
)
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

## License

This project is licensed under the MIT License - see the LICENSE file for details. 