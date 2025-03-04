# db_manager

A simple database manager with optional MongoDB support.

## Installation
```
poetry install
poetry install --extras "mongodb"
```

## Usage
```python
from db_manager import DatabaseManager

# For MongoDB
manager = DatabaseManager(db_type="mongodb", connection_string="mongodb://localhost:27017")
client = manager.get_client()
```