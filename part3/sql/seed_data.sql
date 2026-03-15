PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

-- Replace the password value below with a real bcrypt hash if you want the
-- seeded admin user to authenticate through the Flask app immediately.
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
    '00000000-0000-0000-0000-000000000001',
    '2026-03-15T00:00:00+00:00',
    '2026-03-15T00:00:00+00:00',
    'HBnB',
    'Administrator',
    'admin@hbnb.io',
    'REPLACE_WITH_VALID_BCRYPT_HASH',
    1
);

INSERT INTO amenities (id, created_at, updated_at, name) VALUES
    ('10000000-0000-0000-0000-000000000001', '2026-03-15T00:00:00+00:00', '2026-03-15T00:00:00+00:00', 'WiFi'),
    ('10000000-0000-0000-0000-000000000002', '2026-03-15T00:00:00+00:00', '2026-03-15T00:00:00+00:00', 'Pool'),
    ('10000000-0000-0000-0000-000000000003', '2026-03-15T00:00:00+00:00', '2026-03-15T00:00:00+00:00', 'Air Conditioning'),
    ('10000000-0000-0000-0000-000000000004', '2026-03-15T00:00:00+00:00', '2026-03-15T00:00:00+00:00', 'Kitchen'),
    ('10000000-0000-0000-0000-000000000005', '2026-03-15T00:00:00+00:00', '2026-03-15T00:00:00+00:00', 'Parking');

COMMIT;
