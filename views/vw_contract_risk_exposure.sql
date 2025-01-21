-- 2. Contract Risk Exposure View
CREATE VIEW vw_contract_risk_exposure AS
SELECT 
    contract_id,
    contract_number,
    vendor_name,
    contract_type,
    contract_value,
    -- Event frequency
    COUNT(DISTINCT event_id) as total_events,
    COUNT(DISTINCT CASE WHEN impact_level IN ('critical', 'high') 
        THEN event_id END) as high_impact_events,
    -- Recent events (last 90 days)
    COUNT(DISTINCT CASE 
        WHEN occurrence_date >= DATE('now', '-90 days') 
        THEN event_id END) as recent_events,
    -- Event severity distribution
    COUNT(DISTINCT CASE WHEN severity_name = 'Critical' 
        THEN event_id END) as critical_events,
    COUNT(DISTINCT CASE WHEN severity_name = 'High' 
        THEN event_id END) as high_severity_events,
    -- Impact metrics
    AVG(CASE WHEN impact_level = 'critical' THEN kpi_impact END) 
        as avg_critical_impact,
    ROUND(AVG(kpi_impact), 2) as avg_kpi_impact,
    -- Value at risk calculation
    ROUND(contract_value * (
        CASE 
            WHEN COUNT(DISTINCT CASE WHEN impact_level = 'critical' 
                THEN event_id END) > 0 THEN 0.1
            WHEN COUNT(DISTINCT CASE WHEN impact_level = 'high' 
                THEN event_id END) > 0 THEN 0.05
            WHEN COUNT(DISTINCT CASE WHEN impact_level = 'medium' 
                THEN event_id END) > 0 THEN 0.02
            ELSE 0.01
        END
    ), 2) as estimated_value_at_risk
FROM vw_contract_event_impact
GROUP BY 
    contract_id, contract_number, vendor_name,
    contract_type, contract_value;
