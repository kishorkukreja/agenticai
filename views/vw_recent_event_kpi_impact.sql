CREATE VIEW vw_recent_event_kpi_impact AS
WITH EventKPIs AS (
    SELECT 
        e.event_id,
        e.event_title,
        e.occurrence_date,
        eia.contract_id,
        ch.contract_number,
        ckm.kpi_id,
        kd.kpi_name,
        -- KPI performance changes
        AVG(CASE 
            WHEN ckm.measure_date < e.occurrence_date 
            THEN ckm.actual_value--.achievement_percentage 
        END) as pre_event_performance,
        AVG(CASE 
            WHEN ckm.measure_date >= e.occurrence_date 
            THEN ckm.actual_value--ckm.achievement_percentage 
        END) as post_event_performance
    FROM vw_recent_event_details e
    JOIN EventImpactAssessment eia ON e.event_id = eia.event_id
    JOIN ContractHeader ch ON eia.contract_id = ch.contract_id
    JOIN ContractKPIMeasurement ckm ON eia.contract_id = ckm.contract_id
    JOIN KPIDefinition kd ON ckm.kpi_id = kd.kpi_id
    WHERE ckm.measure_date BETWEEN 
        DATE(e.occurrence_date, '-3 months') 
        AND DATE(e.occurrence_date, '+3 months')
    GROUP BY 
        e.event_id, e.event_title, e.occurrence_date,
        eia.contract_id, ch.contract_number,
        ckm.kpi_id, kd.kpi_name
),
MetaKPIBaseline AS (
    SELECT
        ek.event_id,
        ek.contract_id,
        ek.contract_number,
        mkd.meta_kpi_id,
        mkd.meta_kpi_name,
        -- Calculate baseline Meta KPI value (pre-event)
        SUM(ek.pre_event_performance * mkc.weight) as baseline_meta_kpi_value,
        -- Calculate final Meta KPI value (post-event)
        SUM(ek.post_event_performance * mkc.weight) as final_meta_kpi_value
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
    ek.contract_id,
    ek.contract_number,
    mkd.meta_kpi_name,
    ek.kpi_name as component_kpi,
    mkc.weight as kpi_weight,
    -- Component KPI metrics
    ek.pre_event_performance as kpi_baseline,
    ek.post_event_performance as kpi_final_value,
    (ek.post_event_performance - ek.pre_event_performance) as kpi_absolute_change,
    CASE 
        WHEN ek.pre_event_performance > 0 
        THEN ((ek.post_event_performance - ek.pre_event_performance) / ek.pre_event_performance * 100)
        ELSE NULL 
    END as kpi_percentage_change,
    -- Meta KPI metrics
    mb.baseline_meta_kpi_value as meta_kpi_baseline,
    mb.final_meta_kpi_value as meta_kpi_final_value,
    (mb.final_meta_kpi_value - mb.baseline_meta_kpi_value) as meta_kpi_absolute_change,
    CASE 
        WHEN mb.baseline_meta_kpi_value > 0 
        THEN ((mb.final_meta_kpi_value - mb.baseline_meta_kpi_value) / mb.baseline_meta_kpi_value * 100)
        ELSE NULL 
    END as meta_kpi_percentage_change
FROM EventKPIs ek
JOIN MetaKPIComponent mkc ON ek.kpi_id = mkc.kpi_id
JOIN MetaKPIDefinition mkd ON mkc.meta_kpi_id = mkd.meta_kpi_id
JOIN MetaKPIBaseline mb ON 
    ek.event_id = mb.event_id 
    AND ek.contract_id = mb.contract_id
    AND mkd.meta_kpi_name = mb.meta_kpi_name
where 1=1
--ek.event_id=196
order by    ek.contract_number,mkd.meta_kpi_name,
    ek.kpi_name;