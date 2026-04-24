-- OrionPulse: Mission summary ready for multi-mission comparison
SELECT
    'Artemis II' as mission_name,
    MIN(LEFT(timestamp, 10)) as mission_start,
    MAX(LEFT(timestamp, 10)) as mission_end,
    COUNT(*) as total_orbital_snapshots,
    MAX(distance_from_earth_km) as max_distance_km,
    AVG(distance_from_earth_km) as avg_distance_km,
    (SELECT COUNT(*) FROM fact_space_weather) as total_flares
FROM fact_orbital_data