-- 1. Direct Cost Impact Base View
CREATE VIEW vw_direct_cost_impact AS
SELECT 
    e.event_id,
    e.event_title,
    e.occurrence_date,
    et.type_name as event_type,
    es.severity_name,
    ec.category_name as event_category,
    eia.contract_id,
    ch.contract_number,
    ch.total_value as contract_value,
    eia.impact_level,
    -- Direct financial calculations
    CASE impact_level
        WHEN 'critical' THEN ch.total_value * 0.10  -- 10% impact for critical
        WHEN 'high' THEN ch.total_value * 0.05      -- 5% impact for high
        WHEN 'medium' THEN ch.total_value * 0.02    -- 2% impact for medium
        WHEN 'low' THEN ch.total_value * 0.01       -- 1% impact for low
        ELSE 0
    END as direct_financial_impact,
    -- KPI impact costs
    COUNT(DISTINCT ckm.kpi_id) as affected_kpis,
    AVG(CASE 
        WHEN ckm.measure_date >= e.occurrence_date 
        THEN ckm.achievement_percentage 
    END) - AVG(CASE 
        WHEN ckm.measure_date < e.occurrence_date 
        THEN ckm.achievement_percentage 
    END) as kpi_performance_change,
    -- Contract line items affected
    COUNT(DISTINCT cl.line_id) as affected_line_items,
    SUM(cl.line_value) as affected_line_value
FROM Event e
JOIN EventType et ON e.type_id = et.type_id
JOIN EventCategory ec ON et.category_id = ec.category_id
JOIN EventSeverity es ON e.severity_id = es.severity_id
JOIN EventImpactAssessment eia ON e.event_id = eia.event_id
JOIN ContractHeader ch ON eia.contract_id = ch.contract_id
LEFT JOIN ContractKPIMeasurement ckm ON ch.contract_id = ckm.contract_id
    AND ckm.measure_date BETWEEN 
        DATE(e.occurrence_date, '-1 month') 
        AND DATE(e.occurrence_date, '+3 months')
LEFT JOIN ContractLine cl ON ch.contract_id = cl.contract_id
GROUP BY 
    e.event_id, e.event_title, e.occurrence_date,
    et.type_name, es.severity_name, ec.category_name,
    eia.contract_id, ch.contract_number, ch.total_value,
    eia.impact_level;

