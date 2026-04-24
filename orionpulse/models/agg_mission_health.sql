WITH daily_distance AS (
    SELECT
        LEFT(timestamp, 10) as mission_date,
        AVG(distance_from_earth_km) as avg_distance_km
    FROM fact_orbital_data
    GROUP BY LEFT(timestamp, 10)
),
daily_flares AS (
    SELECT
        LEFT(begin_time, 10) as mission_date,
        COUNT(*) as flare_count,
        SUM(CASE WHEN class_type LIKE 'X%' THEN 3
                 WHEN class_type LIKE 'M%' THEN 2
                 WHEN class_type LIKE 'C%' THEN 1
                 ELSE 0 END) as flare_severity_score
    FROM fact_space_weather
    GROUP BY LEFT(begin_time, 10)
)
SELECT
    d.mission_date,
    d.avg_distance_km,
    COALESCE(f.flare_count, 0) as flare_count,
    COALESCE(f.flare_severity_score, 0) as flare_severity,
    CASE
        WHEN COALESCE(f.flare_severity_score, 0) >= 4 THEN 'RED'
        WHEN COALESCE(f.flare_severity_score, 0) >= 2 THEN 'YELLOW'
        ELSE 'GREEN'
    END as mission_health,
    100 - (COALESCE(f.flare_severity_score, 0) * 10) as health_score
FROM daily_distance d
LEFT JOIN daily_flares f ON d.mission_date = f.mission_date
ORDER BY d.mission_date