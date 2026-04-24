WITH flares AS (
    SELECT
        flare_id,
        class_type,
        begin_time::timestamp as flare_time
    FROM fact_space_weather
),
orbital AS (
    SELECT
        timestamp::timestamp as orbital_time,
        distance_from_earth_km,
        ABS(distance_from_earth_km - LAG(distance_from_earth_km) OVER (ORDER BY timestamp)) as distance_change
    FROM fact_orbital_data
)
SELECT
    f.flare_id,
    f.class_type as flare_class,
    f.flare_time,
    o.orbital_time,
    o.distance_from_earth_km,
    o.distance_change,
    ROUND(ABS(EXTRACT(EPOCH FROM (f.flare_time - o.orbital_time)) / 3600)::numeric, 2) as hours_apart,
    CASE
        WHEN ABS(EXTRACT(EPOCH FROM (f.flare_time - o.orbital_time)) / 3600) < 6
        THEN 'POSSIBLE_INTERFERENCE'
        ELSE 'NO_CORRELATION'
    END as correlation_flag
FROM flares f
CROSS JOIN orbital o
WHERE ABS(EXTRACT(EPOCH FROM (f.flare_time - o.orbital_time)) / 3600) < 6
ORDER BY f.flare_time