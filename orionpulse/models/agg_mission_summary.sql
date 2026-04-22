-- OrionPulse: Daily mission summary aggregation
-- Joins space weather severity with orbital distance per day

WITH orbital AS (
    SELECT
        LEFT(timestamp, 10) as mission_date,
        AVG(distance_from_earth_km) as avg_distance_km,
        MAX(distance_from_earth_km) as max_distance_km
    FROM fact_orbital_data
    GROUP BY LEFT(timestamp, 10)
),

flares AS (
    SELECT
        LEFT(begin_time, 10) as mission_date,
        COUNT(*) as total_flares,
        MAX(class_type) as worst_flare_class
    FROM fact_space_weather
    GROUP BY LEFT(begin_time, 10)
)

SELECT
    o.mission_date,
    o.avg_distance_km,
    o.max_distance_km,
    COALESCE(f.total_flares, 0) as total_flares,
    COALESCE(f.worst_flare_class, 'None') as worst_flare_class
FROM orbital o
LEFT JOIN flares f ON o.mission_date = f.mission_date
ORDER BY o.mission_date