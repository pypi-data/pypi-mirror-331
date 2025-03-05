# yonoma-client

A Python client for the Yonoma API, designed for managing email marketing automation.

## Installation

You can install the package using pip:

```sh
pip install yonoma
```

## Usage

### Importing the Client

```python
from yonoma_client import YonomaClient

client = YonomaClient(api_key="your_api_key")
```

### Fetching Lists
```python
lists = client.get_lists()
print(lists)
```

### Creating a Contact
```python
response = client.create_contact(list_id="your_list_id", email="test@example.com", name="John Doe")
print(response)
```

## Requirements
- Python >= 3.6
- `requests` library

## License
This project is licensed under the MIT License.