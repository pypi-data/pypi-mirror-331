# NanoJson library provided by Mohammed Ghanam.

![PyPI - Version](https://img.shields.io/pypi/v/NanoJson?color=blue&label=version)  
![Python](https://img.shields.io/badge/python-3.6%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)  
![Status](https://img.shields.io/badge/status-active-success)  

--------

NanoJson is a Python library designed to make working with JSON files easy and seamless. It offers a variety of functions to handle JSON data, such as reading, writing, modifying, and managing lists within JSON files, all with a simple and intuitive interface.

## Features

- **Reading JSON data**: Easily read JSON data from a file.
- **Writing JSON data**: Write or update JSON data to a file.
- **Updating JSON**: Modify specific keys and values within a JSON file.
- **Deleting keys**: Remove specific keys from a JSON object.
- **Search for keys**: Search for and retrieve values associated with a specific key.
- **Managing lists**: Append or remove values from lists within JSON data.

## Installation

To install **NanoJson**, use `pip`:

```bash
pip install NanoJson
```

## Usage

First, you must **import it**:
```python
import NanoJson
```

### 1) Reading JSON Data

You can read the contents of a JSON file and either print it as a formatted string or as a Python dictionary.

Example:

```python
# Initialize the JSON helper with the path to your JSON file
json_helper = NanoJson("data.json")
```

# Read the JSON data as a Python dictionary
```python
data = json_helper.read_json()
```

# Print the formatted JSON data
```python
formatted_data = json_helper.read_json(pretty=True)
```

### 2) Writing JSON Data

You can write new JSON data or update existing data in a file.

Example:

```python
# New data to write to the file
new_data = {"name": "John", "age": 30}

# Write the new data to the JSON file
json_helper.write_json(new_data)
```

### 3) Updating JSON Data

You can update a specific key with a new value in your JSON data.

Example:

```python
# Update the value of the "age" key
json_helper.update_json("age", 31)
```

### 4) Deleting Keys

You can delete a key from your JSON file.

Example:

```python
# Remove the key "name" from the JSON data
json_helper.delete_key("name")
```

### 5) Searching for a Key

You can search for a specific key in the JSON data and retrieve its value.

Example:

```python
# Get the value associated with the key "age"
age = json_helper.search_key("age")
```

### 6) Managing Lists

You can append or remove items from lists stored within your JSON file.

Example:

```python
# Append a new item to the list under the "items" key
json_helper.append_to_list("items", "new_item")

# Remove an item from the list under the "items" key
json_helper.remove_from_list("items", "old_item")
```

## For Contact:

- My telegram Account: [@midoghanam](https://t.me/midoghanam)
- My Channel: [@mido_ghanam](https://t.me/mido_ghanam)

## Best Regards ♡