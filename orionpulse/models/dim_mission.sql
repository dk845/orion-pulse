-- OrionPulse: Mission dimension
-- Static metadata about the Artemis II mission
-- Structured for multi-mission comparison with Artemis I

SELECT
    'Artemis II' as mission_name,
    'ART-002' as mission_code,
    DATE('2026-04-01') as launch_date,
    DATE('2026-04-10') as splashdown_date,
    10 as mission_duration_days,
    4 as crew_size,
    'Reid Wiseman' as commander,
    'Victor Glover' as pilot,
    'Christina Koch, Jeremy Hansen' as mission_specialists,
    'Kennedy Space Center, LC-39B' as launch_site,
    'Pacific Ocean, San Diego' as landing_site,
    'SLS Block 1' as rocket,
    'Orion MPCV' as spacecraft,
    -1024 as jpl_spacecraft_id,
    412784 as max_distance_from_earth_km,
    252756 as max_distance_from_earth_miles,
    TRUE as crewed,
    'Lunar Flyby' as mission_type,
    'First crewed lunar mission since Apollo 17 in 1972' as mission_summary