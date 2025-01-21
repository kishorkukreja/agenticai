-- 2. KPI Degradation Cost View
CREATE VIEW vw_kpi_degradation_cost AS
SELECT 
    e.event_id,
    kd.kpi_id,
    kd.kpi_name,
    kc.category_name as kpi_category,
    eia.contract_id,
    ch.contract_number,
    -- Pre-event baseline
    AVG(CASE 
        WHEN ckm.measure_date < e.occurrence_date 
        THEN ckm.actual_value 
    END) as baseline_value,
    -- Post-event performance
    AVG(CASE 
        WHEN ckm.measure_date >= e.occurrence_date 
        THEN ckm.actual_value 
    END) as impact_value,
    -- Performance degradation
    kd.target_threshold,
    -- Calculate degradation cost based on KPI weight and contract value
    CASE 
        WHEN AVG(CASE 
            WHEN ckm.measure_date >= e.occurrence_date 
            THEN ckm.actual_value 
        END) < kd.target_threshold
        THEN (ch.total_value * kd.weight * 0.01 * 
            (1 - AVG(CASE 
                WHEN ckm.measure_date >= e.occurrence_date 
                THEN ckm.actual_value 
            END) / kd.target_threshold))
        ELSE 0
    END as degradation_cost
FROM Event e
JOIN EventImpactAssessment eia ON e.event_id = eia.event_id
JOIN ContractHeader ch ON eia.contract_id = ch.contract_id
JOIN ContractKPIMeasurement ckm ON ch.contract_id = ckm.contract_id
JOIN KPIDefinition kd ON ckm.kpi_id = kd.kpi_id
JOIN KPICategory kc ON kd.category_id = kc.category_id
WHERE ckm.measure_date BETWEEN 
    DATE(e.occurrence_date, '-1 month') 
    AND DATE(e.occurrence_date, '+3 months')
GROUP BY 
    e.event_id, kd.kpi_id, kd.kpi_name, kc.category_name,
    eia.contract_id, ch.contract_number, kd.target_threshold;
