-- a. List All Recent Events with Impact Details
SELECT 
    event_title,
    event_type,
    severity_name,
    location,
    business_unit,
    occurrence_date,
    detection_date,
    resolution_date,
    affected_contracts,
    high_impact_contracts,
    affected_meta_kpis,
    ROUND(avg_kpi_impact, 2) as avg_kpi_impact,
    ROUND(estimated_financial_impact, 2) as estimated_impact
FROM vw_recent_event_impact_summary
ORDER BY occurrence_date DESC;


-- b. Critical Event Impact Assessment
SELECT 
    event_title,
    severity_name,
    event_type,
    business_unit,
    location,
    COUNT(DISTINCT contract_id) as affected_contracts,
    COUNT(DISTINCT CASE WHEN impact_level IN ('high', 'critical') THEN contract_id END) as high_impact_contracts,
    COUNT(DISTINCT meta_kpi_name) as affected_meta_kpis,
    ROUND(AVG(kpi_percentage_change), 2) as avg_kpi_impact_pct,
    ROUND(AVG(meta_kpi_percentage_change), 2) as avg_meta_kpi_impact_pct,
    COUNT(CASE WHEN kpi_performance_status = 'Below Target' THEN 1 END) as kpis_below_target,
    COUNT(CASE WHEN meta_kpi_performance_status = 'Below Target' THEN 1 END) as meta_kpis_below_target
FROM vw_recent_event_kpi_impact_detailed
GROUP BY 
    event_title, severity_name, event_type, business_unit, location
ORDER BY high_impact_contracts DESC;


-- c. Geographic Impact Distribution of Recent Events
SELECT 
    location,
    COUNT(*) as event_count,
    SUM(affected_contracts) as total_affected_contracts,
    SUM(high_impact_contracts) as total_high_impact_contracts,
    ROUND(AVG(estimated_financial_impact), 2) as avg_financial_impact
FROM vw_recent_event_impact_summary
GROUP BY location
ORDER BY avg_financial_impact DESC;

-- d. Business Unit Impact Analysis of Recent Events
SELECT 
    business_unit,
    COUNT(*) as event_count,
    SUM(affected_contracts) as total_affected_contracts,
    ROUND(AVG(avg_kpi_impact), 2) as avg_kpi_impact,
    ROUND(AVG(avg_meta_kpi_impact), 2) as avg_meta_kpi_impact,
    ROUND(SUM(estimated_financial_impact), 2) as total_financial_impact
FROM vw_recent_event_impact_summary
GROUP BY business_unit
ORDER BY total_financial_impact DESC;


-- e. Recent Events' Impact on Meta KPIs
SELECT 
    eki.meta_kpi_name,
    COUNT(DISTINCT eki.event_id) as affecting_events,
    ROUND(AVG(eki.kpi_percentage_change), 2) as avg_performance_impact,
    ROUND(AVG(eki.meta_kpi_percentage_change), 2) as avg_weighted_impact
FROM vw_recent_event_kpi_impact eki
GROUP BY eki.meta_kpi_name
ORDER BY avg_weighted_impact;

-- f. Contract Risk Exposure Analysis
SELECT 
    contract_number,
    vendor_name,
    COUNT(DISTINCT meta_kpi_name) as affected_meta_kpis,
    ROUND(AVG(CASE WHEN kpi_performance_status = 'Below Target' THEN kpi_percentage_change END), 2) as avg_underperforming_kpi_impact,
    COUNT(CASE WHEN meta_kpi_performance_status = 'Below Target' THEN 1 END) as meta_kpis_at_risk,
    GROUP_CONCAT(DISTINCT CASE WHEN meta_kpi_performance_status = 'Below Target' 
        THEN meta_kpi_name END) as at_risk_meta_kpis
