-- OrionPulse: Time dimension
-- Breaks every orbital timestamp into granular time attributes
-- Enables easy filtering by day, hour, week in downstream queries

SELECT
    timestamp::timestamp as timestamp,
    DATE(timestamp::timestamp) as date,
    EXTRACT(HOUR FROM timestamp::timestamp) as hour,
    EXTRACT(DOW FROM timestamp::timestamp) as day_of_week,
    TO_CHAR(timestamp::timestamp, 'Day') as day_name,
    EXTRACT(WEEK FROM timestamp::timestamp) as week_number,
    CASE
        WHEN EXTRACT(HOUR FROM timestamp::timestamp) < 6 THEN 'Night'
        WHEN EXTRACT(HOUR FROM timestamp::timestamp) < 12 THEN 'Morning'
        WHEN EXTRACT(HOUR FROM timestamp::timestamp) < 18 THEN 'Afternoon'
        ELSE 'Evening'
    END as time_of_day,
    (DATE(timestamp::timestamp) - DATE('2026-04-01')) + 1 as mission_day_number
FROM fact_orbital_data
ORDER BY timestamp