-- 4. Comprehensive Event Impact Summary
CREATE VIEW vw_recent_event_impact_summary AS
SELECT 
    ed.event_id,
    ed.event_title,
    ed.event_type,
    ed.event_category,
    ed.severity_name,
    ed.location,
    ed.business_unit,
    ed.occurrence_date,
    ed.detection_date,
    ed.resolution_date,
    -- Impact metrics
    COUNT(DISTINCT eci.contract_id) as affected_contracts,
    SUM(CASE WHEN eci.impact_level IN ('high', 'critical') 
        THEN 1 ELSE 0 END) as high_impact_contracts,
    COUNT(DISTINCT eki.meta_kpi_name) as affected_meta_kpis,
    -- Average impacts
    AVG(eci.avg_kpi_after_event - eci.avg_kpi_before_event) 
        as avg_kpi_impact,
    AVG(eki.meta_kpi_final_value) as avg_meta_kpi_impact,
    -- Financial impact proxy
    SUM(CASE WHEN eci.impact_level = 'critical' THEN eci.contract_value * 0.1
         WHEN eci.impact_level = 'high' THEN eci.contract_value * 0.05
         WHEN eci.impact_level = 'medium' THEN eci.contract_value * 0.02
         ELSE eci.contract_value * 0.01 END) as estimated_financial_impact
FROM vw_recent_event_details ed
LEFT JOIN vw_recent_event_contract_impact eci ON ed.event_id = eci.event_id
LEFT JOIN vw_recent_event_kpi_impact eki ON ed.event_id = eki.event_id
GROUP BY 
    ed.event_id, ed.event_title, ed.event_type, 
    ed.event_category, ed.severity_name, ed.location,
    ed.business_unit, ed.occurrence_date, ed.detection_date, ed.resolution_date;