FROM vw_recent_event_kpi_impact_detailed
GROUP BY contract_number, vendor_name
HAVING COUNT(CASE WHEN meta_kpi_performance_status = 'Below Target' THEN 1 END) > 0
ORDER BY meta_kpis_at_risk DESC;

-- g. Meta KPI Impact Severity Analysis
SELECT 
    meta_kpi_name,
    COUNT(DISTINCT event_id) as affecting_events,
    COUNT(DISTINCT contract_id) as affected_contracts,
    ROUND(AVG(meta_kpi_percentage_change), 2) as avg_impact_percentage,
    COUNT(CASE WHEN meta_kpi_performance_status = 'Below Target' THEN 1 END) as instances_below_target,
    ROUND(AVG(CASE WHEN impact_level = 'critical' 
        THEN meta_kpi_percentage_change END), 2) as critical_event_impact,
    GROUP_CONCAT(DISTINCT CASE WHEN meta_kpi_performance_status = 'Below Target' 
        THEN event_title END) as contributing_events
FROM  vw_recent_event_kpi_impact_detailed
GROUP BY meta_kpi_name
ORDER BY avg_impact_percentage;


-- h. Component KPI Contribution Analysis
SELECT 
    meta_kpi_name,
    component_kpi,
    kpi_category,
    kpi_weight,
    COUNT(DISTINCT event_id) as affecting_events,
    ROUND(AVG(kpi_percentage_change), 2) as avg_component_impact,
    ROUND(AVG(meta_kpi_percentage_change), 2) as avg_meta_kpi_impact,
    ROUND(AVG(kpi_percentage_change * kpi_weight), 2) as weighted_contribution,
    COUNT(CASE WHEN kpi_performance_status = 'Below Target' THEN 1 END) as times_below_target
FROM vw_recent_event_kpi_impact_detailed
GROUP BY meta_kpi_name, component_kpi, kpi_category, kpi_weight
ORDER BY meta_kpi_name, weighted_contribution DESC;

-- i. Geographic Impact Pattern Analysis
SELECT 
    location,
    event_category,
    COUNT(DISTINCT event_id) as event_count,
    COUNT(DISTINCT contract_id) as affected_contracts,
    ROUND(AVG(meta_kpi_percentage_change), 2) as avg_meta_kpi_impact,
    GROUP_CONCAT(DISTINCT CASE WHEN meta_kpi_performance_status = 'Below Target' 
        THEN meta_kpi_name END) as affected_meta_kpis,
    COUNT(DISTINCT CASE WHEN impact_level IN ('high', 'critical') 
        THEN contract_id END) as high_impact_contracts
FROM vw_recent_event_kpi_impact_detailed
GROUP BY location, event_category
ORDER BY event_count DESC;


-- j. Business Unit Risk Profile
SELECT 
    business_unit,
    COUNT(DISTINCT event_id) as total_events,
    COUNT(DISTINCT CASE WHEN severity_name IN ('Critical', 'High') 
        THEN event_id END) as high_severity_events,
    COUNT(DISTINCT contract_id) as affected_contracts,
    ROUND(AVG(CASE WHEN meta_kpi_performance_status = 'Below Target' 
        THEN meta_kpi_percentage_change END), 2) as avg_negative_impact,
    GROUP_CONCAT(DISTINCT CASE WHEN impact_level = 'critical' 
        THEN meta_kpi_name END) as critical_impact_areas
FROM vw_recent_event_kpi_impact_detailed
GROUP BY business_unit
ORDER BY high_severity_events DESC;


-- k. Recent SLA Breaches with Impact
SELECT 
    event_id,
    event_title,
    severity_name,
    event_type,
    occurrence_date,
    detection_time_hours,
    resolution_time_hours,
    response_sla_hours,
    highest_impact_level,
    affected_contracts_count,
    ROUND(detection_time_hours - response_sla_hours, 2) as hours_over_sla
FROM vw_event_response_metrics
WHERE sla_status = 'SLA Breached'
    AND occurrence_date >= DATE('now', '-30 days')
