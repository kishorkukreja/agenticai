CREATE VIEW vw_recent_event_details AS
SELECT 
    e.event_id,
    e.event_title,
    e.description,
    e.occurrence_date,
    e.detection_date,
    e.resolution_date,
    et.type_name as event_type,
    ec.category_name as event_category,
    ec.category_type,
    es.severity_name,
    es.response_sla_hours,
    est.status_name as event_status,
    -- Geographic region
    gr.region_name as location,
    gr.region_type,
    -- Business unit
    bu.unit_name as business_unit
FROM Event e
JOIN EventType et ON e.type_id = et.type_id
JOIN EventCategory ec ON et.category_id = ec.category_id
JOIN EventSeverity es ON e.severity_id = es.severity_id
JOIN EventStatus est ON e.status_id = est.status_id
LEFT JOIN GeographicRegion gr ON e.region_id = gr.region_id
LEFT JOIN BusinessUnit bu ON e.business_unit_id = bu.unit_id
WHERE e.occurrence_date >= DATE('now', '-7 days');
