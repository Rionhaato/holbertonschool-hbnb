# HBnB Evolution - Part 3

This directory contains the Part 3 backend baseline for HBnB Evolution.
Part 3 extends the previous stages by preparing the application for
authentication, authorization, and database-backed persistence.

## Part 3 Goals

In this phase, the project moves from a prototype-style backend toward a more
realistic application architecture. The main objectives are:

- introduce configuration-driven app setup
- prepare the backend for JWT authentication
- transition from in-memory persistence toward database persistence
- support different environments such as development, testing, and production
- keep the project structure scalable for the remaining tasks

## Task 0

Task 0 updates the Flask application factory so the app can be created with a
configuration object.

This is the foundation for the rest of Part 3 because later tasks will need
configuration values for:

- database connection settings
- JWT secret keys
- debug and testing flags
- environment-specific behavior

## What Was Implemented

The following Task 0 changes are included in this directory:

- a base `Config` class was added in `config.py`
- `create_app()` now accepts a configuration class
- the Flask app loads settings through `app.config.from_object(...)`
- `run.py` creates the app through the configuration-aware factory
- tests use a dedicated testing configuration through the same factory pattern

## Project Structure

- `config.py`
  Base application configuration used by the app factory.
- `run.py`
  Local entry point for starting the Flask application.
- `hbnb/__init__.py`
  Application factory definition for Part 3.
- `hbnb/api`
  Flask-RESTx API initialization and namespace registration.
- `hbnb/models`
  Domain models such as `User`, `Place`, `Review`, and `Amenity`.
- `hbnb/services`
  Facade layer coordinating use cases between the API and persistence.
- `hbnb/persistence`
  Current repository layer. At this stage it still uses in-memory storage and
  will be refactored in later tasks.
- `tests`
  Automated tests for models and API behavior.

## Application Factory

The project uses the Flask Application Factory pattern.

Current behavior:

- `create_app()` builds and configures the Flask app
- configuration is injected through a config class
- the facade is attached to `app.config["FACADE"]`
- API namespaces are registered after configuration is loaded

This makes the app easier to test and easier to adapt for multiple
environments.

## Configuration

The base configuration is defined in `config.py`.

Current settings:

- `DEBUG = False`
- `TESTING = False`
- `RESTX_MASK_SWAGGER = False`

These values are intentionally minimal for Task 0. Later tasks can extend this
module with development, testing, and production configurations.

## Run the Project

From the repository root:

```bash
cd part3
pip install -r requirements.txt
python run.py
```

The API should then be available locally on port `5000`.

Useful endpoint:

- `GET /api/v1/status`

Swagger documentation:

- `http://127.0.0.1:5000/api/v1/`

## Run the Tests

From `part3`:

```bash
python -m unittest discover -s tests -v
```

Note: API tests require the Flask dependencies from `requirements.txt`. If the
dependencies are not installed, those tests will be skipped.

## Current Status

Task 0 is complete.

At this point, Part 3 has:

- a dedicated `part3` working directory
- a configuration-aware Flask application factory
- the same baseline API and model structure carried over from Part 2
- a clean starting point for the authentication and database tasks that follow

## Next Steps

After Task 0, the next tasks will typically build toward:

- secure password handling
- JWT login and protected endpoints
- role-based access control
- SQLAlchemy integration
- relational database modeling
- environment-specific database configuration

## Task 5 Notes

Task 5 introduces the SQLAlchemy persistence foundation without enabling full
database-backed runtime behavior yet.

What was added:

- `Flask-SQLAlchemy` was added to `requirements.txt`
- `hbnb/extensions.py` now initializes a shared `db` extension
- `hbnb/persistence/sqlalchemy_repository.py` implements the repository
  contract using SQLAlchemy sessions
- `hbnb/__init__.py` now selects the repository backend through
  `REPOSITORY_TYPE`
- `config.py` now includes SQLAlchemy-related configuration values

Current behavior:

- the default repository remains `in_memory`
- if `REPOSITORY_TYPE=sqlalchemy`, the app will build a
  `SQLAlchemyRepository`
- mapped SQLAlchemy model classes must be provided through
  `SQLALCHEMY_MODEL_MAP`
- actual model mapping and database initialization are intentionally deferred to
  the next task

Example integration path for the next task:

```python
class DevelopmentConfig(Config):
    REPOSITORY_TYPE = "sqlalchemy"
    SQLALCHEMY_MODEL_MAP = {
        "User": UserModel,
        "Place": PlaceModel,
        "Review": ReviewModel,
        "Amenity": AmenityModel,
    }
```

At that point, the application factory can use the SQLAlchemy repository with
real mapped entities and a live database session.
