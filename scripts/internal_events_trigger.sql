-- Insert new internal event categories
INSERT INTO EventCategory (category_name, category_type, description) 
SELECT 'Organizational Change', 'internal', 'Major organizational structure and leadership changes'
WHERE NOT EXISTS (SELECT 1 FROM EventCategory WHERE category_name = 'Organizational Change');

INSERT INTO EventCategory (category_name, category_type, description) 
SELECT 'Infrastructure Event', 'internal', 'IT and facility infrastructure related events'
WHERE NOT EXISTS (SELECT 1 FROM EventCategory WHERE category_name = 'Infrastructure Event');

INSERT INTO EventCategory (category_name, category_type, description) 
SELECT 'Resource Management', 'internal', 'Events related to workforce and resource allocation'
WHERE NOT EXISTS (SELECT 1 FROM EventCategory WHERE category_name = 'Resource Management');

INSERT INTO EventCategory (category_name, category_type, description) 
SELECT 'Process Change', 'internal', 'Significant changes in internal processes and procedures'
WHERE NOT EXISTS (SELECT 1 FROM EventCategory WHERE category_name = 'Process Change');

-- Insert event types for Organizational Change
INSERT INTO EventType (category_id, type_name, description, monitoring_frequency, is_automated)
SELECT 
    (SELECT category_id FROM EventCategory WHERE category_name = 'Organizational Change'),
    'Leadership Change',
    'Changes in key leadership positions affecting contract oversight',
    'monthly',
    0
WHERE NOT EXISTS (SELECT 1 FROM EventType WHERE type_name = 'Leadership Change');

INSERT INTO EventType (category_id, type_name, description, monitoring_frequency, is_automated)
SELECT 
    (SELECT category_id FROM EventCategory WHERE category_name = 'Organizational Change'),
    'Department Restructuring',
    'Reorganization of departments affecting contract management',
    'monthly',
    0
WHERE NOT EXISTS (SELECT 1 FROM EventType WHERE type_name = 'Department Restructuring');

-- Insert event types for Infrastructure Event
INSERT INTO EventType (category_id, type_name, description, monitoring_frequency, is_automated)
SELECT 
    (SELECT category_id FROM EventCategory WHERE category_name = 'Infrastructure Event'),
    'System Outage',
    'Critical system downtime affecting contract operations',
    'realtime',
    1
WHERE NOT EXISTS (SELECT 1 FROM EventType WHERE type_name = 'System Outage');

INSERT INTO EventType (category_id, type_name, description, monitoring_frequency, is_automated)
SELECT 
    (SELECT category_id FROM EventCategory WHERE category_name = 'Infrastructure Event'),
    'Facility Disruption',
    'Physical facility issues affecting operations',
    'realtime',
    1
WHERE NOT EXISTS (SELECT 1 FROM EventType WHERE type_name = 'Facility Disruption');

-- Insert event types for Resource Management
INSERT INTO EventType (category_id, type_name, description, monitoring_frequency, is_automated)
SELECT 
    (SELECT category_id FROM EventCategory WHERE category_name = 'Resource Management'),
    'Workforce Reduction',
    'Significant reduction in workforce affecting contract delivery',
    'weekly',
    0
WHERE NOT EXISTS (SELECT 1 FROM EventType WHERE type_name = 'Workforce Reduction');

INSERT INTO EventType (category_id, type_name, description, monitoring_frequency, is_automated)
SELECT 
    (SELECT category_id FROM EventCategory WHERE category_name = 'Resource Management'),
    'Budget Constraint',
    'Major budget cuts affecting contract resources',
    'monthly',
    1
WHERE NOT EXISTS (SELECT 1 FROM EventType WHERE type_name = 'Budget Constraint');

-- Create trigger rules
INSERT INTO EventTriggerRule (event_type_id, rule_name, rule_condition, is_active)
SELECT 
    type_id,
    'Critical_System_Downtime',
    '{"type": "system_metric", "threshold": {"duration_minutes": 30, "severity": "high"}}',
    1
FROM EventType 
WHERE type_name = 'System Outage'
AND NOT EXISTS (
    SELECT 1 FROM EventTriggerRule 
    WHERE rule_name = 'Critical_System_Downtime'
);

INSERT INTO EventTriggerRule (event_type_id, rule_name, rule_condition, is_active)
SELECT 
    type_id,
    'Budget_Threshold_Alert',
    '{"type": "budget_metric", "threshold": {"percentage_reduction": 15, "period_months": 3}}',
    1
FROM EventType 
WHERE type_name = 'Budget Constraint'
AND NOT EXISTS (
    SELECT 1 FROM EventTriggerRule 
    WHERE rule_name = 'Budget_Threshold_Alert'
);

-- Insert Events with sequential IDs
INSERT INTO Event (
    event_id,
    type_id,
    severity_id,
    status_id,
    event_title,
    description,
    occurrence_date,
    detection_date,
    region_id,
    business_unit_id,
    source_reference,
    created_by,
    created_at,
    updated_at
)
SELECT
    (SELECT COALESCE(MAX(event_id), 0) FROM Event) + rowid,
    et.type_id,
    (SELECT severity_id FROM EventSeverity WHERE severity_name = 'High'),
    (SELECT status_id FROM EventStatus WHERE status_name = 'In Progress'),
    CASE et.type_name 
        WHEN 'Leadership Change' THEN 'CFO Transition Announcement'
        WHEN 'System Outage' THEN 'ERP System Critical Downtime'
        WHEN 'Workforce Reduction' THEN '15% Workforce Reduction Program'
        ELSE 'Q3 Emergency Budget Cut'
    END,
    CASE et.type_name
        WHEN 'Leadership Change' THEN 'Planned transition of CFO position affecting financial oversight of contracts'
        WHEN 'System Outage' THEN 'Unplanned ERP system outage affecting contract management operations'
        WHEN 'Workforce Reduction' THEN 'Company-wide workforce reduction program affecting contract delivery capabilities'
        ELSE 'Immediate 20% budget reduction across all departments'
    END,
    datetime('now'),
    datetime('now'),
    (SELECT region_id FROM GeographicRegion WHERE region_name = 'Global Operations'),
    (SELECT unit_id FROM BusinessUnit WHERE unit_name = 'Global Operations'),
    'INT-' || CAST((SELECT COALESCE(MAX(event_id), 0) FROM Event) + rowid AS TEXT),
    (SELECT user_id FROM "User" WHERE is_active = 1 LIMIT 1),
    datetime('now'),
    datetime('now')
FROM EventType et
WHERE et.type_name IN ('Leadership Change', 'System Outage', 'Workforce Reduction', 'Budget Constraint');