# Database Class Documentation

## Overview

This `Database` class is designed to manage interactions with the SQL database using SQLAlchemy.
It handles the creation, querying, and deletion of various database objects related to a `Study`.
This class also provides error handling and session management to ensure smooth database operations.

You can add operation performed in the database here, or in external file using function that get this class as
parameter.

### Initialization

- **Database Initialization**: Connects to the database using a provided URL and sets up the SQLAlchemy engine and
  session maker.

### Utility Methods

- **UUID Generation**: Provides a method to generate a universally unique identifier (UUID).
- **Session Management**: Offers context manager support to create and manage database sessions.

### Data Insertion

- **Insert Study**: Inserts a `Study` into the database from a dictionary containing study details and foreign keys.

### Data Querying

- **Get All Studies**: Retrieves all studies with their associated objects.
- **Query Posts by Study**: Gets a list of posts related to a specific study.
- **Query Posts by Study as Dictionary**: Returns posts related to a specific study in a dictionary format.
- **Query Comments by Study**: Retrieves a list of comments associated with a specific study.
- **Query Comments by Post**: Gets comments related to a specific post.
- **Query Sources by Study**: Fetches a list of sources related to a specific study.
- **Query Study Comments and Posts**: Retrieves all comments, posts, and sources associated with a study.

### Data Updating

- **Update Study Enabled**: Updates the enabled status and last modified time of a study.

### Data Deletion

- **Delete Study**: Deletes a study along with all associated posts, comments, and sources.

### User Management

- **Generate Debug Test User**: Creates a debug test user if it does not already exist.

## Error Handling

- **Exception Decorator**: The `handle_db_query_exceptions` decorator handles database exceptions and logs errors,
  returning an empty collection when exceptions occur.

## Example Usage

### Creating a Database Instance

```python
db = Database(db_url="your_database_url")
```

### Using the Session Context Manager

```python
with db.session() as session:
    # Perform database operations
    pass
```

### Inserting a Study

```python
study_dict = {
    "basic_settings": ...,
    "advanced_settings": ...,
    # Other study details
}
await db.insert_study(study_dict)
```

### Querying Data

```python
all_studies = await db.get_all_studies()
posts = await db.query_posts_list_by_study("study_id")
```

### Updating a Study

```python
parameters = {"id": "study_id", "enabled": True, "last_modified_time": "timestamp"}
await db.update_study_enabled(parameters)
```

### Deleting a Study

```python
await db.delete_study("study_id")
```

### Generating a Debug Test User

```python
db.generate_debug_test_user()
```