ORDER BY detection_time_hours - response_sla_hours DESC;

-- l. Response Performance Trends
WITH weekly_metrics AS (
    SELECT 
        DATE(occurrence_date, 'weekstart') as week_start,
        COUNT(*) as total_events,
        ROUND(AVG(detection_time_hours), 2) as avg_detection_time,
        COUNT(CASE WHEN sla_status = 'SLA Breached' THEN 1 END) as sla_breaches,
        ROUND(AVG(CASE WHEN resolution_date IS NOT NULL 
            THEN resolution_time_hours END), 2) as avg_resolution_time
    FROM vw_event_response_metrics
    WHERE occurrence_date >= DATE('now', '-90 days')
    GROUP BY DATE(occurrence_date, 'weekstart')
)
SELECT 
    week_start,
    total_events,
    avg_detection_time,
    sla_breaches,
    avg_resolution_time,
    ROUND(CAST(sla_breaches AS FLOAT) / total_events * 100, 2) as sla_breach_rate
FROM weekly_metrics
ORDER BY week_start;

-- m. Critical Response Time Analysis
SELECT 
    severity_name,
    event_type,
    COUNT(*) as event_count,
    ROUND(AVG(detection_time_hours), 2) as avg_detection_hours,
    ROUND(AVG(resolution_time_hours), 2) as avg_resolution_hours,
    ROUND(AVG(CASE 
        WHEN resolution_time_hours > response_sla_hours 
        THEN resolution_time_hours - response_sla_hours 
    END), 2) as avg_hours_over_sla,
    COUNT(CASE 
        WHEN highest_impact_level IN ('critical', 'high') 
        AND sla_status = 'SLA Breached' 
        THEN 1 END) as critical_sla_breaches
FROM vw_event_response_metrics
WHERE severity_name IN ('Critical', 'High')
GROUP BY severity_name, event_type
ORDER BY avg_hours_over_sla DESC;

-- n. Impact of Response Time on Resolution
SELECT 
    CASE 
        WHEN detection_time_hours <= response_sla_hours/2 THEN 'Early Detection'
        WHEN detection_time_hours <= response_sla_hours THEN 'Within SLA'
        ELSE 'Late Detection'
    END as detection_category,
    COUNT(*) as event_count,
    ROUND(AVG(resolution_time_hours), 2) as avg_resolution_hours,
    ROUND(AVG(total_incident_hours), 2) as avg_total_duration,
    COUNT(CASE WHEN highest_impact_level IN ('critical', 'high') THEN 1 END) as high_impact_events,
    ROUND(AVG(affected_contracts_count), 2) as avg_affected_contracts
FROM vw_event_response_metrics
WHERE resolution_date IS NOT NULL
GROUP BY 
    CASE 
        WHEN detection_time_hours <= response_sla_hours/2 THEN 'Early Detection'
        WHEN detection_time_hours <= response_sla_hours THEN 'Within SLA'
        ELSE 'Late Detection'
    END
ORDER BY avg_resolution_hours;

-- o. Most Impacted Contracts
SELECT 
    contract_number,
    vendor_name,
    contract_type,
    ROUND(contract_value, 2) as contract_value,
    total_events,
    high_impact_events,
    recent_events,
    ROUND(avg_kpi_impact, 2) as avg_kpi_impact,
    ROUND(estimated_value_at_risk, 2) as value_at_risk,
    ROUND(estimated_value_at_risk / contract_value * 100, 2) 
        as risk_percentage
FROM vw_contract_risk_exposure
WHERE total_events > 0
ORDER BY high_impact_events DESC, value_at_risk DESC
LIMIT 20;

