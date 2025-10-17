-- Seed episodes data
-- Inserts initial episode data

INSERT INTO episodes (
    episode_number,
    title,
    file_name,
    date_published,
    is_processed
) VALUES 
    (180, 'A SCOTUS ''24-''25" term review with Professor Jack Beermann', 'AGD-180-7.m4a', '2025-08-12', FALSE),
    (181, 'Six in Sixty: creeping authoritarianism', 'AGD-181-7.m4a', '2025-08-26', FALSE),
    (182, 'How tariffs are affecting the global economy and geopolitics with Lydia DePillis', 'AGD-182-7.m4a', '2025-09-02', FALSE)
ON CONFLICT (episode_number) DO UPDATE
SET 
    title = EXCLUDED.title,
    file_name = EXCLUDED.file_name,
    date_published = EXCLUDED.date_published,
    is_processed = EXCLUDED.is_processed;

INSERT INTO speakers (name)
VALUES
    ('Ricky Ghoshroy'),
    ('Brendan Kelly'),
    ('Professor Jack Beermann'),
    ('Lydia DePhillis')
ON CONFLICT (name) DO NOTHING;

-- Seed the per-episode speaker map with speaker numbers and roles
INSERT INTO episode_speakers (
    episode_id,
    speaker_id,
    speaker_number,
    role
)
SELECT
    mapping.episode_number,
    s.id,
    mapping.speaker_number,
    mapping.role::speaker_role_enum
FROM (
    VALUES
        (180, 1, 'Ricky Ghoshroy', 'host'),
        (180, 2, 'Brendan Kelly', 'host'),
        (180, 3, 'Professor Jack Beermann', 'guest'),
        (181, 1, 'Ricky Ghoshroy', 'host'),
        (181, 2, 'Brendan Kelly', 'host'),
        (182, 1, 'Ricky Ghoshroy', 'host'),
        (182, 2, 'Brendan Kelly', 'host'),
        (182, 3, 'Lydia DePhillis', 'guest')
) AS mapping(episode_number, speaker_number, speaker_name, role)
JOIN speakers s ON s.name = mapping.speaker_name
ON CONFLICT (episode_id, speaker_number) DO UPDATE
SET role = EXCLUDED.role;
