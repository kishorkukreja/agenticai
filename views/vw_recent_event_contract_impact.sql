CREATE VIEW vw_recent_event_contract_impact AS
SELECT 
    e.event_id,
    e.event_title,
    e.severity_name,
    eia.impact_level,
    ch.contract_id,
    ch.contract_number,
    c.vendor_name,
    -- Contract details
    ch.total_value as contract_value,
    ch.start_date as contract_start,
    ch.end_date as contract_end,
    -- Count of affected KPIs
    COUNT(DISTINCT ckm.kpi_id) as affected_kpis,
    -- Average KPI achievement before and after event
    AVG(CASE 
        WHEN ckm.measure_date < e.occurrence_date 
        THEN ckm.actual_value 
    END) as avg_kpi_before_event,
    AVG(CASE 
        WHEN ckm.measure_date >= e.occurrence_date 
        THEN ckm. actual_value
    END) as avg_kpi_after_event
FROM vw_recent_event_details e
JOIN EventImpactAssessment eia ON e.event_id = eia.event_id
JOIN ContractHeader ch ON eia.contract_id = ch.contract_id
JOIN Vendor c ON ch.vendor_id = c.vendor_id
LEFT JOIN ContractKPIMeasurement ckm ON ch.contract_id = ckm.contract_id
    AND ckm.measure_date BETWEEN 
        DATE(e.occurrence_date, '-3 months') 
        AND DATE(e.occurrence_date, '+3 months')    
GROUP BY 
    e.event_id, e.event_title, e.severity_name, 
    eia.impact_level, ch.contract_id, ch.contract_number,
    c.vendor_name, ch.total_value, ch.start_date, ch.end_date;