-- p. Contract Size vs Impact Analysis
WITH contract_size_categories AS (
    SELECT 
        contract_id,
        total_value,
        NTILE(4) OVER (ORDER BY total_value) as size_quartile
    FROM ContractHeader
)
SELECT 
    CASE size_quartile
        WHEN 1 THEN 'Small'
        WHEN 2 THEN 'Medium'
        WHEN 3 THEN 'Large'
        WHEN 4 THEN 'Enterprise'
    END as contract_size,
    COUNT(DISTINCT cre.contract_id) as total_contracts,
    ROUND(AVG(cre.contract_value), 2) as avg_contract_value,
    ROUND(AVG(cre.total_events), 2) as avg_events_per_contract,
    ROUND(AVG(cre.high_impact_events), 2) as avg_high_impact_events,
    ROUND(AVG(cre.avg_kpi_impact), 2) as avg_kpi_impact,
    ROUND(AVG(cre.estimated_value_at_risk), 2) as avg_value_at_risk,
    ROUND(AVG(cre.estimated_value_at_risk / cre.contract_value * 100), 2) 
        as avg_risk_percentage
FROM contract_size_categories csc
JOIN vw_contract_risk_exposure cre ON csc.contract_id = cre.contract_id
GROUP BY size_quartile
ORDER BY size_quartile;

-- q. Customer Impact Clustering
WITH customer_impact_metrics AS (
    SELECT 
        vendor_name,
        COUNT(DISTINCT contract_id) as total_contracts,
        SUM(contract_value) as total_contract_value,
        SUM(total_events) as total_events,
        SUM(high_impact_events) as total_high_impact_events,
        AVG(avg_kpi_impact) as avg_kpi_impact,
        SUM(estimated_value_at_risk) as total_value_at_risk
    FROM vw_contract_risk_exposure
    GROUP BY vendor_name
)
SELECT 
    vendor_name,
    total_contracts,
    ROUND(total_contract_value, 2) as total_contract_value,
    total_events,
    total_high_impact_events,
    ROUND(avg_kpi_impact, 2) as avg_kpi_impact,
    ROUND(total_value_at_risk, 2) as total_value_at_risk,
    CASE 
        WHEN total_high_impact_events > 2 AND avg_kpi_impact < -10 
            THEN 'High Risk'
        WHEN total_high_impact_events > 0 OR avg_kpi_impact < -5 
            THEN 'Medium Risk'
        ELSE 'Low Risk'
    END as risk_category
FROM customer_impact_metrics
ORDER BY total_value_at_risk DESC;

-- r. Contract Type Risk Analysis
SELECT 
    contract_type,
    COUNT(DISTINCT contract_id) as total_contracts,
    ROUND(AVG(contract_value), 2) as avg_contract_value,
    SUM(total_events) as total_events,
    SUM(high_impact_events) as high_impact_events,
    ROUND(AVG(avg_kpi_impact), 2) as avg_kpi_impact,
    ROUND(SUM(estimated_value_at_risk), 2) as total_value_at_risk,
    ROUND(AVG(estimated_value_at_risk / contract_value * 100), 2) 
        as avg_risk_percentage
FROM vw_contract_risk_exposure
GROUP BY contract_type
ORDER BY total_value_at_risk DESC;

-- s. Time-based Contract Risk Trends
WITH monthly_risk_metrics AS (
    SELECT 
        strftime('%Y-%m', cei.occurrence_date) as month,
        COUNT(DISTINCT cei.contract_id) as affected_contracts,
        COUNT(DISTINCT CASE WHEN cei.impact_level IN ('critical', 'high') 
            THEN cei.contract_id END) as high_impact_contracts,
        AVG(cei.kpi_impact) as avg_kpi_impact,
        SUM(CASE 
            WHEN cei.impact_level = 'critical' THEN ch.total_value * 0.1
            WHEN cei.impact_level = 'high' THEN ch.total_value * 0.05
            WHEN cei.impact_level = 'medium' THEN ch.total_value * 0.02
            ELSE ch.total_value * 0.01
        END) as monthly_value_at_risk
    FROM vw_contract_event_impact cei
    JOIN ContractHeader ch ON cei.contract_id = ch.contract_id
    WHERE cei.occurrence_date >= DATE('now', '-12 months')
    GROUP BY strftime('%Y-%m', cei.occurrence_date)
)
SELECT 
    month,
    affected_contracts,
    high_impact_contracts,
    ROUND(avg_kpi_impact, 2) as avg_kpi_impact,
    ROUND(monthly_value_at_risk, 2) as monthly_value_at_risk,
    ROUND(monthly_value_at_risk / affected_contracts, 2) 
        as avg_risk_per_contract
