-- 1. Customer Event Impact Base View
CREATE VIEW vw_vendor_event_impact AS
SELECT 
    c.vendor_id,
    c.vendor_name,
    ch.contract_id,
    ch.contract_number,
    ch.total_value as contract_value,
    e.event_id,
    e.event_title,
    e.occurrence_date,
    et.type_name as event_type,
    es.severity_name,
    eia.impact_level,
    -- KPI impacts
    COUNT(DISTINCT ckm.kpi_id) as affected_kpis,
    COUNT(DISTINCT CASE 
        WHEN ckm.achievement_percentage < 
            (SELECT target_threshold FROM KPIDefinition kd WHERE kd.kpi_id = ckm.kpi_id)
        THEN ckm.kpi_id 
    END) as kpis_below_threshold,
    -- Average KPI achievement change
    AVG(CASE 
        WHEN ckm.measure_date >= e.occurrence_date 
        THEN ckm.achievement_percentage 
    END) - AVG(CASE 
        WHEN ckm.measure_date < e.occurrence_date 
        THEN ckm.achievement_percentage 
    END) as avg_kpi_impact
FROM Vendor c
JOIN ContractHeader ch ON c.vendor_id = ch.vendor_id
JOIN EventImpactAssessment eia ON ch.contract_id = eia.contract_id
JOIN Event e ON eia.event_id = e.event_id
JOIN EventType et ON e.type_id = et.type_id
JOIN EventSeverity es ON e.severity_id = es.severity_id
LEFT JOIN ContractKPIMeasurement ckm ON ch.contract_id = ckm.contract_id
    AND ckm.measure_date BETWEEN 
        DATE(e.occurrence_date, '-1 month') 
        AND DATE(e.occurrence_date, '+1 month')
GROUP BY 
    c.vendor_id,
    c.vendor_name, ch.contract_id,
    ch.contract_number, ch.total_value, e.event_id,
    e.event_title, e.occurrence_date, et.type_name,
    es.severity_name, eia.impact_level;
