CREATE VIEW vw_event_response_summary AS
SELECT
    severity_name,
    event_type,
    event_category,
    COUNT(*) as total_events,
    -- Response time metrics
    ROUND(AVG(detection_time_hours), 2) as avg_detection_hours,
    ROUND(MIN(detection_time_hours), 2) as min_detection_hours,
    ROUND(MAX(detection_time_hours), 2) as max_detection_hours,
    ROUND(AVG(resolution_time_hours), 2) as avg_resolution_hours,
    ROUND(AVG(total_incident_hours), 2) as avg_total_duration_hours,
    -- SLA compliance
    SUM(CASE WHEN sla_status = 'Within SLA' THEN 1 ELSE 0 END) as sla_compliant_count,
    SUM(CASE WHEN sla_status = 'SLA Breached' THEN 1 ELSE 0 END) as sla_breached_count,
    SUM(CASE WHEN sla_status = 'Open' THEN 1 ELSE 0 END) as open_events_count,
    ROUND(CAST(SUM(CASE WHEN sla_status = 'Within SLA' THEN 1 ELSE 0 END) AS FLOAT) / 
          COUNT(*) * 100, 2) as sla_compliance_rate
FROM vw_event_response_metrics
GROUP BY severity_name, event_type, event_category;