FROM monthly_risk_metrics
ORDER BY month DESC;


-- t. Most and Least Resilient KPIs
SELECT 
    kpi_name,
    kpi_category,
    total_events_affecting,
    avg_immediate_impact,
    avg_recovery_impact,
    avg_recovery_rate,
    threshold_breach_rate,
    resilience_score,
    CASE 
        WHEN resilience_score >= 80 THEN 'High Resilience'
        WHEN resilience_score >= 50 THEN 'Moderate Resilience'
        ELSE 'Low Resilience'
    END as resilience_category
FROM vw_kpi_resilience_metrics
ORDER BY resilience_score DESC;

-- u. Recovery Pattern Analysis
SELECT 
    kpi_name,
    event_type,
    COUNT(*) as event_count,
    ROUND(AVG(CASE 
        WHEN immediate_impact_avg < pre_event_avg 
        THEN ABS((immediate_impact_avg - pre_event_avg) / pre_event_avg * 100)
        ELSE 0 
    END), 2) as avg_impact_percentage,
    ROUND(AVG(CASE 
        WHEN recovery_period_avg > immediate_impact_avg 
        THEN (recovery_period_avg - immediate_impact_avg) / 
            ABS(immediate_impact_avg - pre_event_avg) * 100
        ELSE 0 
    END), 2) as avg_recovery_percentage,
    ROUND(AVG(CASE 
        WHEN recovery_period_avg >= pre_event_avg THEN 1
        ELSE 0 
    END) * 100, 2) as full_recovery_rate
FROM vw_kpi_event_impact
WHERE immediate_impact_avg < pre_event_avg
GROUP BY kpi_name, event_type
HAVING event_count > 1
ORDER BY avg_recovery_percentage DESC;

-- v. Threshold Breach Analysis
SELECT 
    kpi_name,
    kpi_category,
    COUNT(DISTINCT event_id) as total_events,
    ROUND(AVG(CASE 
        WHEN immediate_impact_avg < target_threshold THEN 1
        ELSE 0 
    END) * 100, 2) as immediate_breach_rate,
    ROUND(AVG(CASE 
        WHEN recovery_period_avg < target_threshold THEN 1
        ELSE 0 
    END) * 100, 2) as sustained_breach_rate,
    ROUND(AVG(CAST(below_threshold_count AS FLOAT) / 
        NULLIF(total_measurements, 0) * 100), 2) as overall_breach_rate
FROM vw_kpi_event_impact
GROUP BY kpi_name, kpi_category
HAVING total_events > 1
ORDER BY overall_breach_rate DESC;

-- w. Event Type Impact Correlation
SELECT 
    event_type,
    event_category,
    kpi_category,
    COUNT(DISTINCT event_id) as event_count,
    COUNT(DISTINCT kpi_id) as affected_kpis,
    ROUND(AVG(CASE 
        WHEN immediate_impact_avg < pre_event_avg 
        THEN ABS((immediate_impact_avg - pre_event_avg) / pre_event_avg * 100)
        ELSE 0 
    END), 2) as avg_impact_severity,
    ROUND(AVG(CASE 
        WHEN immediate_impact_avg < target_threshold THEN 1
        ELSE 0 
    END) * 100, 2) as threshold_breach_rate,
    ROUND(AVG(CASE 
        WHEN recovery_period_avg >= pre_event_avg THEN 1
        ELSE 0 
    END) * 100, 2) as recovery_success_rate
