-- 3. Long-term Financial Impact View
CREATE VIEW vw_longterm_financial_impact AS
SELECT 
    dci.event_id,
    dci.event_title,
    dci.event_type,
    dci.severity_name,
    dci.occurrence_date,
    -- Direct costs
    SUM(dci.direct_financial_impact) as total_direct_impact,
    -- KPI degradation costs
    SUM(kdc.degradation_cost) as total_degradation_cost,
    -- Contract impact
    COUNT(DISTINCT dci.contract_id) as affected_contracts,
    SUM(dci.contract_value) as total_contract_value,
    -- Calculated impacts
    ROUND(SUM(dci.direct_financial_impact) + 
          SUM(kdc.degradation_cost), 2) as total_financial_impact,
    -- Impact ratios
    ROUND(SUM(dci.direct_financial_impact) / 
          SUM(dci.contract_value) * 100, 2) as direct_impact_percentage,
    ROUND(SUM(kdc.degradation_cost) / 
          SUM(dci.contract_value) * 100, 2) as degradation_impact_percentage,
    -- Projected annual impact
    ROUND((SUM(dci.direct_financial_impact) + 
           SUM(kdc.degradation_cost)) * 12, 2) as projected_annual_impact
FROM vw_direct_cost_impact dci
LEFT JOIN vw_kpi_degradation_cost kdc 
    ON dci.event_id = kdc.event_id
    AND dci.contract_id = kdc.contract_id
GROUP BY 
    dci.event_id, dci.event_title, dci.event_type,
    dci.severity_name, dci.occurrence_date;
