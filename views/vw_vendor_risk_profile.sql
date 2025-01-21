-- 2. Customer Risk Profile View
CREATE VIEW vw_vendor_risk_profile AS
SELECT 
    vendor_id,
    vendor_name,
    COUNT(DISTINCT contract_id) as total_contracts,
    SUM(contract_value) as total_contract_value,
    -- Event impacts
    COUNT(DISTINCT event_id) as total_events,
    COUNT(DISTINCT CASE 
        WHEN impact_level IN ('critical', 'high') 
        THEN event_id 
    END) as high_impact_events,
    -- Recent impacts (last 90 days)
    COUNT(DISTINCT CASE 
        WHEN occurrence_date >= DATE('now', '-90 days') 
        THEN event_id 
    END) as recent_events,
    -- KPI impacts
    AVG(affected_kpis) as avg_kpis_affected,
    AVG(kpis_below_threshold) as avg_kpis_below_threshold,
    ROUND(AVG(avg_kpi_impact), 2) as avg_kpi_impact,
    -- Risk calculation
    ROUND(SUM(CASE 
        WHEN impact_level = 'critical' THEN contract_value * 0.1
        WHEN impact_level = 'high' THEN contract_value * 0.05
        WHEN impact_level = 'medium' THEN contract_value * 0.02
        ELSE contract_value * 0.01
    END), 2) as total_value_at_risk
FROM vw_vendor_event_impact
GROUP BY vendor_id, vendor_name;	

