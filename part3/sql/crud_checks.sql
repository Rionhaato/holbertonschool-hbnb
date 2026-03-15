PRAGMA foreign_keys = ON;

-- Create a regular user.
INSERT INTO users (
    id,
    created_at,
    updated_at,
    first_name,
    last_name,
    email,
    password,
    is_admin
) VALUES (
    '20000000-0000-0000-0000-000000000001',
    '2026-03-15T01:00:00+00:00',
    '2026-03-15T01:00:00+00:00',
    'Jane',
    'Guest',
    'jane@example.com',
    'REPLACE_WITH_VALID_BCRYPT_HASH',
    0
);

-- Create a place owned by the seeded admin.
INSERT INTO places (
    id,
    created_at,
    updated_at,
    title,
    description,
    price,
    latitude,
    longitude,
    owner_id
) VALUES (
    '30000000-0000-0000-0000-000000000001',
    '2026-03-15T01:10:00+00:00',
    '2026-03-15T01:10:00+00:00',
    'Demo Loft',
    'A simple seeded place for SQL checks.',
    99.50,
    40.7128,
    -74.0060,
    '00000000-0000-0000-0000-000000000001'
);

-- Attach amenities to the place.
INSERT INTO place_amenity (place_id, amenity_id) VALUES
    ('30000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001'),
    ('30000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000004');

-- Create a review.
INSERT INTO reviews (
    id,
    created_at,
    updated_at,
    text,
    rating,
    user_id,
    place_id
) VALUES (
    '40000000-0000-0000-0000-000000000001',
    '2026-03-15T01:20:00+00:00',
    '2026-03-15T01:20:00+00:00',
    'Great test stay.',
    5,
    '20000000-0000-0000-0000-000000000001',
    '30000000-0000-0000-0000-000000000001'
);

-- Read: verify place with owner and amenities.
SELECT p.id, p.title, u.email AS owner_email
FROM places AS p
JOIN users AS u ON u.id = p.owner_id;

SELECT p.title, a.name
FROM place_amenity AS pa
JOIN places AS p ON p.id = pa.place_id
JOIN amenities AS a ON a.id = pa.amenity_id
ORDER BY a.name;

SELECT r.text, r.rating, u.email AS reviewer_email
FROM reviews AS r
JOIN users AS u ON u.id = r.user_id
WHERE r.place_id = '30000000-0000-0000-0000-000000000001';

-- Update.
UPDATE places
SET price = 120.00,
    updated_at = '2026-03-15T01:30:00+00:00'
WHERE id = '30000000-0000-0000-0000-000000000001';

-- Delete.
DELETE FROM reviews
WHERE id = '40000000-0000-0000-0000-000000000001';
