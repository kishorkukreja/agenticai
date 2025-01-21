import sqlite3
import os
from pathlib import Path
import time

"""Create SQLite database and all required tables"""

def create_tables(cursor):
    # Enable foreign key support
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Create Currency Table
    cursor.execute("""
    CREATE TABLE Currency (
        currency_code CHAR(3) PRIMARY KEY,
        currency_name VARCHAR(50) NOT NULL,
        exchange_rate DECIMAL(10,4) DEFAULT 1.0000,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create User Table
    cursor.execute("""
    CREATE TABLE "User" (
        user_id INTEGER PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        role VARCHAR(50) NOT NULL,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create Vendor Table
    cursor.execute("""
    CREATE TABLE Vendor (
        vendor_id INTEGER PRIMARY KEY,
        vendor_name VARCHAR(100) NOT NULL,
        contact_person VARCHAR(100),
        email VARCHAR(100),
        phone VARCHAR(50),
        address TEXT,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create Product Table
    cursor.execute("""
    CREATE TABLE Product (
        product_id INTEGER PRIMARY KEY,
        product_code VARCHAR(50) UNIQUE NOT NULL,
        product_name VARCHAR(100) NOT NULL,
        description TEXT,
        standard_price DECIMAL(15,2),
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create Service Table
    cursor.execute("""
    CREATE TABLE Service (
        service_id INTEGER PRIMARY KEY,
        service_code VARCHAR(50) UNIQUE NOT NULL,
        service_name VARCHAR(100) NOT NULL,
        description TEXT,
        standard_rate DECIMAL(15,2),
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create Unit of Measure Table
    cursor.execute("""
    CREATE TABLE UnitOfMeasure (
        uom_id INTEGER PRIMARY KEY,
        uom_code VARCHAR(20) UNIQUE NOT NULL,
        uom_name VARCHAR(50) NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create Contract Type Table
    cursor.execute("""
    CREATE TABLE ContractType (
        type_id INTEGER PRIMARY KEY,
        type_name VARCHAR(50) NOT NULL,
        description TEXT,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create Contract Status Table
    cursor.execute("""
    CREATE TABLE ContractStatus (
        status_id INTEGER PRIMARY KEY,
        status_name VARCHAR(50) NOT NULL,
        description TEXT,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)


    # Create Contract Header Table
    cursor.execute("""
    CREATE TABLE ContractHeader (
        contract_id INTEGER PRIMARY KEY,
        contract_number VARCHAR(50) UNIQUE NOT NULL,
        vendor_id INTEGER NOT NULL REFERENCES Vendor(vendor_id),
        contract_type_id INTEGER NOT NULL REFERENCES ContractType(type_id),
        status_id INTEGER NOT NULL REFERENCES ContractStatus(status_id),
        start_date DATE NOT NULL,
        end_date DATE NOT NULL,
        total_value DECIMAL(15,2) NOT NULL,
        currency_code CHAR(3) NOT NULL REFERENCES Currency(currency_code),
        terms_conditions TEXT,
        created_by INTEGER NOT NULL REFERENCES "User"(user_id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT valid_dates CHECK (end_date >= start_date)
                   )
    """)

    
    # Create Contract Line Table
    cursor.execute("""
    CREATE TABLE ContractLine (
        line_id INTEGER PRIMARY KEY,
        contract_id INTEGER NOT NULL REFERENCES ContractHeader(contract_id),
        product_id INTEGER REFERENCES Product(product_id),
        service_id INTEGER REFERENCES Service(service_id),
        uom_id INTEGER NOT NULL REFERENCES UnitOfMeasure(uom_id),
        quantity DECIMAL(15,2) NOT NULL,
        unit_price DECIMAL(15,2) NOT NULL,
        line_value DECIMAL(15,2),  
        delivery_start DATE,
        delivery_end DATE,
        line_description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT product_or_service CHECK (
            (product_id IS NOT NULL AND service_id IS NULL) OR 
            (product_id IS NULL AND service_id IS NOT NULL)
        )
    )
    """)

    # Create Contract Payment Schedule  Table
    cursor.execute("""
   CREATE TABLE ContractPaymentSchedule (
    schedule_id INTEGER PRIMARY KEY,
    contract_id INTEGER NOT NULL REFERENCES ContractHeader(contract_id),
    due_date DATE NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    payment_type VARCHAR(50) NOT NULL,
    is_paid BOOLEAN DEFAULT FALSE,
    paid_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create Contract Ammendment Table
    cursor.execute("""
   CREATE TABLE ContractAmendment (
    amendment_id INTEGER PRIMARY KEY,
    contract_id INTEGER NOT NULL REFERENCES ContractHeader(contract_id),
    amendment_date DATE NOT NULL,
    description TEXT NOT NULL,
    changed_fields JSON NOT NULL,
    change_reason TEXT NOT NULL,
    created_by INTEGER NOT NULL REFERENCES "User"(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    ################################ KPIs & Meta KPIs Tables #################

    # Create KPI Category Table
    cursor.execute("""
    CREATE TABLE KPICategory (
        category_id INTEGER PRIMARY KEY,
        category_name VARCHAR(50) NOT NULL,
        description TEXT,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create KPI Type Table
    cursor.execute("""
    CREATE TABLE KPIType (
        type_id INTEGER PRIMARY KEY,
        type_name VARCHAR(20) NOT NULL CHECK (type_name IN ('service', 'product')),
        description TEXT,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create KPI Definition Table
    cursor.execute("""
    CREATE TABLE KPIDefinition (
        kpi_id INTEGER PRIMARY KEY,
        category_id INTEGER NOT NULL REFERENCES KPICategory(category_id),
        type_id INTEGER NOT NULL REFERENCES KPIType(type_id),
        kpi_name VARCHAR(100) NOT NULL,
        description TEXT,
        measure_unit VARCHAR(50),
        target_threshold DECIMAL(10,2),
        calculation_method TEXT,
        is_active BOOLEAN DEFAULT TRUE,
        frequency_days INTEGER DEFAULT 30,
        weight DECIMAL(5,2) DEFAULT 1.00,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create Contract KPI Measurement Table
    cursor.execute("""
    CREATE TABLE ContractKPIMeasurement (
        measurement_id INTEGER PRIMARY KEY,
        contract_id INTEGER NOT NULL REFERENCES ContractHeader(contract_id),
        kpi_id INTEGER NOT NULL REFERENCES KPIDefinition(kpi_id),
        measure_date DATE NOT NULL,
        actual_value DECIMAL(15,2),
        target_value DECIMAL(15,2),
        achievement_percentage DECIMAL(5,2), 
        status VARCHAR(20),
        comments TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create Meta KPI Tables
    cursor.execute("""
    CREATE TABLE MetaKPIDefinition (
        meta_kpi_id INTEGER PRIMARY KEY,
        meta_kpi_name VARCHAR(100) NOT NULL,
        description TEXT,
        target_threshold DECIMAL(5,2) NOT NULL,
        calculation_frequency VARCHAR(20) CHECK (calculation_frequency IN ('daily', 'weekly', 'monthly')),
        filter_condition TEXT,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE MetaKPIComponent (
        component_id INTEGER PRIMARY KEY,
        meta_kpi_id INTEGER NOT NULL REFERENCES MetaKPIDefinition(meta_kpi_id),
        kpi_id INTEGER NOT NULL REFERENCES KPIDefinition(kpi_id),
        weight DECIMAL(5,2) NOT NULL CHECK (weight > 0 AND weight <= 1),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT unique_kpi_per_meta UNIQUE (meta_kpi_id, kpi_id)
    )
    """)

    ################################ EVENTS TABLES ###########################


    # Create Event Category Table
    cursor.execute("""
    CREATE TABLE EventCategory (
        category_id INTEGER PRIMARY KEY,
        category_name VARCHAR(50) NOT NULL,
        category_type VARCHAR(20) NOT NULL CHECK (category_type IN ('internal', 'external')),
        description TEXT,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create Event Type Table
    cursor.execute("""
    CREATE TABLE EventType (
        type_id INTEGER PRIMARY KEY,
        category_id INTEGER NOT NULL REFERENCES EventCategory(category_id),
        type_name VARCHAR(100) NOT NULL,
        description TEXT,
        monitoring_frequency VARCHAR(20) CHECK (monitoring_frequency IN ('realtime', 'daily', 'weekly', 'monthly')),
        is_automated BOOLEAN DEFAULT FALSE,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create Event Severity Table
    cursor.execute("""
    CREATE TABLE EventSeverity (
        severity_id INTEGER PRIMARY KEY,
        severity_name VARCHAR(20) NOT NULL,
        description TEXT,
        response_sla_hours INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create Event Status Table
    cursor.execute("""
    CREATE TABLE EventStatus (
        status_id INTEGER PRIMARY KEY,
        status_name VARCHAR(50) NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create Geographic Region Table
    cursor.execute("""
    CREATE TABLE GeographicRegion (
        region_id INTEGER PRIMARY KEY,
        region_name VARCHAR(100) NOT NULL,
        parent_region_id INTEGER REFERENCES GeographicRegion(region_id),
        region_type VARCHAR(50) CHECK (region_type IN ('global', 'continent', 'country', 'state', 'city')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create Business Unit Table
    cursor.execute("""
    CREATE TABLE BusinessUnit (
        unit_id INTEGER PRIMARY KEY,
        unit_name VARCHAR(100) NOT NULL,
        parent_unit_id INTEGER REFERENCES BusinessUnit(unit_id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create Event Table
    cursor.execute("""
    CREATE TABLE Event (
        event_id INTEGER PRIMARY KEY,
        type_id INTEGER NOT NULL REFERENCES EventType(type_id),
        severity_id INTEGER NOT NULL REFERENCES EventSeverity(severity_id),
        status_id INTEGER NOT NULL REFERENCES EventStatus(status_id),
        event_title VARCHAR(200) NOT NULL,
        description TEXT,
        occurrence_date TIMESTAMP NOT NULL,
        detection_date TIMESTAMP NOT NULL,
        resolution_date TIMESTAMP,
        region_id INTEGER REFERENCES GeographicRegion(region_id),
        business_unit_id INTEGER REFERENCES BusinessUnit(unit_id),
        source_reference TEXT,
        created_by INTEGER NOT NULL REFERENCES "User"(user_id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create Event Impact Assessment Table
    cursor.execute("""
    CREATE TABLE EventImpactAssessment (
        assessment_id INTEGER PRIMARY KEY,
        event_id INTEGER NOT NULL REFERENCES Event(event_id),
        contract_id INTEGER NOT NULL REFERENCES ContractHeader(contract_id),
        impact_level VARCHAR(20) CHECK (impact_level IN ('none', 'low', 'medium', 'high', 'critical')),
        impact_description TEXT,
        recommended_actions TEXT,
        assessment_date TIMESTAMP NOT NULL,
        assessed_by INTEGER NOT NULL REFERENCES "User"(user_id),
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create Event Notification Table
    cursor.execute("""
    CREATE TABLE EventNotification (
        notification_id INTEGER PRIMARY KEY,
        event_id INTEGER NOT NULL REFERENCES Event(event_id),
        user_id INTEGER NOT NULL REFERENCES "User"(user_id),
        notification_type VARCHAR(50) NOT NULL,
        notification_status VARCHAR(20) CHECK (notification_status IN ('pending', 'sent', 'read')),
        sent_at TIMESTAMP,
        read_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create Event Trigger Rule Table
    cursor.execute("""
    CREATE TABLE EventTriggerRule (
        rule_id INTEGER PRIMARY KEY,
        event_type_id INTEGER NOT NULL REFERENCES EventType(type_id),
        rule_name VARCHAR(100) NOT NULL,
        rule_condition JSON NOT NULL,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create KPI Trigger Threshold Table
    cursor.execute("""
    CREATE TABLE KPITriggerThreshold (
        threshold_id INTEGER PRIMARY KEY,
        kpi_id INTEGER NOT NULL REFERENCES KPIDefinition(kpi_id),
        rule_id INTEGER NOT NULL REFERENCES EventTriggerRule(rule_id),
        threshold_value DECIMAL(15,2) NOT NULL,
        comparison_operator VARCHAR(2) CHECK (comparison_operator IN ('>', '<', '>=', '<=', '=')),
        monitoring_period_months INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create the Meta KPI Threshold table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS MetaKPITriggerThreshold (
        threshold_id INTEGER PRIMARY KEY,
        meta_kpi_id INTEGER NOT NULL REFERENCES MetaKPIDefinition(meta_kpi_id),
        rule_id INTEGER NOT NULL REFERENCES EventTriggerRule(rule_id),
        threshold_config JSON NOT NULL,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT unique_meta_kpi_rule UNIQUE (meta_kpi_id, rule_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE MetaKPIMeasurement (
        measurement_id INTEGER PRIMARY KEY,
        meta_kpi_id INTEGER NOT NULL REFERENCES MetaKPIDefinition(meta_kpi_id),
        measurement_date DATE NOT NULL,
        calculated_value DECIMAL(15,2) NOT NULL,
        target_value DECIMAL(15,2) NOT NULL,
        achievement_percentage DECIMAL(5,2),  
        status VARCHAR(20),  
        measurement_details JSON,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)



def create_indexes(cursor):
    """Create indexes for commonly queried columns"""
    
    # Contract Related Indexes
    cursor.execute("""
    CREATE INDEX idx_contract_vendor ON ContractHeader(vendor_id);
    """)
    
    cursor.execute("""
    CREATE INDEX idx_contract_dates ON ContractHeader(start_date, end_date);
    """)
    
    cursor.execute("""
    CREATE INDEX idx_contract_status ON ContractHeader(status_id);
    """)
    
    cursor.execute("""
    CREATE INDEX idx_contract_value ON ContractHeader(total_value);
    """)
    
    # Contract Line Indexes
    cursor.execute("""
    CREATE INDEX idx_contractline_contract ON ContractLine(contract_id);
    """)
    
    cursor.execute("""
    CREATE INDEX idx_contractline_product ON ContractLine(product_id);
    """)
    
    cursor.execute("""
    CREATE INDEX idx_contractline_service ON ContractLine(service_id);
    """)
    
    # Event Related Indexes
    cursor.execute("""
    CREATE INDEX idx_event_type ON Event(type_id);
    """)
    
    cursor.execute("""
    CREATE INDEX idx_event_status ON Event(status_id);
    """)
    
    cursor.execute("""
    CREATE INDEX idx_event_severity ON Event(severity_id);
    """)
    
    cursor.execute("""
    CREATE INDEX idx_event_dates ON Event(occurrence_date, detection_date, resolution_date);
    """)
    
    cursor.execute("""
    CREATE INDEX idx_event_region ON Event(region_id);
    """)
    
    cursor.execute("""
    CREATE INDEX idx_event_business_unit ON Event(business_unit_id);
    """)
    
    # KPI Related Indexes
    cursor.execute("""
    CREATE INDEX idx_kpi_measurement ON ContractKPIMeasurement(contract_id, kpi_id, measure_date);
    """)
    
    cursor.execute("""
    CREATE INDEX idx_kpi_achievement ON ContractKPIMeasurement(achievement_percentage);
    """)
    
    cursor.execute("""
    CREATE INDEX idx_kpi_status ON ContractKPIMeasurement(status);
    """)
    
    # Meta KPI Related Indexes
    cursor.execute("""
    CREATE INDEX idx_meta_kpi_measurement ON MetaKPIMeasurement(meta_kpi_id, measurement_date);
    """)
    
    cursor.execute("""
    CREATE INDEX idx_meta_kpi_achievement ON MetaKPIMeasurement(achievement_percentage);
    """)
    
    # Event Impact Assessment Indexes
    cursor.execute("""
    CREATE INDEX idx_impact_event ON EventImpactAssessment(event_id);
    """)
    
    cursor.execute("""
    CREATE INDEX idx_impact_contract ON EventImpactAssessment(contract_id);
    """)
    
    cursor.execute("""
    CREATE INDEX idx_impact_level ON EventImpactAssessment(impact_level);
    """)
    
    # Event Notification Indexes
    cursor.execute("""
    CREATE INDEX idx_notification_event ON EventNotification(event_id);
    """)
    
    cursor.execute("""
    CREATE INDEX idx_notification_user ON EventNotification(user_id);
    """)
    
    cursor.execute("""
    CREATE INDEX idx_notification_status ON EventNotification(notification_status);
    """)
    
    # Hierarchical Data Indexes
    cursor.execute("""
    CREATE INDEX idx_region_parent ON GeographicRegion(parent_region_id);
    """)
    
    cursor.execute("""
    CREATE INDEX idx_business_unit_parent ON BusinessUnit(parent_unit_id);
    """)

    # Create index for performance
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_meta_kpi_threshold 
    ON MetaKPITriggerThreshold(meta_kpi_id, rule_id)
    """)
    
    print("Created all indexes successfully!")


def main():
    # Database file path
    db_path = 'contract_management.db'
    
    # # Remove existing database if it exists
    # if os.path.exists(db_path):
    #     os.remove(db_path)
    #     print(f"Removed existing database: {db_path}")
    # # Try to remove the file with retry logic
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            if os.path.exists(db_path):
                os.remove(db_path)
                print(f"Removed existing database: {db_path}")
            break
        except PermissionError:
            if attempt < max_attempts - 1:
                print(f"Database is locked, retrying in 2 seconds... (Attempt {attempt + 1}/{max_attempts})")
                time.sleep(2)
            else:
                print("Could not remove database file. Please ensure it's not open in another program.")
                print("You can try these steps:")
                print("1. Close any DB browser applications")
                print("2. Close any Python shells or notebooks using the database")
                print("3. Restart your IDE")
                return
    
    # Create new database and tables
    try:
        conn = sqlite3.connect(db_path)
        print(f"Created new database: {db_path}")
        
        create_tables(conn.cursor())
        create_indexes(conn.cursor())
        conn.commit()
        print("Successfully created all tables & Indexes!")
        
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()