FROM vw_kpi_event_impact
GROUP BY event_type, event_category, kpi_category
HAVING event_count > 1
ORDER BY avg_impact_severity DESC;

-- x. Recovery Time Pattern Analysis
WITH recovery_intervals AS (
    SELECT 
        kpi_name,
        event_id,
        event_type,
        severity_name,
        CASE 
            WHEN recovery_period_avg >= pre_event_avg THEN 'Full Recovery'
            WHEN recovery_period_avg > immediate_impact_avg THEN 'Partial Recovery'
            ELSE 'No Recovery'
        END as recovery_status,
        CASE 
            WHEN recovery_period_avg >= pre_event_avg THEN 
                ROUND((recovery_period_avg - immediate_impact_avg) / 
                    ABS(immediate_impact_avg - pre_event_avg) * 100, 2)
            ELSE 0
        END as recovery_percentage
    FROM vw_kpi_event_impact
    WHERE immediate_impact_avg < pre_event_avg
)
SELECT 
    kpi_name,
    COUNT(*) as total_impacts,
    ROUND(AVG(CASE WHEN recovery_status = 'Full Recovery' 
        THEN 1 ELSE 0 END) * 100, 2) as full_recovery_rate,
    ROUND(AVG(CASE WHEN recovery_status = 'Partial Recovery' 
        THEN 1 ELSE 0 END) * 100, 2) as partial_recovery_rate,
    ROUND(AVG(CASE WHEN recovery_status = 'No Recovery' 
        THEN 1 ELSE 0 END) * 100, 2) as no_recovery_rate,
    ROUND(AVG(recovery_percentage), 2) as avg_recovery_percentage
FROM recovery_intervals
GROUP BY kpi_name
HAVING total_impacts > 1
ORDER BY full_recovery_rate DESC;

-- y. Most Impacted Customers Overview
SELECT 
    vendor_name,
    total_contracts,
    ROUND(total_contract_value, 2) as total_contract_value,
    total_events,
    high_impact_events,
    recent_events,
    ROUND(avg_kpi_impact, 2) as avg_kpi_impact,
    ROUND(total_value_at_risk, 2) as value_at_risk,
    ROUND(total_value_at_risk / total_contract_value * 100, 2) as risk_percentage,
    CASE 
        WHEN high_impact_events > 2 OR risk_percentage > 10 THEN 'High Risk'
        WHEN high_impact_events > 0 OR risk_percentage > 5 THEN 'Medium Risk'
        ELSE 'Low Risk'
    END as risk_category
FROM vw_vendor_risk_profile
ORDER BY value_at_risk DESC;

-- z. Customer Contract Value vs Impact Correlation
WITH customer_value_tiers AS (
    SELECT 
        vendor_name,
        total_contract_value,
        total_events,
        high_impact_events,
        avg_kpi_impact,
        total_value_at_risk,
        NTILE(4) OVER (ORDER BY total_contract_value) as value_tier
    FROM vw_vendor_risk_profile
)
SELECT 
    CASE value_tier
        WHEN 1 THEN 'Tier 4 (Smallest)'
        WHEN 2 THEN 'Tier 3'
        WHEN 3 THEN 'Tier 2'
        WHEN 4 THEN 'Tier 1 (Largest)'
    END as customer_tier,
    COUNT(*) as customer_count,
    ROUND(AVG(total_contract_value), 2) as avg_contract_value,
    ROUND(AVG(total_events), 2) as avg_events,
    ROUND(AVG(high_impact_events), 2) as avg_high_impact_events,
    ROUND(AVG(avg_kpi_impact), 2) as avg_kpi_impact,
    ROUND(AVG(total_value_at_risk), 2) as avg_value_at_risk,
    ROUND(AVG(total_value_at_risk / total_contract_value * 100), 2) as avg_risk_percentage
