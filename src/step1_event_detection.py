import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json
from dataclasses import dataclass
from enum import Enum

class EventSource(Enum):
    EXTERNAL = "external"
    INTERNAL_KPI = "internal_kpi"
    ORGANIZATIONAL = "organizational"

@dataclass
class Event:
    title: str
    description: str
    source_type: EventSource
    severity_level: Optional[str] = None
    event_type_id: Optional[int] = None
    region_id: Optional[int] = None
    business_unit_id: Optional[int] = None
    source_reference: Optional[str] = None
    created_by: int = 1  # Default user ID

class EventProcessor:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_db_connection(self) -> sqlite3.Connection:
        """Create database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def validate_event(self, event: Event) -> Tuple[bool, str]:
        """
        Validate incoming event based on business rules
        Returns: (is_valid: bool, validation_message: str)
        """
        with self._get_db_connection() as conn:
            cursor = conn.cursor()

            # 1. Check if event type exists (if provided)
            if event.event_type_id:
                cursor.execute("""
                    SELECT EXISTS(
                        SELECT 1 FROM EventType 
                        WHERE type_id = ? AND is_active = 1
                    )
                """, (event.event_type_id,))
                if not cursor.fetchone()[0]:
                    return False, "Invalid event type ID"

            # 2. Check if region exists (if provided)
            if event.region_id:
                cursor.execute("""
                    SELECT EXISTS(
                        SELECT 1 FROM GeographicRegion 
                        WHERE region_id = ?
                    )
                """, (event.region_id,))
                if not cursor.fetchone()[0]:
                    return False, "Invalid region ID"

            # 3. Check if business unit exists (if provided)
            if event.business_unit_id:
                cursor.execute("""
                    SELECT EXISTS(
                        SELECT 1 FROM BusinessUnit 
                        WHERE unit_id = ?
                    )
                """, (event.business_unit_id,))
                if not cursor.fetchone()[0]:
                    return False, "Invalid business unit ID"

            # 4. Basic validation checks
            if not event.title or len(event.title.strip()) < 5:
                return False, "Event title is too short"
            
            if not event.description or len(event.description.strip()) < 10:
                return False, "Event description is too short"

            return True, "Event validated successfully"

    def determine_event_priority(self, event: Event) -> Dict:
        """
        Determine event priority based on multiple factors
        Returns priority details including score and factors
        """
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            
            priority_factors = {
                "severity_score": 0,
                "business_impact": 0,
                "urgency": 0,
                "scope": 0
            }

            # 1. Severity Assessment
            if event.severity_level:
                cursor.execute("""
                    SELECT response_sla_hours 
                    FROM EventSeverity 
                    WHERE severity_name = ?
                """, (event.severity_level,))
                sla_hours = cursor.fetchone()
                if sla_hours:
                    # Convert SLA hours to priority score (lower SLA = higher priority)
                    priority_factors["severity_score"] = min(100, int(24 / sla_hours[0] * 100))

            # 2. Business Impact Assessment
            if event.business_unit_id:
                cursor.execute("""
                    SELECT COUNT(*) 
                   FROM ContractHeader ch
                    JOIN EventImpactAssessment eia ON ch.contract_id = eia.contract_id
                    JOIN Event e ON eia.event_id = e.event_id
                    WHERE e.business_unit_id = ?
                    AND eia.impact_level IN ('high', 'critical') 
                """, (event.business_unit_id,))
                high_impact_count = cursor.fetchone()[0]
                priority_factors["business_impact"] = min(100, high_impact_count * 10)

            # 3. Calculate final priority score (0-100)
            total_score = sum(priority_factors.values()) / len(priority_factors)
            
            priority_level = "Low" if total_score < 40 else "Medium" if total_score < 70 else "High"

            return {
                "priority_level": priority_level,
                "priority_score": total_score,
                "factors": priority_factors
            }

    def map_affected_contracts(self, event: Event) -> List[Dict]:
        """
        Map event to potentially affected contracts based on various criteria
        """
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Base query to find potentially affected contracts
            query = """
                SELECT DISTINCT 
                    ch.vendor_id,
                    ch.contract_number,
                    c.vendor_name,
                    ch.total_value,
                    ch.start_date,
                    ch.end_date
                FROM ContractHeader ch
                JOIN Vendor c ON ch.vendor_id = c.vendor_id
                WHERE ch.status_id IN (
                    SELECT status_id 
                    FROM ContractStatus 
                    WHERE status_name IN ('Active', 'Under Review')
                )
            """
            
            params = []
            conditions = []

            # Add business unit filter if applicable
            # if event.business_unit_id:
            #     conditions.append("ch.business_unit_id = ?")
            #     params.append(event.business_unit_id)

            # # Add region filter if applicable
            # if event.region_id:
            #     conditions.append("ch.region_id = ?")
            #     params.append(event.region_id)

            # # Combine conditions
            # if conditions:
            #     query += " AND " + " AND ".join(conditions)

            cursor.execute(query, params)
            affected_contracts = [dict(row) for row in cursor.fetchall()]

            return affected_contracts

    def classify_event(self, event: Event, priority_details: Dict) -> Dict:
        """
        Classify event based on type, impact, and priority
        """
        with self._get_db_connection() as conn:
            cursor = conn.cursor()

            # Get event type details if available
            event_type_info = {}
            if event.event_type_id:
                cursor.execute("""
                    SELECT 
                        et.type_name,
                        et.monitoring_frequency,
                        ec.category_name,
                        ec.category_type
                    FROM EventType et
                    JOIN EventCategory ec ON et.category_id = ec.category_id
                    WHERE et.type_id = ?
                """, (event.event_type_id,))
                row = cursor.fetchone()
                if row:
                    event_type_info = dict(row)

            # Determine response requirements based on priority
            response_requirements = {
                "High": {
                    "max_response_time": "2 hours",
                    "required_approvals": ["Department Head", "Risk Management"],
                    "notification_level": "Immediate"
                },
                "Medium": {
                    "max_response_time": "8 hours",
                    "required_approvals": ["Team Lead"],
                    "notification_level": "Standard"
                },
                "Low": {
                    "max_response_time": "24 hours",
                    "required_approvals": [],
                    "notification_level": "Routine"
                }
            }[priority_details["priority_level"]]

            return {
                "event_type": event_type_info,
                "priority_level": priority_details["priority_level"],
                "priority_score": priority_details["priority_score"],
                "response_requirements": response_requirements,
                "source_type": event.source_type.value,
                "detection_time": datetime.now().isoformat(),
                "classification_confidence": self._calculate_confidence_score(event, priority_details)
            }

    def _calculate_confidence_score(self, event: Event, priority_details: Dict) -> float:
        """Calculate confidence score for event classification"""
        confidence_factors = {
            "has_event_type": bool(event.event_type_id) * 0.2,
            "has_severity": bool(event.severity_level) * 0.2,
            "has_location": bool(event.region_id) * 0.15,
            "has_business_unit": bool(event.business_unit_id) * 0.15,
            "priority_score": min(priority_details["priority_score"] / 100, 1) * 0.3
        }
        return sum(confidence_factors.values()) * 100

    def process_event(self, event: Event) -> Dict:
        """
        Main method to process an incoming event through all steps
        """
        # Step 1: Validate Event
        is_valid, validation_message = self.validate_event(event)
        if not is_valid:
            raise ValueError(f"Event validation failed: {validation_message}")

        # Step 2: Determine Priority
        priority_details = self.determine_event_priority(event)

        # Step 3: Map Affected Contracts
        affected_contracts = self.map_affected_contracts(event)

        # Step 4: Classify Event
        classification = self.classify_event(event, priority_details)

        # Compile and return complete event processing results
        return {
            "event_details": {
                "title": event.title,
                "description": event.description,
                "source_type": event.source_type.value,
                "detection_time": datetime.now().isoformat()
            },
            "validation": {
                "is_valid": is_valid,
                "message": validation_message
            },
            "priority": priority_details,
            "affected_contracts": affected_contracts,
            "classification": classification
        }

# Example usage:
def main():
    # Initialize processor
    processor = EventProcessor(r"C:\Users\Kish Kukreja\OneDrive\Desktop\agenticai\data\contract_management.db")
    
    # Create sample event
    sample_event = Event(
        title="Supply Chain Disruption - Chip Shortage",
        description="Critical shortage of semiconductor components affecting production schedule",
        source_type=EventSource.EXTERNAL,
        severity_level="High",
        event_type_id=1,  # Assuming this exists in your DB
        region_id=1,      # Assuming this exists in your DB
        business_unit_id=1 # Assuming this exists in your DB
    )
    
    # Process event
    try:
        result = processor.process_event(sample_event)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error processing event: {str(e)}")

if __name__ == "__main__":
    main()