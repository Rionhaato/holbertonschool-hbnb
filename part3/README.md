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

## Task 6 Notes

Task 6 maps the shared base fields and the `User` entity to SQLAlchemy and
introduces a dedicated `UserRepository`.

What changed:

- `hbnb/models/base_model.py` now provides SQLAlchemy-compatible `id`,
  `created_at`, and `updated_at` fields as a reusable abstract base mixin
- `hbnb/models/user.py` is now a mapped SQLAlchemy model for the `users` table
- `hbnb/persistence/user_repository.py` implements SQLAlchemy-backed user
  persistence
- `hbnb/services/facade.py` now routes user CRUD and authentication through the
  dedicated user repository
- `hbnb/__init__.py` initializes the database tables for mapped user storage

## Task 7 Notes

Task 7 extends SQLAlchemy mapping to the remaining core entities: `Place`,
`Review`, and `Amenity`.

What changed:

- `hbnb/models/place.py` is now a mapped `places` table model
- `hbnb/models/review.py` is now a mapped `reviews` table model
- `hbnb/models/amenity.py` is now a mapped `amenities` table model
- `hbnb/__init__.py` now registers all mapped entities in the SQLAlchemy model
  map
- the generic `SQLAlchemyRepository` now supports CRUD for all mapped entities
- repository tests now cover persistent storage for `User`, `Place`, `Review`,
  and `Amenity`

Important limitation:

- no SQLAlchemy relationships are defined yet
- foreign keys and object relationships will be added in later tasks
- for now, only the core scalar attributes are mapped and stored

## Task 8 Notes

Task 8 adds the ORM relationships between the mapped entities.

What changed:

- `User.places` and `User.reviews` are now one-to-many relationships
- `Place.owner` links each place back to its owning user
- `Place.reviews` and `Review.place` form the place-to-review relationship
- `Review.author` links each review back to its user
- `Place` and `Amenity` are now connected through a many-to-many association
  table named `place_amenity`
- the facade now converts incoming `amenity_ids` into real SQLAlchemy
  relationship assignments when creating or updating places

This gives the project proper bidirectional ORM navigation while keeping the
existing API payload format based on `owner_id`, `user_id`, `place_id`, and
`amenity_ids`.

## Task 9 Notes

Task 9 adds raw SQL scripts so the full schema can be created without relying
on SQLAlchemy.

Files added:

- `sql/schema.sql`
  Creates all tables, constraints, indexes, and the `place_amenity`
  association table.
- `sql/seed_data.sql`
  Inserts the initial administrator row and a starter amenity set.
- `sql/crud_checks.sql`
  Runs sample create, read, update, and delete statements against the schema.

Suggested SQLite usage:

```bash
sqlite3 hbnb_dev.db < sql/schema.sql
sqlite3 hbnb_dev.db < sql/seed_data.sql
sqlite3 hbnb_dev.db < sql/crud_checks.sql
```

Important note:

- the admin seed row uses a placeholder bcrypt hash because a bcrypt generator
  is not available in this local environment
- replace `REPLACE_WITH_VALID_BCRYPT_HASH` with a real bcrypt hash before using
  the seeded account for application login

## Task 10 Notes

Task 10 adds a Mermaid ER diagram for the Part 3 database schema.

Files added:

- `diagrams/database-er-diagram.mmd`
  Mermaid ER diagram covering `users`, `places`, `reviews`, `amenities`, and
  `place_amenity`.

Diagram scope:

- one-to-many: `users` to `places`
- one-to-many: `users` to `reviews`
- one-to-many: `places` to `reviews`
- many-to-many: `places` to `amenities` through `place_amenity`

Rendering note:

- the Mermaid CLI tool (`mmdc`) is not installed in this local environment, so
  PNG and PDF exports were not generated here
- the `.mmd` source is ready to render once Mermaid CLI is available