FROM customer_value_tiers
GROUP BY value_tier
ORDER BY value_tier DESC;

-- a1. SLA Violation Analysis
WITH sla_violations AS (
    SELECT 
        cei.vendor_id,
        cei.vendor_name,
        e.event_id,
        e.event_title,
        e.occurrence_date,
        e.detection_date,
        es.severity_name,
        es.response_sla_hours,
        ROUND(CAST((JULIANDAY(e.detection_date) - JULIANDAY(e.occurrence_date)) * 24 AS REAL), 2) 
            as response_time_hours,
        CASE 
            WHEN CAST((JULIANDAY(e.detection_date) - JULIANDAY(e.occurrence_date)) * 24 AS REAL) 
                > es.response_sla_hours 
            THEN 1 ELSE 0 
        END as is_sla_breach
    FROM vw_vendor_event_impact cei
    JOIN Event e ON cei.event_id = e.event_id
    JOIN EventSeverity es ON e.severity_id = es.severity_id
)
SELECT 
    vendor_name,
    COUNT(DISTINCT event_id) as total_events,
    SUM(is_sla_breach) as sla_violations,
    ROUND(AVG(CASE WHEN is_sla_breach = 1 
        THEN response_time_hours - response_sla_hours END), 2) as avg_hours_over_sla,
    ROUND(AVG(CASE WHEN severity_name = 'Critical' 
        THEN is_sla_breach END) * 100, 2) as critical_sla_breach_rate,
    GROUP_CONCAT(CASE WHEN is_sla_breach = 1 
        THEN event_title END) as breached_events
FROM sla_violations
GROUP BY vendor_name
HAVING sla_violations > 0
ORDER BY sla_violations DESC;

