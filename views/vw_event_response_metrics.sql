CREATE VIEW vw_event_response_metrics AS
SELECT 
    e.event_id,
    e.event_title,
    e.occurrence_date,
    e.detection_date,
    e.resolution_date,
    et.type_name as event_type,
    ec.category_name as event_category,
    es.severity_name,
    es.response_sla_hours,
    est.status_name as event_status,
    -- Response time calculations (in hours)
    ROUND(CAST((JULIANDAY(e.detection_date) - JULIANDAY(e.occurrence_date)) * 24 AS REAL), 2) 
        as detection_time_hours,
    CASE 
        WHEN e.resolution_date IS NOT NULL THEN
            ROUND(CAST((JULIANDAY(e.resolution_date) - JULIANDAY(e.detection_date)) * 24 AS REAL), 2)
        ELSE NULL
    END as resolution_time_hours,
    -- Total incident duration (if resolved)
    CASE 
        WHEN e.resolution_date IS NOT NULL THEN
            ROUND(CAST((JULIANDAY(e.resolution_date) - JULIANDAY(e.occurrence_date)) * 24 AS REAL), 2)
        ELSE NULL
    END as total_incident_hours,
    -- SLA Status
    CASE 
        WHEN e.resolution_date IS NULL THEN 'Open'
        WHEN CAST((JULIANDAY(e.detection_date) - JULIANDAY(e.occurrence_date)) * 24 AS REAL) <= es.response_sla_hours THEN 'Within SLA'
        ELSE 'SLA Breached'
    END as sla_status,
    -- Impact metrics
    (SELECT impact_level 
     FROM EventImpactAssessment 
     WHERE event_id = e.event_id 
     ORDER BY CASE impact_level 
         WHEN 'critical' THEN 1 
         WHEN 'high' THEN 2 
         WHEN 'medium' THEN 3 
         WHEN 'low' THEN 4 
         ELSE 5 
     END LIMIT 1) as highest_impact_level,
    (SELECT COUNT(DISTINCT contract_id) 
     FROM EventImpactAssessment 
     WHERE event_id = e.event_id) as affected_contracts_count
FROM Event e
JOIN EventType et ON e.type_id = et.type_id
JOIN EventCategory ec ON et.category_id = ec.category_id
JOIN EventSeverity es ON e.severity_id = es.severity_id
JOIN EventStatus est ON e.status_id = est.status_id;	
