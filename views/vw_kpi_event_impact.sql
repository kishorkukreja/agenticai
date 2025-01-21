CREATE VIEW vw_kpi_event_impact AS
SELECT 
    e.event_id,
    e.event_title,
    et.type_name as event_type,
    ec.category_name as event_category,
    es.severity_name,
    e.occurrence_date,
    eia.contract_id,
    ch.contract_number,
    kd.kpi_id,
    kd.kpi_name,
    kc.category_name as kpi_category,
    kd.target_threshold,
    -- Pre-event metrics (3 months before)
    AVG(CASE 
        WHEN ckm.measure_date BETWEEN DATE(e.occurrence_date, '-3 months') 
            AND DATE(e.occurrence_date, '-1 day')
        THEN ckm.actual_value 
    END) as pre_event_avg,
    -- Immediate impact (1 month after)
    AVG(CASE 
        WHEN ckm.measure_date BETWEEN DATE(e.occurrence_date) 
            AND DATE(e.occurrence_date, '+1 month')
        THEN ckm.actual_value 
    END) as immediate_impact_avg,
    -- Recovery period (1-3 months after)
    AVG(CASE 
        WHEN ckm.measure_date BETWEEN DATE(e.occurrence_date, '+1 month') 
            AND DATE(e.occurrence_date, '+3 months')
        THEN ckm.actual_value 
    END) as recovery_period_avg,
    -- Number of below-threshold measurements
    COUNT(CASE 
        WHEN ckm.measure_date >= e.occurrence_date 
            AND ckm.actual_value < kd.target_threshold 
        THEN 1 
    END) as below_threshold_count,
    -- Total measurements after event
    COUNT(CASE 
        WHEN ckm.measure_date >= e.occurrence_date 
        THEN 1 
    END) as total_measurements
FROM Event e
JOIN EventType et ON e.type_id = et.type_id
JOIN EventCategory ec ON et.category_id = ec.category_id
JOIN EventSeverity es ON e.severity_id = es.severity_id
JOIN EventImpactAssessment eia ON e.event_id = eia.event_id
JOIN ContractHeader ch ON eia.contract_id = ch.contract_id
JOIN ContractKPIMeasurement ckm ON ch.contract_id = ckm.contract_id
JOIN KPIDefinition kd ON ckm.kpi_id = kd.kpi_id
JOIN KPICategory kc ON kd.category_id = kc.category_id
WHERE ckm.measure_date BETWEEN 
    DATE(e.occurrence_date, '-3 months') 
    AND DATE(e.occurrence_date, '+3 months')
GROUP BY 
    e.event_id, e.event_title, et.type_name, ec.category_name,
    es.severity_name, e.occurrence_date, eia.contract_id,
    ch.contract_number, kd.kpi_id, kd.kpi_name, 
    kc.category_name, kd.target_threshold;
