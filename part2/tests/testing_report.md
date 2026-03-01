# HBnB Part 2 - Testing and Validation Report

## 1. Scope

This report validates the Part 2 endpoints and model rules for:

- Users (`POST`, `GET`, `PUT`)
- Amenities (`POST`, `GET`, `PUT`)
- Places (`POST`, `GET`, `PUT`, plus `/places/<id>/reviews`)
- Reviews (`POST`, `GET`, `PUT`, `DELETE`)

## 2. Automated Tests

Test files:

- `tests/test_models.py`
- `tests/test_api.py`

Command:

```bash
cd part2
python -m unittest discover -s tests -v
```

Coverage highlights:

- Model attribute validation (email, coordinates, rating, required names)
- API status codes for success and error paths
- Password exclusion in user API responses
- Place composed payload includes owner, amenities, and reviews
- Review deletion behavior and post-delete `404`

## 3. Manual Black-Box Tests (cURL)

Run app:

```bash
cd part2
python run.py
```

Open Swagger docs:

- `http://127.0.0.1:5000/api/v1/`

### 3.1 Health Check

```bash
curl -i http://127.0.0.1:5000/api/v1/status
```

Expected:

- `200 OK`
- Body: `{"status":"OK"}`

### 3.2 Users

Create:

```bash
curl -i -X POST http://127.0.0.1:5000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d "{\"first_name\":\"John\",\"last_name\":\"Doe\",\"email\":\"john@example.com\",\"password\":\"secret\"}"
```

Expected:

- `201 Created`
- No `password` field in response body

List:

```bash
curl -i http://127.0.0.1:5000/api/v1/users/
```

Expected:

- `200 OK`
- Array of users, each without `password`

Invalid email:

```bash
curl -i -X POST http://127.0.0.1:5000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d "{\"first_name\":\"Bad\",\"last_name\":\"Email\",\"email\":\"not-an-email\",\"password\":\"secret\"}"
```

Expected:

- `400 Bad Request`

### 3.3 Amenities

Create:

```bash
curl -i -X POST http://127.0.0.1:5000/api/v1/amenities/ \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"WiFi\"}"
```

Expected:

- `201 Created`

Update:

```bash
curl -i -X PUT http://127.0.0.1:5000/api/v1/amenities/<amenity_id> \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Air Conditioning\"}"
```

Expected:

- `200 OK`

### 3.4 Places

Create:

```bash
curl -i -X POST http://127.0.0.1:5000/api/v1/places/ \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Loft\",\"description\":\"City center\",\"price\":120,\"latitude\":40.7128,\"longitude\":-74.0060,\"owner_id\":\"<user_id>\",\"amenity_ids\":[\"<amenity_id>\"]}"
```

Expected:

- `201 Created`
- Includes `owner` and `amenities` fields

Validation error (latitude out of range):

```bash
curl -i -X POST http://127.0.0.1:5000/api/v1/places/ \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Bad\",\"description\":\"x\",\"price\":10,\"latitude\":200,\"longitude\":0,\"owner_id\":\"<user_id>\",\"amenity_ids\":[]}"
```

Expected:

- `400 Bad Request`

### 3.5 Reviews

Create:

```bash
curl -i -X POST http://127.0.0.1:5000/api/v1/reviews/ \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"Great stay\",\"rating\":5,\"user_id\":\"<user_id>\",\"place_id\":\"<place_id>\"}"
```

Expected:

- `201 Created`

List place reviews:

```bash
curl -i http://127.0.0.1:5000/api/v1/places/<place_id>/reviews
```

Expected:

- `200 OK`
- Array with related reviews

Delete review:

```bash
curl -i -X DELETE http://127.0.0.1:5000/api/v1/reviews/<review_id>
```

Expected:

- `200 OK`

Get deleted review:

```bash
curl -i http://127.0.0.1:5000/api/v1/reviews/<review_id>
```

Expected:

- `404 Not Found`

## 4. Edge Cases Validated

- Missing required fields return `400`
- Invalid types/ranges (email, coordinates, rating) return `400`
- Unknown IDs return `404`
- Review delete path is functional and idempotence is enforced by `404` on later retrieval

## 5. Notes

- `DELETE` remains intentionally unavailable for users, amenities, and places in Part 2.
