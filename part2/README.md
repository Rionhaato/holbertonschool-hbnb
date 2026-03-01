# HBnB Evolution - Part 2

This directory contains the initial implementation of the Presentation and
Business Logic layers for HBnB.

## Project Structure

- `hbnb/api`: Flask-RESTx API bootstrap and namespaces
- `hbnb/models`: Business entities (`User`, `Place`, `Review`, `Amenity`)
- `hbnb/services`: Facade layer that coordinates use-cases
- `hbnb/persistence`: Repository contract and in-memory implementation

## Run

```bash
cd part2
pip install -r requirements.txt
python run.py
```

Health check endpoint:

`GET /api/v1/status`

## Testing

Automated tests:

```bash
cd part2
python -m unittest discover -s tests -v
```

Manual tests:

1. Run the app: `python run.py`
2. Use Swagger docs at `http://127.0.0.1:5000/api/v1/`
3. Execute cURL checks from `tests/testing_report.md`
