-- Function to get next assessment ID
CREATE TEMPORARY TABLE IF NOT EXISTS temp_sequence (next_id INTEGER);
INSERT INTO temp_sequence VALUES ((SELECT COALESCE(MAX(assessment_id), 0) + 1 FROM EventImpactAssessment));

-- Leadership Change Impact
INSERT INTO EventImpactAssessment (
    assessment_id,
    event_id,
    contract_id,
    impact_level,
    impact_description,
    recommended_actions,
    assessment_date,
    assessed_by,
    is_active,
    created_at,
    updated_at
)
SELECT 
    temp_sequence.next_id + (ROW_NUMBER() OVER (ORDER BY ch.contract_id) - 1),
    e.event_id,
    ch.contract_id,
    CASE 
        WHEN ch.total_value > 500000 THEN 'high'
        WHEN ch.total_value > 100000 THEN 'medium'
        ELSE 'low'
    END as impact_level,
    CASE 
        WHEN ch.total_value > 500000 
        THEN 'High-value contract requiring immediate leadership review and risk assessment'
        WHEN ch.total_value > 100000 
        THEN 'Medium-value contract requiring review within next quarter'
        ELSE 'Low-value contract to be reviewed as per regular schedule'
    END as impact_description,
    'Schedule contract review meeting with new leadership team. Update approval matrices and signing authorities.' as recommended_actions,
    datetime('now'),
    (SELECT user_id FROM "User" WHERE role = 'Contract Manager' LIMIT 1),
    1,
    datetime('now'),
    datetime('now')
FROM Event e
JOIN EventType et ON e.type_id = et.type_id
JOIN ContractHeader ch ON ch.status_id IN (
    SELECT status_id FROM ContractStatus WHERE status_name IN ('Active', 'Under Review', 'Negotiation')
)
CROSS JOIN temp_sequence
WHERE et.type_name = 'Leadership Change'
AND e.event_title = 'CFO Transition Announcement'
AND NOT EXISTS (
    SELECT 1 FROM EventImpactAssessment eia 
    WHERE eia.event_id = e.event_id 
    AND eia.contract_id = ch.contract_id
);

-- Update sequence for next batch
UPDATE temp_sequence 
SET next_id = (SELECT MAX(assessment_id) + 1 FROM EventImpactAssessment);

-- System Outage Impact
INSERT INTO EventImpactAssessment (
    assessment_id,
    event_id,
    contract_id,
    impact_level,
    impact_description,
    recommended_actions,
    assessment_date,
    assessed_by,
    is_active,
    created_at,
    updated_at
)
SELECT 
    temp_sequence.next_id + (ROW_NUMBER() OVER (ORDER BY ch.contract_id) - 1),
    e.event_id,
    ch.contract_id,
    'critical' as impact_level,
    'System outage affecting contract management capabilities. Risk of missing contractual obligations and deadlines.' as impact_description,
    'Implement manual tracking procedures. Notify affected customers of potential delays. Schedule catch-up data entry once systems are restored.' as recommended_actions,
    datetime('now'),
    (SELECT user_id FROM "User" WHERE role = 'Contract Manager' LIMIT 1),
    1,
    datetime('now'),
    datetime('now')
FROM Event e
JOIN EventType et ON e.type_id = et.type_id
JOIN ContractHeader ch ON ch.status_id IN (
    SELECT status_id FROM ContractStatus WHERE status_name IN ('Active', 'Under Review')
)
CROSS JOIN temp_sequence
WHERE et.type_name = 'System Outage'
AND NOT EXISTS (
    SELECT 1 FROM EventImpactAssessment eia 
    WHERE eia.event_id = e.event_id 
    AND eia.contract_id = ch.contract_id
)
LIMIT 10;

-- Update sequence for next batch
UPDATE temp_sequence 
SET next_id = (SELECT MAX(assessment_id) + 1 FROM EventImpactAssessment);

