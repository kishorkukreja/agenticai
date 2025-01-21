-- 1. Contract Event Impact Base View
CREATE VIEW vw_contract_event_impact AS
SELECT 
    ch.contract_id,
    ch.contract_number,
    c.vendor_name,
    ch.contract_type_id,
    ct.type_name as contract_type,
    ch.total_value as contract_value,
    ch.start_date,
    ch.end_date,
    -- Event impacts
    e.event_id,
    e.event_title,
    e.occurrence_date,
    et.type_name as event_type,
    es.severity_name,
    eia.impact_level,
    -- KPI impacts
    COUNT(DISTINCT ckm.kpi_id) as affected_kpis,
    AVG(CASE 
        WHEN ckm.measure_date >= e.occurrence_date 
        THEN ckm.achievement_percentage 
        END) - AVG(CASE 
        WHEN ckm.measure_date < e.occurrence_date 
        THEN ckm.achievement_percentage 
        END) as kpi_impact
FROM ContractHeader ch
JOIN Vendor c ON ch.vendor_id = c.vendor_id
JOIN ContractType ct ON ch.contract_type_id = ct.type_id
JOIN EventImpactAssessment eia ON ch.contract_id = eia.contract_id
JOIN Event e ON eia.event_id = e.event_id
JOIN EventType et ON e.type_id = et.type_id
JOIN EventSeverity es ON e.severity_id = es.severity_id
LEFT JOIN ContractKPIMeasurement ckm ON ch.contract_id = ckm.contract_id
    AND ckm.measure_date BETWEEN 
        DATE(e.occurrence_date, '-1 month') 
        AND DATE(e.occurrence_date, '+1 month')
GROUP BY 
    ch.contract_id, ch.contract_number, c.vendor_name,
    ch.contract_type_id, ct.type_name, ch.total_value,
    ch.start_date, ch.end_date,
    e.event_id, e.event_title, e.occurrence_date,
    et.type_name, es.severity_name, eia.impact_level;
