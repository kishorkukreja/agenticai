CREATE VIEW vw_recent_event_kpi_impact_detailed AS
WITH EventKPIs AS (
    SELECT 
        e.event_id,
        e.event_title,
        e.occurrence_date,
        e.severity_name,
        e.event_type,
        e.event_category,
        e.location,
        e.business_unit,
        eia.contract_id,
        ch.contract_number,
        c.vendor_name,
        ckm.kpi_id,
        kd.kpi_name,
        kd.category_id,
        kc.category_name as kpi_category,
        -- KPI performance changes using actual values
        AVG(CASE 
            WHEN ckm.measure_date < e.occurrence_date 
            THEN ckm.actual_value
        END) as pre_event_performance,
        AVG(CASE 
            WHEN ckm.measure_date >= e.occurrence_date 
            THEN ckm.actual_value
        END) as post_event_performance,
        -- Target values
        MAX(ckm.target_value) as target_value,
        -- Impact level from assessment
        eia.impact_level
    FROM vw_recent_event_details e
    JOIN EventImpactAssessment eia ON e.event_id = eia.event_id
    JOIN ContractHeader ch ON eia.contract_id = ch.contract_id
    JOIN Vendor c ON ch.vendor_id = c.vendor_id
    JOIN ContractKPIMeasurement ckm ON eia.contract_id = ckm.contract_id
    JOIN KPIDefinition kd ON ckm.kpi_id = kd.kpi_id
    JOIN KPICategory kc ON kd.category_id = kc.category_id
    WHERE ckm.measure_date BETWEEN 
        DATE(e.occurrence_date, '-3 months') 
        AND DATE(e.occurrence_date, '+3 months')
    GROUP BY 
        e.event_id, e.event_title, e.occurrence_date,
        e.severity_name, e.event_type, e.event_category,
        e.location, e.business_unit,
        eia.contract_id, ch.contract_number, c.vendor_name,
        ckm.kpi_id, kd.kpi_name, kd.category_id, kc.category_name,
        eia.impact_level
),
MetaKPIBaseline AS (
    SELECT
        ek.event_id,
        ek.contract_id,
        ek.contract_number,
        mkd.meta_kpi_id,
        mkd.meta_kpi_name,
        -- Calculate weighted baseline and final values
        SUM(ek.pre_event_performance * mkc.weight) as baseline_meta_kpi_value,
        SUM(ek.post_event_performance * mkc.weight) as final_meta_kpi_value,
        -- Store max target threshold for reference
        MAX(mkd.target_threshold) as meta_kpi_target
    FROM EventKPIs ek
    JOIN MetaKPIComponent mkc ON ek.kpi_id = mkc.kpi_id
    JOIN MetaKPIDefinition mkd ON mkc.meta_kpi_id = mkd.meta_kpi_id
    GROUP BY 
        ek.event_id, ek.contract_id, ek.contract_number,
        mkd.meta_kpi_id, mkd.meta_kpi_name
)
SELECT 
    ek.event_id,
    ek.event_title,
    ek.severity_name,
    ek.event_type,
    ek.event_category,
    ek.location,
    ek.business_unit,
    ek.occurrence_date,
    ek.contract_id,
    ek.contract_number,
    ek.vendor_name,
    ek.impact_level,
    mkd.meta_kpi_name,
    ek.kpi_category,
    ek.kpi_name as component_kpi,
    mkc.weight as kpi_weight,
    -- Component KPI metrics
    ROUND(ek.pre_event_performance, 2) as kpi_baseline,
    ROUND(ek.post_event_performance, 2) as kpi_final_value,
    ROUND(ek.target_value, 2) as kpi_target,
    ROUND((ek.post_event_performance - ek.pre_event_performance), 2) as kpi_absolute_change,
    ROUND(CASE 
        WHEN ek.pre_event_performance > 0 
        THEN ((ek.post_event_performance - ek.pre_event_performance) / ek.pre_event_performance * 100)
        ELSE NULL 
    END, 2) as kpi_percentage_change,
    -- Meta KPI metrics
    ROUND(mb.baseline_meta_kpi_value, 2) as meta_kpi_baseline,
    ROUND(mb.final_meta_kpi_value, 2) as meta_kpi_final_value,
    ROUND(mb.meta_kpi_target, 2) as meta_kpi_target,
    ROUND((mb.final_meta_kpi_value - mb.baseline_meta_kpi_value), 2) as meta_kpi_absolute_change,
    ROUND(CASE 
        WHEN mb.baseline_meta_kpi_value > 0 
        THEN ((mb.final_meta_kpi_value - mb.baseline_meta_kpi_value) / mb.baseline_meta_kpi_value * 100)
        ELSE NULL 
    END, 2) as meta_kpi_percentage_change,
    -- Performance vs Target indicators
    CASE 
        WHEN ek.post_event_performance >= ek.target_value THEN 'Above Target'
        WHEN ek.post_event_performance >= ek.target_value * 0.9 THEN 'Near Target'
        ELSE 'Below Target'
    END as kpi_performance_status,
    CASE 
        WHEN mb.final_meta_kpi_value >= mb.meta_kpi_target THEN 'Above Target'
        WHEN mb.final_meta_kpi_value >= mb.meta_kpi_target * 0.9 THEN 'Near Target'
        ELSE 'Below Target'
    END as meta_kpi_performance_status
FROM EventKPIs ek
JOIN MetaKPIComponent mkc ON ek.kpi_id = mkc.kpi_id
JOIN MetaKPIDefinition mkd ON mkc.meta_kpi_id = mkd.meta_kpi_id
JOIN MetaKPIBaseline mb ON 
    ek.event_id = mb.event_id 
    AND ek.contract_id = mb.contract_id
    AND mkd.meta_kpi_name = mb.meta_kpi_name;
