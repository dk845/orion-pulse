-- OrionPulse: Flare severity dimension
-- Maps raw NASA flare class codes to human readable severity levels
-- Joins to fact_space_weather on class_type prefix

WITH flare_classes AS (
    SELECT DISTINCT class_type FROM fact_space_weather
)
SELECT
    class_type,
    LEFT(class_type, 1) as class_letter,
    CASE LEFT(class_type, 1)
        WHEN 'X' THEN 'Extreme'
        WHEN 'M' THEN 'Strong'
        WHEN 'C' THEN 'Moderate'
        WHEN 'B' THEN 'Minor'
        ELSE 'Unknown'
    END as severity_label,
    CASE LEFT(class_type, 1)
        WHEN 'X' THEN 5
        WHEN 'M' THEN 4
        WHEN 'C' THEN 3
        WHEN 'B' THEN 2
        ELSE 1
    END as severity_rank,
    CASE LEFT(class_type, 1)
        WHEN 'X' THEN 'Can cause complete radio blackouts and radiation storms'
        WHEN 'M' THEN 'Can cause brief radio blackouts at polar regions'
        WHEN 'C' THEN 'Minor impact on radio communications'
        WHEN 'B' THEN 'Rarely impacts Earth'
        ELSE 'Below detection threshold'
    END as impact_description
FROM flare_classes
ORDER BY severity_rank DESC