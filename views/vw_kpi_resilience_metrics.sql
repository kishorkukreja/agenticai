-- 2. KPI Resilience Metrics View
CREATE VIEW vw_kpi_resilience_metrics AS
SELECT 
    kpi_id,
    kpi_name,
    kpi_category,
    COUNT(DISTINCT event_id) as total_events_affecting,
    -- Impact severity
    ROUND(AVG(immediate_impact_avg - pre_event_avg), 2) as avg_immediate_impact,
    ROUND(AVG(recovery_period_avg - pre_event_avg), 2) as avg_recovery_impact,
    -- Recovery rate
    ROUND(AVG(CASE 
        WHEN immediate_impact_avg < pre_event_avg 
        THEN (recovery_period_avg - immediate_impact_avg) / ABS(immediate_impact_avg - pre_event_avg) 
        ELSE NULL 
    END) * 100, 2) as avg_recovery_rate,
    -- Threshold breaches
    ROUND(AVG(CAST(below_threshold_count AS FLOAT) / 
        NULLIF(total_measurements, 0) * 100), 2) as threshold_breach_rate,
    -- Resilience score (higher is better)
    ROUND(
        (1 - AVG(CAST(below_threshold_count AS FLOAT) / NULLIF(total_measurements, 0))) *
        (1 + AVG(CASE 
            WHEN immediate_impact_avg < pre_event_avg 
            THEN (recovery_period_avg - immediate_impact_avg) / ABS(immediate_impact_avg - pre_event_avg)
            ELSE 1 
        END)) * 100, 2) as resilience_score
FROM vw_kpi_event_impact
GROUP BY kpi_id, kpi_name, kpi_category;