-- a2. Customer Risk Exposure Trends
WITH monthly_customer_impacts AS (
    SELECT 
        vendor_name,
        strftime('%Y-%m', occurrence_date) as month,
        COUNT(DISTINCT event_id) as monthly_events,
        COUNT(DISTINCT CASE 
            WHEN impact_level IN ('critical', 'high') 
            THEN event_id END) as high_impact_events,
        AVG(avg_kpi_impact) as avg_kpi_impact,
        SUM(CASE 
            WHEN impact_level = 'critical' THEN contract_value * 0.1
            WHEN impact_level = 'high' THEN contract_value * 0.05
            WHEN impact_level = 'medium' THEN contract_value * 0.02
            ELSE contract_value * 0.01
        END) as monthly_value_at_risk
    FROM vw_vendor_event_impact
    WHERE occurrence_date >= DATE('now', '-12 months')
    GROUP BY vendor_name, strftime('%Y-%m', occurrence_date)
)
SELECT 
    vendor_name,
    month,
    monthly_events,
    high_impact_events,
    ROUND(avg_kpi_impact, 2) as avg_kpi_impact,
    ROUND(monthly_value_at_risk, 2) as monthly_value_at_risk,
    ROUND(AVG(monthly_value_at_risk) OVER (
        PARTITION BY vendor_name 
        ORDER BY month 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2) as rolling_3month_risk_avg
FROM monthly_customer_impacts
ORDER BY vendor_name, month;

-- a3. Comprehensive Cost Impact Summary
SELECT 
    event_title,
    event_type,
    severity_name,
    affected_contracts,
    ROUND(total_direct_impact, 2) as direct_impact,
    ROUND(total_degradation_cost, 2) as degradation_cost,
    ROUND(total_financial_impact, 2) as total_impact,
    direct_impact_percentage,
    degradation_impact_percentage,
    ROUND(total_financial_impact / affected_contracts, 2) as avg_impact_per_contract,
    ROUND(projected_annual_impact, 2) as projected_annual_impact
FROM vw_longterm_financial_impact
ORDER BY total_financial_impact DESC;

-- a4. KPI Cost Impact Analysis
SELECT 
    kpi_name,
    kpi_category,
    COUNT(DISTINCT event_id) as affecting_events,
    COUNT(DISTINCT contract_id) as affected_contracts,
    ROUND(AVG(baseline_value), 2) as avg_baseline,
    ROUND(AVG(impact_value), 2) as avg_impact_value,
    ROUND(AVG(degradation_cost), 2) as avg_degradation_cost,
    ROUND(SUM(degradation_cost), 2) as total_degradation_cost
FROM vw_kpi_degradation_cost
GROUP BY kpi_name, kpi_category
ORDER BY total_degradation_cost DESC;

-- a5. Event Type Cost Pattern Analysis
SELECT 
    event_type,
    COUNT(*) as event_count,
    ROUND(AVG(total_direct_impact), 2) as avg_direct_impact,
    ROUND(AVG(total_degradation_cost), 2) as avg_degradation_cost,
    ROUND(AVG(total_financial_impact), 2) as avg_total_impact,
    ROUND(SUM(total_financial_impact), 2) as cumulative_impact,
    ROUND(AVG(direct_impact_percentage), 2) as avg_direct_impact_pct,
    ROUND(AVG(degradation_impact_percentage), 2) as avg_degradation_pct
FROM vw_longterm_financial_impact
GROUP BY event_type
ORDER BY avg_total_impact DESC;

-- a6. Monthly Cost Trend Analysis
SELECT 
    strftime('%Y-%m', occurrence_date) as month,
    COUNT(*) as event_count,
    ROUND(SUM(total_direct_impact), 2) as total_direct_impact,
    ROUND(SUM(total_degradation_cost), 2) as total_degradation_cost,
    ROUND(SUM(total_financial_impact), 2) as total_impact,
    ROUND(AVG(total_financial_impact), 2) as avg_impact_per_event,
    -- Rolling averages
    ROUND(AVG(total_financial_impact) OVER (
        ORDER BY strftime('%Y-%m', occurrence_date)
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2) as rolling_3month_avg_impact
FROM vw_longterm_financial_impact
GROUP BY strftime('%Y-%m', occurrence_date)
ORDER BY month DESC;

-- a7. High-Cost Event Root Cause Analysis
WITH event_costs AS (
    SELECT 
        lfi.event_id,
        lfi.event_title,
        lfi.event_type,
        ec.category_type,
        lfi.severity_name,
        gr.region_name,
        bu.unit_name as business_unit,
        ROUND(lfi.total_financial_impact, 2) as total_impact,
        ROUND(lfi.total_direct_impact, 2) as direct_impact,
        ROUND(lfi.total_degradation_cost, 2) as degradation_cost,
        lfi.affected_contracts
    FROM vw_longterm_financial_impact lfi
    JOIN Event e ON lfi.event_id = e.event_id
    JOIN EventType et ON e.type_id = et.type_id
    JOIN EventCategory ec ON et.category_id = ec.category_id
    LEFT JOIN GeographicRegion gr ON e.region_id = gr.region_id
    LEFT JOIN BusinessUnit bu ON e.business_unit_id = bu.unit_id
    WHERE lfi.total_financial_impact > (
        SELECT AVG(total_financial_impact) 
        FROM vw_longterm_financial_impact
    )
)
SELECT 
    event_type,
    category_type,
    severity_name,
    region_name,
    business_unit,
    COUNT(*) as event_count,
    ROUND(AVG(total_impact), 2) as avg_total_impact,
    ROUND(AVG(direct_impact), 2) as avg_direct_impact,
    ROUND(AVG(degradation_cost), 2) as avg_degradation_cost,
    ROUND(SUM(total_impact), 2) as cumulative_impact,
    AVG(affected_contracts) as avg_affected_contracts
FROM event_costs
GROUP BY 
    event_type, category_type, severity_name,
    region_name, business_unit
ORDER BY avg_total_impact DESC;



