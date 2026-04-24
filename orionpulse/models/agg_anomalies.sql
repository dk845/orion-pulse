WITH stats AS (
    SELECT
        AVG(distance_from_earth_km) as mean_dist,
        STDDEV(distance_from_earth_km) as std_dist
    FROM fact_orbital_data
),
orbital_with_zscore AS (
    SELECT
        o.timestamp,
        o.distance_from_earth_km,
        ABS(o.distance_from_earth_km - s.mean_dist) / NULLIF(s.std_dist, 0) as z_score
    FROM fact_orbital_data o
    CROSS JOIN stats s
)
SELECT
    timestamp,
    distance_from_earth_km,
    ROUND(z_score::numeric, 2) as z_score,
    CASE
        WHEN z_score > 2 THEN 'HIGH'
        WHEN z_score > 1.5 THEN 'MEDIUM'
        ELSE 'NORMAL'
    END as anomaly_severity
FROM orbital_with_zscore
ORDER BY z_score DESC