-- Workforce Reduction Impact
INSERT INTO EventImpactAssessment (
    assessment_id,
    event_id,
    contract_id,
    impact_level,
    impact_description,
    recommended_actions,
    assessment_date,
    assessed_by,
    is_active,
    created_at,
    updated_at
)
SELECT 
    temp_sequence.next_id + (ROW_NUMBER() OVER (ORDER BY ch.contract_id) - 1),
    e.event_id,
    ch.contract_id,
    CASE 
        WHEN cl.service_id IS NOT NULL THEN 'high'
        ELSE 'medium'
    END as impact_level,
    CASE 
        WHEN cl.service_id IS NOT NULL 
        THEN 'Service delivery capacity severely affected due to workforce reduction'
        ELSE 'Product delivery and support capacity affected by workforce reduction'
    END as impact_description,
    CASE 
        WHEN cl.service_id IS NOT NULL 
        THEN 'Reassign service delivery teams. Review service level commitments. Notify customers of potential changes.'
        ELSE 'Review product support capacity. Adjust delivery schedules if needed.'
    END as recommended_actions,
    datetime('now'),
    (SELECT user_id FROM "User" WHERE role = 'Contract Manager' LIMIT 1),
    1,
    datetime('now'),
    datetime('now')
FROM Event e
JOIN EventType et ON e.type_id = et.type_id
JOIN ContractHeader ch ON ch.status_id IN (
    SELECT status_id FROM ContractStatus WHERE status_name = 'Active'
)
JOIN ContractLine cl ON ch.contract_id = cl.contract_id
CROSS JOIN temp_sequence
WHERE et.type_name = 'Workforce Reduction'
AND NOT EXISTS (
    SELECT 1 FROM EventImpactAssessment eia 
    WHERE eia.event_id = e.event_id 
    AND eia.contract_id = ch.contract_id
)
GROUP BY ch.contract_id;

-- Update sequence for next batch
UPDATE temp_sequence 
SET next_id = (SELECT MAX(assessment_id) + 1 FROM EventImpactAssessment);

-- Budget Constraint Impact
INSERT INTO EventImpactAssessment (
    assessment_id,
    event_id,
    contract_id,
    impact_level,
    impact_description,
    recommended_actions,
    assessment_date,
    assessed_by,
    is_active,
    created_at,
    updated_at
)
SELECT 
    temp_sequence.next_id + (ROW_NUMBER() OVER (ORDER BY ch.contract_id) - 1),
    e.event_id,
    ch.contract_id,
    CASE 
        WHEN ch.total_value > 500000 OR cl.service_id IS NOT NULL THEN 'high'
        ELSE 'medium'
    END as impact_level,
    CASE 
        WHEN ch.total_value > 500000 
        THEN 'High-value contract affected by budget constraints. Risk to delivery capacity.'
        ELSE 'Contract delivery costs need review due to budget constraints'
    END as impact_description,
    'Review contract profitability. Identify cost optimization opportunities. Consider renegotiation if necessary.' as recommended_actions,
    datetime('now'),
    (SELECT user_id FROM "User" WHERE role = 'Contract Manager' LIMIT 1),
    1,
    datetime('now'),
    datetime('now')
FROM Event e
JOIN EventType et ON e.type_id = et.type_id
JOIN ContractHeader ch ON ch.status_id IN (
    SELECT status_id FROM ContractStatus WHERE status_name = 'Active'
)
JOIN ContractLine cl ON ch.contract_id = cl.contract_id
CROSS JOIN temp_sequence
WHERE et.type_name = 'Budget Constraint'
AND NOT EXISTS (
    SELECT 1 FROM EventImpactAssessment eia 
    WHERE eia.event_id = e.event_id 
    AND eia.contract_id = ch.contract_id
)
GROUP BY ch.contract_id;

-- Clean up
DROP TABLE IF EXISTS temp_sequence;