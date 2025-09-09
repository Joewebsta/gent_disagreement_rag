-- Seed episodes data
-- Inserts initial episode data

INSERT INTO episodes (
    episode_number,
    title,
    file_name, 
    date_published
) VALUES 
    ('180', 'A SCOTUS ''24-''25" term review with Professor Jack Beermann', 'AGD-180.mp3', '2025-08-12'),
    ('181', 'Six in Sixty: creeping authoritarianism', 'AGD-181.mp3', '2025-08-26'),
    ('182', 'How tariffs are affecting the global economy and geopolitics with Lydia DePillis', 'AGD-182-7.mp3', '2025-09-02')
ON CONFLICT (episode_number) DO NOTHING;
