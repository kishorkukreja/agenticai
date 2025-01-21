import sqlite3
import random
from datetime import datetime, timedelta, date
from faker import Faker
import json
import uuid
import pandas as pd

# Initialize Faker
fake = Faker()

# Define date adapter functions
def adapt_date(val):
    return val.isoformat()

def convert_date(val):
    return datetime.strptime(val.decode(), "%Y-%m-%d").date()

def adapt_datetime(val):
    return val.isoformat()

def convert_datetime(val):
    return datetime.fromisoformat(val.decode())

# Register adapters
sqlite3.register_adapter(date, adapt_date)
sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("DATE", convert_date)
sqlite3.register_converter("DATETIME", convert_datetime)
sqlite3.register_converter("TIMESTAMP", convert_datetime)


def generate_currencies(cursor, num_records=10):
    currencies = [
        ('USD', 'US Dollar', 1.0000),
        ('EUR', 'Euro', 1.1000),
        ('GBP', 'British Pound', 1.2500),
        ('JPY', 'Japanese Yen', 0.0090),
        ('CAD', 'Canadian Dollar', 0.7800),
        ('AUD', 'Australian Dollar', 0.7400),
        ('CHF', 'Swiss Franc', 1.1200),
        ('CNY', 'Chinese Yuan', 0.1500),
        ('INR', 'Indian Rupee', 0.0135),
        ('SGD', 'Singapore Dollar', 0.7500)
    ]
    
    cursor.executemany("""
        INSERT INTO Currency (currency_code, currency_name, exchange_rate, is_active)
        VALUES (?, ?, ?, 1)
    """, currencies)
    
    print(f"Inserted {len(currencies)} currencies")

def generate_users(cursor, num_records=50):
    roles = ['Contract Manager', 'Account Executive', 'Legal Advisor', 'Finance Manager', 'Operations Manager']
    users = []
    
    for i in range(num_records):
        username = fake.user_name()
        email = fake.email()
        role = random.choice(roles)
        is_active = random.random() > 0.1  # 90% active users
        
        users.append((username, email, role, is_active))
    
    cursor.executemany("""
        INSERT INTO "User" (username, email, role, is_active)
        VALUES (?, ?, ?, ?)
    """, users)
    
    print(f"Inserted {num_records} users")

def generate_vendors(cursor, num_records=100):
    vendors = []
    
    for i in range(num_records):
        vendor_name = fake.company()
        contact_person = fake.name()
        email = fake.company_email()
        phone = fake.phone_number()
        address = fake.address()
        is_active = random.random() > 0.1
        
        vendors.append((vendor_name, contact_person, email, phone, address, is_active))
    
    cursor.executemany("""
        INSERT INTO Vendor (vendor_name, contact_person, email, phone, address, is_active)
        VALUES (?, ?, ?, ?, ?, ?)
    """, vendors)
    
    print(f"Inserted {num_records} vendors")

def generate_realistic_product_description(product_type):
    """Generate realistic product descriptions based on type"""
    
    hardware_products = [
        {
            "name": "Enterprise Server",
            "description": "High-performance rack server featuring dual Intel Xeon processors, up to 2TB RAM, redundant power supplies, and hot-swappable drives. Ideal for mission-critical applications and data centers. Includes remote management capabilities and advanced cooling system.",
            "price_range": (2000, 15000)
        },
        {
            "name": "Network Switch",
            "description": "Managed Layer 3 switch with 48 Gigabit Ethernet ports, 4 SFP+ uplinks, and PoE+ capability. Supports advanced QoS, VLAN management, and security features. Enterprise-grade reliability with lifetime warranty.",
            "price_range": (1000, 5000)
        },
        {
            "name": "Storage Array",
            "description": "Enterprise storage solution with 24 drive bays, supporting up to 384TB raw capacity. Features dual controllers, multiple RAID configurations, and high-speed cache. Includes snapshot, replication, and encryption capabilities.",
            "price_range": (5000, 20000)
        },
        {
            "name": "Workstation",
            "description": "Professional workstation with latest-gen Intel Core i9 processor, NVIDIA RTX graphics, 64GB RAM, and NVMe storage. Certified for major CAD and creative applications. Includes thermal optimization and tool-less chassis design.",
            "price_range": (1500, 8000)
        }
    ]
    
    software_products = [
        {
            "name": "Enterprise Resource Planning Suite",
            "description": "Comprehensive ERP solution covering financial management, inventory control, procurement, and HR functions. Features real-time analytics, customizable dashboards, and mobile accessibility. Includes annual maintenance and 24/7 support.",
            "price_range": (5000, 50000)
        },
        {
            "name": "Security Management Platform",
            "description": "Advanced security information and event management (SIEM) platform with real-time threat detection, automated incident response, and compliance reporting. Includes AI-powered analytics and threat intelligence integration.",
            "price_range": (3000, 25000)
        },
        {
            "name": "Business Intelligence Tool",
            "description": "Data visualization and analytics platform supporting multiple data sources, custom reporting, and predictive analytics. Features interactive dashboards, scheduled reports, and natural language querying.",
            "price_range": (2000, 15000)
        },
        {
            "name": "Collaboration Suite",
            "description": "Integrated collaboration platform with video conferencing, document sharing, project management, and team messaging. Includes enterprise-grade security, SSO integration, and API access.",
            "price_range": (1000, 10000)
        }
    ]
    
    license_products = [
        {
            "name": "Database Management System License",
            "description": "Enterprise database license supporting unlimited cores, high availability features, and advanced security options. Includes 24/7 premium support, quarterly updates, and disaster recovery tools.",
            "price_range": (5000, 100000)
        },
        {
            "name": "Development Platform License",
            "description": "Full-featured IDE license with support for multiple programming languages, integrated debugging, and version control. Includes code analysis tools, cloud deployment integration, and plugin ecosystem.",
            "price_range": (500, 5000)
        },
        {
            "name": "Virtual Machine License Pack",
            "description": "Enterprise virtualization license pack supporting unlimited VMs, live migration, and advanced resource management. Includes high availability features and disaster recovery capabilities.",
            "price_range": (3000, 30000)
        }
    ]
    
    equipment_products = [
        {
            "name": "Data Center Cooling System",
            "description": "Precision cooling solution for data center environments, featuring variable speed fans, humidity control, and smart temperature management. Includes remote monitoring and predictive maintenance capabilities.",
            "price_range": (10000, 50000)
        },
        {
            "name": "UPS System",
            "description": "Enterprise-grade uninterruptible power supply with online double conversion, extended runtime batteries, and network management card. Features hot-swappable batteries and power conditioning.",
            "price_range": (2000, 20000)
        },
        {
            "name": "Network Cable Tester",
            "description": "Professional cable certification tester supporting Cat 6A/7/8 and fiber optic cables. Features touchscreen interface, cloud reporting, and advanced diagnostics. Includes calibration certificate.",
            "price_range": (1000, 8000)
        }
    ]
    
    tool_products = [
        {
            "name": "Network Monitoring Tool",
            "description": "Comprehensive network monitoring solution with bandwidth analysis, device tracking, and alert management. Features customizable thresholds, automated mapping, and performance trending.",
            "price_range": (1000, 10000)
        },
        {
            "name": "Backup Solution",
            "description": "Enterprise backup and recovery tool supporting multiple platforms, deduplication, and encryption. Features automated scheduling, retention policies, and cloud integration.",
            "price_range": (2000, 15000)
        },
        {
            "name": "IT Asset Management Tool",
            "description": "Asset lifecycle management solution with automated discovery, license tracking, and compliance reporting. Includes software metering, patch management, and warranty tracking.",
            "price_range": (1500, 12000)
        }
    ]
    
    product_categories = {
        'Hardware': hardware_products,
        'Software': software_products,
        'License': license_products,
        'Equipment': equipment_products,
        'Tool': tool_products
    }
    
    selected_product = random.choice(product_categories[product_type])
    return selected_product

def generate_products(cursor, num_records=50):
    """Generate realistic product records"""
    product_types = ['Hardware', 'Software', 'License', 'Equipment', 'Tool']
    products = []
    
    for i in range(num_records):
        product_type = random.choice(product_types)
        product_info = generate_realistic_product_description(product_type)
        
        product_code = f"{product_type[:3].upper()}{str(i+1).zfill(4)}"
        product_name = f"{product_info['name']} - {product_type}"
        description = product_info['description']
        min_price, max_price = product_info['price_range']
        standard_price = round(random.uniform(min_price, max_price), 2)
        is_active = random.random() > 0.1
        
        products.append((
            product_code,
            product_name,
            description,
            standard_price,
            is_active
        ))
    
    cursor.executemany("""
        INSERT INTO Product (
            product_code,
            product_name,
            description,
            standard_price,
            is_active
        ) VALUES (?, ?, ?, ?, ?)
    """, products)
    
    print(f"Inserted {num_records} products")

def generate_realistic_service_description(service_type):
    """Generate realistic service descriptions based on type"""
    
    consulting_services = [
        {
            "name": "IT Strategy Consulting",
            "description": "Comprehensive IT strategy development and digital transformation consulting. Includes technology roadmap planning, architecture assessment, and innovation strategy. Deliverables include detailed recommendations, implementation roadmap, and ROI analysis.",
            "rate_range": (200, 400)
        },
        {
            "name": "Security Assessment Consulting",
            "description": "In-depth cybersecurity assessment and consulting services. Covers vulnerability assessment, penetration testing, security architecture review, and compliance gap analysis. Includes detailed reporting and remediation recommendations.",
            "rate_range": (250, 450)
        },
        {
            "name": "Cloud Migration Consulting",
            "description": "Expert guidance on cloud migration strategy and execution. Includes workload assessment, cloud provider selection, migration planning, and cost optimization. Features TCO analysis and architectural design services.",
            "rate_range": (225, 425)
        },
        {
            "name": "Data Analytics Consulting",
            "description": "Advanced analytics and data strategy consulting services. Covers data architecture design, BI strategy, predictive analytics implementation, and data governance framework development.",
            "rate_range": (275, 475)
        }
    ]
    
    maintenance_services = [
        {
            "name": "Infrastructure Maintenance",
            "description": "Proactive infrastructure maintenance service including regular health checks, performance optimization, and preventive maintenance. Features 24/7 monitoring, quarterly audits, and capacity planning.",
            "rate_range": (150, 300)
        },
        {
            "name": "Database Maintenance",
            "description": "Comprehensive database maintenance service covering performance tuning, backup verification, patch management, and health monitoring. Includes quarterly optimization reviews and capacity planning.",
            "rate_range": (175, 350)
        },
        {
            "name": "Network Maintenance",
            "description": "Professional network infrastructure maintenance including performance monitoring, configuration management, and security updates. Features proactive troubleshooting and quarterly network audits.",
            "rate_range": (160, 320)
        },
        {
            "name": "Security Systems Maintenance",
            "description": "Regular maintenance of security systems including firewall rule updates, IDS/IPS tuning, and security patch management. Includes monthly security posture reviews and threat assessment.",
            "rate_range": (200, 375)
        }
    ]
    
    support_services = [
        {
            "name": "24/7 Technical Support",
            "description": "Round-the-clock technical support service with guaranteed response times. Includes incident management, problem resolution, and escalation handling. Features dedicated support team and regular service reviews.",
            "rate_range": (100, 250)
        },
        {
            "name": "Enterprise Application Support",
            "description": "Comprehensive application support covering troubleshooting, bug fixes, and performance optimization. Includes user support, application monitoring, and regular maintenance updates.",
            "rate_range": (150, 300)
        },
        {
            "name": "Cloud Infrastructure Support",
            "description": "Dedicated support for cloud infrastructure including availability monitoring, performance optimization, and cost management. Features 24/7 monitoring and monthly service reviews.",
            "rate_range": (175, 350)
        },
        {
            "name": "End-User Support",
            "description": "Professional end-user support services including helpdesk, desktop support, and user account management. Features ticket tracking system and regular satisfaction surveys.",
            "rate_range": (75, 200)
        }
    ]
    
    training_services = [
        {
            "name": "Security Awareness Training",
            "description": "Comprehensive security awareness training program covering phishing prevention, data protection, and security best practices. Includes interactive modules, assessments, and certification.",
            "rate_range": (120, 250)
        },
        {
            "name": "Technical Skills Training",
            "description": "Hands-on technical training for IT professionals covering latest technologies and best practices. Features practical exercises, case studies, and certification preparation.",
            "rate_range": (150, 300)
        },
        {
            "name": "Cloud Technology Training",
            "description": "Specialized training in cloud technologies including architecture, security, and optimization. Includes hands-on labs, real-world scenarios, and best practices guidance.",
            "rate_range": (200, 400)
        },
        {
            "name": "Application User Training",
            "description": "Custom application training programs for end-users including workflow optimization and best practices. Features hands-on exercises and user documentation.",
            "rate_range": (100, 250)
        }
    ]
    
    implementation_services = [
        {
            "name": "ERP Implementation",
            "description": "End-to-end ERP implementation service including requirement analysis, customization, data migration, and user training. Features project management, change management, and post-go-live support.",
            "rate_range": (200, 450)
        },
        {
            "name": "Cloud Migration Implementation",
            "description": "Professional cloud migration services including workload migration, testing, and optimization. Features minimal downtime strategies and comprehensive testing protocols.",
            "rate_range": (225, 475)
        },
        {
            "name": "Security Solution Implementation",
            "description": "Expert implementation of security solutions including SIEM, endpoint protection, and access management. Includes configuration, integration, and validation testing.",
            "rate_range": (250, 500)
        },
        {
            "name": "Network Infrastructure Implementation",
            "description": "Comprehensive network implementation services including design, deployment, and optimization. Features performance testing and documentation delivery.",
            "rate_range": (175, 400)
        }
    ]
    
    service_categories = {
        'Consulting': consulting_services,
        'Maintenance': maintenance_services,
        'Support': support_services,
        'Training': training_services,
        'Implementation': implementation_services
    }
    
    selected_service = random.choice(service_categories[service_type])
    return selected_service

def generate_services(cursor, num_records=30):
    """Generate realistic service records"""
    service_types = ['Consulting', 'Maintenance', 'Support', 'Training', 'Implementation']
    services = []
    
    for i in range(num_records):
        service_type = random.choice(service_types)
        service_info = generate_realistic_service_description(service_type)
        
        service_code = f"{service_type[:3].upper()}{str(i+1).zfill(4)}"
        service_name = f"{service_info['name']} - {service_type}"
        description = service_info['description']
        min_rate, max_rate = service_info['rate_range']
        standard_rate = round(random.uniform(min_rate, max_rate), 2)
        is_active = random.random() > 0.1
        
        services.append((
            service_code,
            service_name,
            description,
            standard_rate,
            is_active
        ))
    
    cursor.executemany("""
        INSERT INTO Service (
            service_code,
            service_name,
            description,
            standard_rate,
            is_active
        ) VALUES (?, ?, ?, ?, ?)
    """, services)
    
    print(f"Inserted {num_records} services")

def generate_uom(cursor):
    units = [
        ('PCS', 'Pieces', 'Individual unit count'),
        ('HRS', 'Hours', 'Time in hours'),
        ('DAYS', 'Days', 'Time in days'),
        ('MTH', 'Months', 'Time in months'),
        ('KG', 'Kilograms', 'Weight in kilograms'),
        ('LIC', 'Licenses', 'Software licenses'),
        ('USR', 'Users', 'Number of users'),
        ('PKG', 'Package', 'Complete package'),
        ('SET', 'Set', 'Collection of items')
    ]
    
    cursor.executemany("""
        INSERT INTO UnitOfMeasure (uom_code, uom_name, description)
        VALUES (?, ?, ?)
    """, units)
    
    print(f"Inserted {len(units)} units of measure")

def generate_contract_types(cursor):
    types = [
        ('Fixed Price', 'Contract with a fixed total price'),
        ('Time & Material', 'Billing based on time and materials used'),
        ('Subscription', 'Recurring subscription contract'),
        ('Framework', 'Framework agreement with multiple orders'),
        ('Maintenance', 'Service maintenance contract')
    ]
    
    cursor.executemany("""
        INSERT INTO ContractType (type_name, description, is_active)
        VALUES (?, ?, 1)
    """, types)
    
    print(f"Inserted {len(types)} contract types")

def generate_contract_statuses(cursor):
    statuses = [
        ('Draft', 'Initial contract draft'),
        ('Under Review', 'Contract is being reviewed'),
        ('Negotiation', 'In negotiation with vendor'),
        ('Approved', 'Contract has been approved'),
        ('Active', 'Contract is currently active'),
        ('On Hold', 'Contract temporarily on hold'),
        ('Terminated', 'Contract has been terminated'),
        ('Completed', 'Contract has been completed'),
        ('Expired', 'Contract has expired'),
        ('Cancelled', 'Contract has been cancelled')
    ]
    
    cursor.executemany("""
        INSERT INTO ContractStatus (status_name, description, is_active)
        VALUES (?, ?, 1)
    """, statuses)
    
    print(f"Inserted {len(statuses)} contract statuses")

def insert_base_data(conn):
    cursor = conn.cursor()
    
    # Generate base data
    generate_currencies(cursor)
    generate_users(cursor)
    generate_vendors(cursor)
    generate_products(cursor)
    generate_services(cursor)
    generate_uom(cursor)
    generate_contract_types(cursor)
    generate_contract_statuses(cursor)
    
    conn.commit()
    print("Base data generation completed!")

def generate_contracts(cursor, num_contracts=400):
    # Get IDs from related tables
    cursor.execute("SELECT vendor_id FROM Vendor WHERE is_active = 1")
    vendor_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT type_id FROM ContractType WHERE is_active = 1")
    contract_type_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT status_id FROM ContractStatus WHERE is_active = 1")
    contract_status_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT currency_code FROM Currency WHERE is_active = 1")
    currency_codes = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT user_id FROM User WHERE is_active = 1")
    user_ids = [row[0] for row in cursor.fetchall()]
    
    # Generate contracts
    contracts = []
    current_date = datetime.now()
    
    for i in range(num_contracts):
        contract_number = f"CTR{str(i+1).zfill(6)}"
        vendor_id = random.choice(vendor_ids)
        contract_type_id = random.choice(contract_type_ids)
        status_id = random.choice(contract_status_ids)
        
        # Generate realistic dates
        start_date = current_date - timedelta(days=random.randint(0, 365*2))  # Up to 2 years in the past
        duration_days = random.choice([90, 180, 365, 730])  # 3 months, 6 months, 1 year, or 2 years
        end_date = start_date + timedelta(days=duration_days)
        
        total_value = round(random.uniform(10000, 1000000), 2)
        currency_code = random.choice(currency_codes)
        terms_conditions = fake.text(max_nb_chars=500)
        created_by = random.choice(user_ids)
        
        contracts.append((
            contract_number, vendor_id, contract_type_id, status_id,
            start_date.date(), end_date.date(), total_value, currency_code,
            terms_conditions, created_by
        ))
    
    cursor.executemany("""
        INSERT INTO ContractHeader (
            contract_number, vendor_id, contract_type_id, status_id,
            start_date, end_date, total_value, currency_code,
            terms_conditions, created_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, contracts)
    
    print(f"Inserted {num_contracts} contracts")
    return contracts

def generate_contract_lines(cursor):
    # Get necessary reference data
    cursor.execute("SELECT contract_id FROM ContractHeader")
    contract_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT product_id FROM Product WHERE is_active = 1")
    product_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT service_id FROM Service WHERE is_active = 1")
    service_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT uom_id FROM UnitOfMeasure")
    uom_ids = [row[0] for row in cursor.fetchall()]
    
    contract_lines = []
    
    for contract_id in contract_ids:
        # Generate 1-5 lines per contract
        num_lines = random.randint(1, 5)
        
        for _ in range(num_lines):
            # Randomly choose between product and service
            if random.random() < 0.6:  # 60% chance of product
                product_id = random.choice(product_ids)
                service_id = None
            else:
                product_id = None
                service_id = random.choice(service_ids)
            
            quantity = round(random.uniform(1, 100), 2)
            unit_price = round(random.uniform(100, 10000), 2)
            line_value = quantity * unit_price  # Calculate line value
            
            contract_lines.append((
                contract_id,
                product_id,
                service_id,
                random.choice(uom_ids),
                quantity,
                unit_price,
                line_value,  # Include calculated value
                fake.date_between(start_date='-1y', end_date='+1y'),
                fake.date_between(start_date='+1y', end_date='+2y'),
                fake.text(max_nb_chars=200)
            ))
    
    cursor.executemany("""
        INSERT INTO ContractLine (
            contract_id, product_id, service_id, uom_id,
            quantity, unit_price, line_value,
            delivery_start, delivery_end, line_description
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, contract_lines)
    
    print(f"Inserted {len(contract_lines)} contract lines")

def generate_payment_schedules(cursor):
    cursor.execute("SELECT contract_id, start_date, end_date, total_value FROM ContractHeader")
    contracts = cursor.fetchall()
    
    payment_schedules = []
    payment_types = ['Milestone', 'Monthly', 'Quarterly', 'Annual']
    
    for contract in contracts:
        contract_id, start_date, end_date, total_value = contract
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Determine number of payments based on contract duration
        duration_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        payment_type = random.choice(payment_types)
        
        if payment_type == 'Monthly':
            num_payments = max(1, duration_months)
        elif payment_type == 'Quarterly':
            num_payments = max(1, duration_months // 3)
        elif payment_type == 'Annual':
            num_payments = max(1, duration_months // 12)
        else:  # Milestone
            num_payments = random.randint(2, 4)
        
        payment_amount = round(total_value / num_payments, 2)
        
        for i in range(num_payments):
            if payment_type == 'Monthly':
                due_date = start_date + timedelta(days=30 * i)
            elif payment_type == 'Quarterly':
                due_date = start_date + timedelta(days=90 * i)
            elif payment_type == 'Annual':
                due_date = start_date + timedelta(days=365 * i)
            else:  # Milestone
                interval = (end_date - start_date) / (num_payments - 1)
                due_date = start_date + (interval * i)
            
            is_paid = due_date.date() < datetime.now().date()
            paid_date = due_date if is_paid else None
            
            payment_schedules.append((
                contract_id, due_date.date(), payment_amount, payment_type,
                is_paid, paid_date
            ))
    
    cursor.executemany("""
        INSERT INTO ContractPaymentSchedule (
            contract_id, due_date, amount, payment_type,
            is_paid, paid_date
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, payment_schedules)
    
    print(f"Inserted {len(payment_schedules)} payment schedules")

def generate_kpi_categories(cursor):
    categories = [
        ('Service Quality', 'Metrics related to service delivery quality'),
        ('Product Quality', 'Metrics related to product quality'),
        ('Customer Satisfaction', 'Metrics measuring customer satisfaction levels'),
        ('Operational Efficiency', 'Metrics for operational performance'),
        ('Compliance', 'Metrics for regulatory and standard compliance'),
        ('Risk Management', 'Metrics related to risk assessment and management')
    ]
    
    cursor.executemany("""
        INSERT INTO KPICategory (category_name, description, is_active)
        VALUES (?, ?, 1)
    """, categories)
    
    print(f"Inserted {len(categories)} KPI categories")

def generate_kpi_types(cursor):
    types = [
        ('service', 'Service-related performance indicators'),
        ('product', 'Product-related performance indicators')
    ]
    
    cursor.executemany("""
        INSERT INTO KPIType (type_name, description, is_active)
        VALUES (?, ?, 1)
    """, types)
    
    print(f"Inserted {len(types)} KPI types")

def generate_kpi_definitions(cursor):
    # Get category and type IDs
    cursor.execute("SELECT category_id, category_name FROM KPICategory")
    categories = {name: id for id, name in cursor.fetchall()}
    
    cursor.execute("SELECT type_id, type_name FROM KPIType")
    types = {name: id for id, name in cursor.fetchall()}
    
    # Define KPIs with their properties
    kpis = [
        # Service KPIs
        ('Data Integrity', categories['Service Quality'], types['service'], 'Percentage of accurate data records', '%', 57.0, 30),
        ('Supplier Risk Rating', categories['Risk Management'], types['service'], 'Overall risk score', 'score', 35.0, 90),
        ('Technical Expertise', categories['Service Quality'], types['service'], 'Technical competency score', 'score', 35.0, 30),
        ('Cost of Poor Supplier Quality', categories['Operational Efficiency'], types['service'], 'Cost impact', 'USD', 26.0, 30),
        ('Subject Matter Expertise', categories['Service Quality'], types['service'], 'Expertise assessment score', 'score', 26.0, 90),
        ('Customer Complaints', categories['Customer Satisfaction'], types['service'], 'Number of complaints', 'count', 48.0, 30),
        ('Deadline Adherence Rate', categories['Operational Efficiency'], types['service'], 'On-time delivery percentage', '%', 20.0, 30),
        ('Employee Turnover Rate', categories['Operational Efficiency'], types['service'], 'Staff turnover percentage', '%', 2.0, 30),
        ('Internal Stakeholder Complaints', categories['Service Quality'], types['service'], 'Internal complaint count', 'count', 48.0, 30),
        ('On-Time Delivery Rate', categories['Operational Efficiency'], types['service'], 'Delivery timeliness', '%', 81.0, 30),
        
        # Product KPIs
        ('Audit Results', categories['Compliance'], types['product'], 'Audit success rate', '%', 59.0, 90),
        ('CAPA Completion Time', categories['Operational Efficiency'], types['product'], 'Resolution time', 'days', 43.0, 30),
        ('First-Time Pass Rate', categories['Product Quality'], types['product'], 'First pass yield', '%', 19.0, 30),
        ('Lot Acceptance Rate', categories['Product Quality'], types['product'], 'Accepted lots percentage', '%', 20.0, 30),
        ('Defective Parts per Million', categories['Product Quality'], types['product'], 'Defect rate', 'PPM', 30.0, 30),
        ('Percentage of Returns', categories['Customer Satisfaction'], types['product'], 'Return rate', '%', 22.0, 30),
        ('Error Frequency', categories['Product Quality'], types['product'], 'Error rate', '%', 11.0, 30),
        ('Rework', categories['Operational Efficiency'], types['product'], 'Rework percentage', '%', 9.0, 30),
        ('Noncompliance Rate', categories['Compliance'], types['product'], 'Non-compliance percentage', '%', 54.0, 30),
        ('Misdeliveries per Million', categories['Operational Efficiency'], types['product'], 'Delivery error rate', 'PPM', 6.0, 30)
    ]
    
    kpi_data = []
    for kpi_name, category_id, type_id, description, measure_unit, target_threshold, frequency_days in kpis:
        # Calculate weight based on target threshold (normalized)
        weight = round(target_threshold / 100, 2) if target_threshold else 1.00
        
        kpi_data.append((
            category_id, type_id, kpi_name, description, measure_unit,
            target_threshold, f'Standard calculation for {kpi_name}',
            True, frequency_days, weight
        ))
    
    cursor.executemany("""
        INSERT INTO KPIDefinition (
            category_id, type_id, kpi_name, description, measure_unit,
            target_threshold, calculation_method, is_active, frequency_days, weight
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, kpi_data)
    
    print(f"Inserted {len(kpis)} KPI definitions")

def generate_kpi_measurements(cursor):
    cursor.execute("""
        SELECT contract_id 
        FROM ContractHeader 
        WHERE status_id IN (
            SELECT status_id FROM ContractStatus WHERE status_name IN ('Active', 'Completed')
        )
    """)
    contract_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT kpi_id, target_threshold FROM KPIDefinition WHERE is_active = 1")
    kpis = cursor.fetchall()
    
    measurements = []
    current_date = datetime.now().date()
    
    for contract_id in contract_ids:
        for kpi_id, target_threshold in kpis:
            # Generate monthly measurements for the past year
            for month in range(24):
                measure_date = current_date - timedelta(days=30 * month)
                
                actual_value = round(target_threshold * random.uniform(0.7, 1.3), 2)
                target_value = target_threshold
                
                # Calculate achievement percentage
                achievement_percentage = round((actual_value / target_value * 100), 2) if target_value != 0 else None
                
                # Calculate status
                if achievement_percentage:
                    if actual_value >= target_value:
                        status = 'Achieved'
                    elif actual_value >= (target_value * 0.9):
                        status = 'At Risk'
                    else:
                        status = 'Below Target'
                else:
                    status = 'Not Applicable'
                
                measurements.append((
                    contract_id,
                    kpi_id,
                    measure_date,
                    actual_value,
                    target_value,
                    achievement_percentage,
                    status,
                    fake.text(max_nb_chars=100)  # Comments
                ))
    
    cursor.executemany("""
        INSERT INTO ContractKPIMeasurement (
            contract_id, kpi_id, measure_date,
            actual_value, target_value, achievement_percentage,
            status, comments
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, measurements)
    
    print(f"Inserted {len(measurements)} KPI measurements")

def generate_meta_kpi_definitions(cursor):
    meta_kpis = [
        ('Overall Service Quality Index', 
         'Composite measure of core service quality metrics',
         90.0, 'monthly',
         "contract_type IN ('Service', 'Maintenance')"),
         
        ('Service Risk & Compliance',
         'Aggregated view of service-related risks and compliance',
         85.0, 'monthly',
         "contract_type = 'Service'"),
         
        ('Service Customer Satisfaction',
         'Overall service satisfaction measurement',
         95.0, 'monthly',
         "contract_type = 'Service'"),
         
        ('Product Manufacturing Quality',
         'Combined product quality indicators',
         98.0, 'weekly',
         "contract_type IN ('Fixed Price', 'Time & Material')"),
         
        ('Product Compliance & Audit',
         'Aggregated compliance and audit performance',
         95.0, 'monthly',
         "product_id IS NOT NULL"),
         
        ('Product Customer Satisfaction',
         'Overall product satisfaction measurement',
         92.0, 'monthly',
         "product_id IS NOT NULL")
    ]
    
    cursor.executemany("""
        INSERT INTO MetaKPIDefinition (
            meta_kpi_name, description, target_threshold,
            calculation_frequency, filter_condition, is_active
        ) VALUES (?, ?, ?, ?, ?, 1)
    """, meta_kpis)
    
    print(f"Inserted {len(meta_kpis)} meta KPI definitions")

def generate_meta_kpi_components(cursor):
    # Get meta KPI IDs
    cursor.execute("SELECT meta_kpi_id, meta_kpi_name FROM MetaKPIDefinition")
    meta_kpis = {name: id for id, name in cursor.fetchall()}
    
    # Get KPI IDs
    cursor.execute("SELECT kpi_id, kpi_name FROM KPIDefinition")
    kpis = {name: id for id, name in cursor.fetchall()}
    
    components = [
        # Overall Service Quality Index
        (meta_kpis['Overall Service Quality Index'], kpis['Data Integrity'], 0.30),
        (meta_kpis['Overall Service Quality Index'], kpis['Technical Expertise'], 0.25),
        (meta_kpis['Overall Service Quality Index'], kpis['Subject Matter Expertise'], 0.25),
        (meta_kpis['Overall Service Quality Index'], kpis['On-Time Delivery Rate'], 0.20),
        
        # Service Risk & Compliance
        (meta_kpis['Service Risk & Compliance'], kpis['Supplier Risk Rating'], 0.40),
        (meta_kpis['Service Risk & Compliance'], kpis['Data Integrity'], 0.35),
        (meta_kpis['Service Risk & Compliance'], kpis['Employee Turnover Rate'], 0.25),
        
        # Service Customer Satisfaction
        (meta_kpis['Service Customer Satisfaction'], kpis['Customer Complaints'], 0.35),
        (meta_kpis['Service Customer Satisfaction'], kpis['Internal Stakeholder Complaints'], 0.25),
        (meta_kpis['Service Customer Satisfaction'], kpis['Deadline Adherence Rate'], 0.25),
        (meta_kpis['Service Customer Satisfaction'], kpis['On-Time Delivery Rate'], 0.15),
        
        # Product Manufacturing Quality
        (meta_kpis['Product Manufacturing Quality'], kpis['First-Time Pass Rate'], 0.30),
        (meta_kpis['Product Manufacturing Quality'], kpis['Lot Acceptance Rate'], 0.25),
        (meta_kpis['Product Manufacturing Quality'], kpis['Defective Parts per Million'], 0.25),
        (meta_kpis['Product Manufacturing Quality'], kpis['Error Frequency'], 0.20),
        
        # Product Compliance & Audit
        (meta_kpis['Product Compliance & Audit'], kpis['Audit Results'], 0.35),
        (meta_kpis['Product Compliance & Audit'], kpis['Noncompliance Rate'], 0.35),
        (meta_kpis['Product Compliance & Audit'], kpis['CAPA Completion Time'], 0.30),
        
        # Product Customer Satisfaction
        (meta_kpis['Product Customer Satisfaction'], kpis['Percentage of Returns'], 0.40),
        (meta_kpis['Product Customer Satisfaction'], kpis['Misdeliveries per Million'], 0.30),
        (meta_kpis['Product Customer Satisfaction'], kpis['Rework'], 0.30)
    ]
    
    cursor.executemany("""
        INSERT INTO MetaKPIComponent (meta_kpi_id, kpi_id, weight)
        VALUES (?, ?, ?)
    """, components)
    
    print(f"Inserted {len(components)} meta KPI components")

def generate_meta_kpi_measurements(cursor):
    # Get meta KPI definitions and their components
    cursor.execute("""
        SELECT mkd.meta_kpi_id, mkd.calculation_frequency, mkd.target_threshold,
               mkc.kpi_id, mkc.weight
        FROM MetaKPIDefinition mkd
        JOIN MetaKPIComponent mkc ON mkd.meta_kpi_id = mkc.meta_kpi_id
        WHERE mkd.is_active = 1
    """)
    meta_kpi_data = cursor.fetchall()
    
    # Group by meta_kpi_id
    meta_kpis = {}
    for row in meta_kpi_data:
        meta_kpi_id = row[0]
        if meta_kpi_id not in meta_kpis:
            meta_kpis[meta_kpi_id] = {
                'frequency': row[1],
                'target': row[2],
                'components': []
            }
        meta_kpis[meta_kpi_id]['components'].append({
            'kpi_id': row[3],
            'weight': row[4]
        })
    
    measurements = []
    current_date = datetime.now().date()
    
    # Generate measurements for each meta KPI
    for meta_kpi_id, meta_kpi in meta_kpis.items():
        # Determine measurement dates based on frequency
        if meta_kpi['frequency'] == 'weekly':
            interval_days = 7
        elif meta_kpi['frequency'] == 'monthly':
            interval_days = 30
        else:
            interval_days = 30  # default to monthly
        
        # Generate measurements for the past year
        measurement_date = current_date - timedelta(days=730)
        while measurement_date <= current_date:
            # Calculate weighted average of component KPIs
            calculated_value = round(random.uniform(0.85, 1.15) * meta_kpi['target'], 2)
            target_value = round(meta_kpi['target'], 2)
            
            # Calculate achievement percentage (previously GENERATED)
            achievement_percentage = (
                round((calculated_value / target_value * 100), 2)
                if target_value != 0 else None
            )
            
            # Calculate status (previously GENERATED)
            if calculated_value >= target_value:
                status = 'Achieved'
            elif calculated_value >= (target_value * 0.9):
                status = 'At Risk'
            else:
                status = 'Below Target'
            
            # Store measurement details as JSON
            measurement_details = {
                'component_values': [
                    {
                        'kpi_id': comp['kpi_id'],
                        'weight': comp['weight'],
                        'value': round(random.uniform(0.8, 1.2) * 100, 2)
                    }
                    for comp in meta_kpi['components']
                ]
            }
            
            measurements.append((
                meta_kpi_id,
                measurement_date,
                calculated_value,
                target_value,
                achievement_percentage,
                status,
                json.dumps(measurement_details)
            ))
            
            measurement_date += timedelta(days=interval_days)
    
    cursor.executemany("""
        INSERT INTO MetaKPIMeasurement (
            meta_kpi_id, measurement_date, calculated_value,
            target_value, achievement_percentage, status, measurement_details
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, measurements)
    
    print(f"Inserted {len(measurements)} meta KPI measurements")

# def generate_meta_kpi_measurements(cursor):
#     # Get meta KPI definitions and their components
#     cursor.execute("""
#         SELECT mkd.meta_kpi_id, mkd.calculation_frequency, mkd.target_threshold,
#                mkc.kpi_id, mkc.weight
#         FROM MetaKPIDefinition mkd
#         JOIN MetaKPIComponent mkc ON mkd.meta_kpi_id = mkc.meta_kpi_id
#         WHERE mkd.is_active = 1
#     """)
#     meta_kpi_data = cursor.fetchall()
    
#     # Group by meta_kpi_id
#     meta_kpis = {}
#     for row in meta_kpi_data:
#         meta_kpi_id = row[0]
#         if meta_kpi_id not in meta_kpis:
#             meta_kpis[meta_kpi_id] = {
#                 'frequency': row[1],
#                 'target': row[2],
#                 'components': []
#             }
#         meta_kpis[meta_kpi_id]['components'].append({
#             'kpi_id': row[3],
#             'weight': row[4]
#         })
    
#     measurements = []
#     current_date = datetime.now().date()
    
#     # Generate measurements for each meta KPI
#     for meta_kpi_id, meta_kpi in meta_kpis.items():
#         # Determine measurement dates based on frequency
#         if meta_kpi['frequency'] == 'weekly':
#             interval_days = 7
#         elif meta_kpi['frequency'] == 'monthly':
#             interval_days = 30
#         else:
#             interval_days = 30  # default to monthly
        
#         # Generate measurements for the past year
#         measurement_date = current_date - timedelta(days=365)
#         while measurement_date <= current_date:
#             # Calculate weighted average of component KPIs
#             calculated_value = random.uniform(0.85, 1.15) * meta_kpi['target']
#             target_value = meta_kpi['target']
            
#             # Store measurement details as JSON
#             measurement_details = {
#                 'component_values': [
#                     {
#                         'kpi_id': comp['kpi_id'],
#                         'weight': comp['weight'],
#                         'value': round(random.uniform(0.8, 1.2) * 100, 2)
#                     }
#                     for comp in meta_kpi['components']
#                 ]
#             }
            
#             measurements.append((
#                 meta_kpi_id,
#                 measurement_date,
#                 round(calculated_value, 2),
#                 round(target_value, 2),
#                 json.dumps(measurement_details)
#             ))
            
#             measurement_date += timedelta(days=interval_days)
    
#     cursor.executemany("""
#         INSERT INTO MetaKPIMeasurement (
#             meta_kpi_id, measurement_date, calculated_value,
#             target_value, measurement_details
#         ) VALUES (?, ?, ?, ?, ?)
#     """, measurements)
    
#     print(f"Inserted {len(measurements)} meta KPI measurements")

def generate_contract_amendments(cursor, num_amendments=100):
    cursor.execute("SELECT contract_id FROM ContractHeader")
    contract_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT user_id FROM User WHERE is_active = 1")
    user_ids = [row[0] for row in cursor.fetchall()]
    
    amendments = []
    change_types = ['Price Change', 'Duration Extension', 'Scope Change', 'Terms Update']
    
    for _ in range(num_amendments):
        contract_id = random.choice(contract_ids)
        amendment_date = datetime.now() - timedelta(days=random.randint(1, 365))
        description = f"Amendment: {random.choice(change_types)}"
        
        # Generate realistic changed fields
        changed_fields = {
            'field': random.choice(['total_value', 'end_date', 'terms_conditions']),
            'old_value': str(random.randint(1000, 10000)),
            'new_value': str(random.randint(1000, 10000))
        }
        
        change_reason = fake.text(max_nb_chars=200)
        created_by = random.choice(user_ids)
        
        amendments.append((
            contract_id, amendment_date.date(), description,
            json.dumps(changed_fields), change_reason, created_by
        ))
    
    cursor.executemany("""
        INSERT INTO ContractAmendment (
            contract_id, amendment_date, description,
            changed_fields, change_reason, created_by
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, amendments)
    
    print(f"Inserted {num_amendments} contract amendments")

def generate_event_categories(cursor):
    categories = [
        ('Supplier Issue', 'external', 'Issues related to supplier performance or delivery'),
        ('Quality Incident', 'internal', 'Internal quality control incidents'),
        ('Compliance Breach', 'internal', 'Regulatory or policy compliance issues'),
        ('Market Event', 'external', 'Significant market changes affecting contracts'),
        ('Resource Shortage', 'internal', 'Internal resource availability issues'),
        ('Natural Disaster', 'external', 'Natural events affecting operations'),
        ('Security Incident', 'internal', 'Security-related events and breaches'),
        ('Financial Event', 'external', 'Economic events affecting contracts'),
        ('Operational Issue', 'internal', 'Internal operational disruptions'),
        ('Regulatory Change', 'external', 'Changes in regulations affecting contracts')
    ]
    
    cursor.executemany("""
        INSERT INTO EventCategory (category_name, category_type, description, is_active)
        VALUES (?, ?, ?, 1)
    """, categories)
    
    print(f"Inserted {len(categories)} event categories")

def generate_event_types(cursor):
    # Get category IDs
    cursor.execute("SELECT category_id, category_name FROM EventCategory")
    categories = {name: id for id, name in cursor.fetchall()}
    
    event_types = [
        # Supplier Issue types
        (categories['Supplier Issue'], 'Late Delivery', 'Supplier delivery delays', 'daily', True),
        (categories['Supplier Issue'], 'Quality Defect', 'Supplier quality issues', 'realtime', True),
        
        # Quality Incident types
        (categories['Quality Incident'], 'Production Defect', 'Manufacturing quality issues', 'realtime', True),
        (categories['Quality Incident'], 'Service Quality', 'Service delivery issues', 'daily', True),
        
        # Compliance Breach types
        (categories['Compliance Breach'], 'Policy Violation', 'Internal policy violations', 'daily', True),
        (categories['Compliance Breach'], 'Regulatory Non-compliance', 'Regulatory requirement breaches', 'realtime', True),
        
        # Market Event types
        (categories['Market Event'], 'Price Fluctuation', 'Significant market price changes', 'daily', True),
        (categories['Market Event'], 'Supply Chain Disruption', 'Market supply chain issues', 'weekly', True),
        
        # Resource Shortage types
        (categories['Resource Shortage'], 'Staff Shortage', 'Insufficient staffing', 'daily', True),
        (categories['Resource Shortage'], 'Material Shortage', 'Material availability issues', 'daily', True)
    ]
    
    cursor.executemany("""
        INSERT INTO EventType (category_id, type_name, description, monitoring_frequency, is_automated)
        VALUES (?, ?, ?, ?, ?)
    """, event_types)
    
    print(f"Inserted {len(event_types)} event types")

def generate_event_severities(cursor):
    severities = [
        ('Critical', 'Severe impact requiring immediate attention', 2),
        ('High', 'Significant impact requiring urgent attention', 4),
        ('Medium', 'Moderate impact requiring timely attention', 8),
        ('Low', 'Minor impact requiring routine attention', 24),
        ('Negligible', 'Minimal impact requiring monitoring only', 48)
    ]
    
    cursor.executemany("""
        INSERT INTO EventSeverity (severity_name, description, response_sla_hours)
        VALUES (?, ?, ?)
    """, severities)
    
    print(f"Inserted {len(severities)} event severities")

def generate_event_statuses(cursor):
    statuses = [
        ('New', 'Newly reported event'),
        ('Under Investigation', 'Event is being investigated'),
        ('Action Required', 'Action items identified'),
        ('In Progress', 'Remediation in progress'),
        ('Monitoring', 'Event under monitoring'),
        ('Resolved', 'Event has been resolved'),
        ('Closed', 'Event investigation closed')
    ]
    
    cursor.executemany("""
        INSERT INTO EventStatus (status_name, description)
        VALUES (?, ?)
    """, statuses)
    
    print(f"Inserted {len(statuses)} event statuses")

def generate_geographic_regions(cursor):
    regions = [
        # Global
        (None, 'Global Operations', 'global'),
        
        # Continents
        (1, 'North America', 'continent'),
        (1, 'Europe', 'continent'),
        (1, 'Asia Pacific', 'continent'),
        
        # Countries
        (2, 'United States', 'country'),
        (2, 'Canada', 'country'),
        (3, 'United Kingdom', 'country'),
        (3, 'Germany', 'country'),
        (4, 'Japan', 'country'),
        (4, 'China', 'country'),
        
        # States
        (5, 'California', 'state'),
        (5, 'Texas', 'state'),
        (5, 'New York', 'state'),
        
        # Cities
        (11, 'Los Angeles', 'city'),
        (11, 'San Francisco', 'city'),
        (12, 'Houston', 'city'),
        (12, 'Dallas', 'city'),
        (13, 'New York City', 'city')
    ]
    
    cursor.executemany("""
        INSERT INTO GeographicRegion (parent_region_id, region_name, region_type)
        VALUES (?, ?, ?)
    """, regions)
    
    print(f"Inserted {len(regions)} geographic regions")

def generate_business_units(cursor):
    units = [
        # Top level
        (None, 'Global Operations'),
        
        # Divisions
        (1, 'Manufacturing'),
        (1, 'Sales & Distribution'),
        (1, 'Research & Development'),
        
        # Departments under Manufacturing
        (2, 'Production'),
        (2, 'Quality Control'),
        (2, 'Supply Chain'),
        
        # Departments under Sales & Distribution
        (3, 'North America Sales'),
        (3, 'Europe Sales'),
        (3, 'Asia Pacific Sales'),
        
        # Departments under R&D
        (4, 'Product Development'),
        (4, 'Innovation Lab'),
        (4, 'Technical Services')
    ]
    
    cursor.executemany("""
        INSERT INTO BusinessUnit (parent_unit_id, unit_name)
        VALUES (?, ?)
    """, units)
    
    print(f"Inserted {len(units)} business units")

# def generate_events(cursor, num_events=200):
#     """Generate event records"""
#     # Get reference data
#     cursor.execute("SELECT type_id FROM EventType")
#     type_ids = [row[0] for row in cursor.fetchall()]
    
#     cursor.execute("SELECT severity_id FROM EventSeverity")
#     severity_ids = [row[0] for row in cursor.fetchall()]
    
#     cursor.execute("SELECT status_id FROM EventStatus")
#     status_ids = [row[0] for row in cursor.fetchall()]
    
#     cursor.execute("SELECT region_id FROM GeographicRegion")
#     region_ids = [row[0] for row in cursor.fetchall()]
    
#     cursor.execute("SELECT unit_id FROM BusinessUnit")
#     unit_ids = [row[0] for row in cursor.fetchall()]
    
#     cursor.execute("SELECT user_id FROM User WHERE is_active = 1")
#     user_ids = [row[0] for row in cursor.fetchall()]
    
#     events = []
#     current_date = datetime.now()
    
#     for _ in range(num_events):
#         occurrence_date = current_date - timedelta(days=random.randint(1, 365))
#         detection_delay = timedelta(minutes=random.randint(5, 1440))
#         detection_date = occurrence_date + detection_delay
        
#         resolution_date = None
#         if (current_date - occurrence_date).days > 30 and random.random() < 0.7:
#             resolution_date = detection_date + timedelta(days=random.randint(1, 30))
        
#         source_ref = f"REF-{fake.uuid4()[:8]}"
        
#         events.append((
#             random.choice(type_ids),
#             random.choice(severity_ids),
#             random.choice(status_ids),
#             f"Event: {fake.bs()}",
#             fake.text(max_nb_chars=200),
#             occurrence_date.strftime('%Y-%m-%d %H:%M:%S'),
#             detection_date.strftime('%Y-%m-%d %H:%M:%S'),
#             resolution_date.strftime('%Y-%m-%d %H:%M:%S') if resolution_date else None,
#             random.choice(region_ids),
#             random.choice(unit_ids),
#             source_ref,
#             random.choice(user_ids)
#         ))
    
#     cursor.executemany("""
#         INSERT INTO Event (
#             type_id, severity_id, status_id, event_title,
#             description, occurrence_date, detection_date, resolution_date,
#             region_id, business_unit_id, source_reference, created_by
#         ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#     """, events)
    
#     print(f"Inserted {len(events)} events")
#     return [event[10] for event in events]  # Return source references

def generate_realistic_event_description(event_type, severity, business_unit):
    """Generate a realistic event description based on event type and severity"""
    
    templates = {
        'Late Delivery': [
            "Supplier {supplier} reported delays in delivering {component}, impacting {business_unit} operations. Expected delay: {delay} days. Current buffer stock status: {status}.",
            "Logistics disruption at {location} causing delivery delays for {component}. Impact assessment initiated for {business_unit}."
        ],
        'Quality Defect': [
            "Quality audit revealed {issue} in {component} from supplier {supplier}. Affecting {business_unit} with {severity} impact. Batch numbers: {batch}.",
            "Defect rate of {rate}% detected in recent {component} shipment. Quality control team investigating root cause."
        ],
        'Production Defect': [
            "Manufacturing line {line} reported {issue} affecting product quality. Production efficiency dropped to {efficiency}%. Immediate investigation initiated.",
            "Quality control detected {defect_type} defect in {product_line}. Affected units: {units}. Root cause analysis underway."
        ],
        'Service Quality': [
            "Service level degradation reported in {service_area}. Customer satisfaction metrics show {impact}% decline. Recovery plan initiated.",
            "Performance issues detected in {service_type} service delivery. Response times increased by {delay}%."
        ],
        'Policy Violation': [
            "Compliance audit identified {violation_type} policy violation in {department}. Risk level: {severity}. Immediate corrective actions implemented.",
            "Internal review discovered non-adherence to {policy_name} in {business_unit} operations."
        ],
        'Regulatory Non-compliance': [
            "Regulatory audit found {compliance_issue} in {process_area}. Potential impact: {impact_level}. Remediation plan activated.",
            "{regulation_type} compliance gap identified during {audit_type} audit. Affecting {business_unit} operations."
        ],
        'Price Fluctuation': [
            "Market analysis indicates {percentage}% price variation in {commodity}. Impact assessment on contracts initiated.",
            "Significant price volatility detected in {market_sector}. Risk mitigation strategies under review."
        ],
        'Supply Chain Disruption': [
            "Supply chain disruption reported at {location}. {component} availability affected. Impact on {business_unit}: {impact_level}.",
            "Global logistics issues affecting {supply_type} supply chain. Contingency measures activated."
        ],
        'Staff Shortage': [
            "Critical staff shortage reported in {department}. Current capacity at {capacity}%. Impact on service delivery being assessed.",
            "Resource constraints identified in {business_unit}. Temporary staffing solutions being implemented."
        ],
        'Material Shortage': [
            "Inventory alert: {material} stocks below critical threshold. Current level: {level}%. Impact on production schedules being evaluated.",
            "Material shortage affecting {production_line}. Alternative sourcing options under review."
        ]
    }
    
    faker = Faker()
    
    # Get template for event type
    template = random.choice(templates.get(event_type, ["Generic event affecting {business_unit}"]))
    
    # Generate dynamic values
    replacements = {
        'supplier': faker.company(),
        'component': faker.bs(),
        'business_unit': business_unit,
        'delay': random.randint(1, 30),
        'status': random.choice(['Critical', 'Low', 'Adequate']),
        'location': faker.city(),
        'issue': faker.bs(),
        'severity': severity,
        'batch': f"BT-{random.randint(1000, 9999)}",
        'rate': random.randint(1, 15),
        'line': f"L{random.randint(1, 99)}",
        'efficiency': random.randint(60, 95),
        'defect_type': random.choice(['Minor', 'Major', 'Critical']),
        'product_line': f"PL-{random.randint(100, 999)}",
        'units': random.randint(10, 1000),
        'service_area': faker.bs(),
        'impact': random.randint(5, 25),
        'service_type': faker.bs(),
        'violation_type': random.choice(['Minor', 'Major', 'Critical']),
        'department': faker.bs(),
        'policy_name': f"POL-{random.randint(100, 999)}",
        'compliance_issue': faker.bs(),
        'process_area': faker.bs(),
        'impact_level': severity,
        'regulation_type': random.choice(['Safety', 'Environmental', 'Quality', 'Security']),
        'audit_type': random.choice(['Internal', 'External', 'Surprise']),
        'percentage': random.randint(5, 30),
        'commodity': faker.bs(),
        'market_sector': faker.bs(),
        'supply_type': random.choice(['Raw Material', 'Component', 'Equipment']),
        'material': faker.bs(),
        'level': random.randint(10, 40),
        'production_line': f"PROD-{random.randint(100, 999)}",
        'capacity': random.randint(60, 85)
    }
    
    return template.format(**replacements)

def generate_events(cursor, num_events=200):
    """Generate and insert fake event records"""
    # Get reference data
    cursor.execute("SELECT type_id, type_name FROM EventType")
    type_data = cursor.fetchall()
    type_ids = [row[0] for row in type_data]
    type_names = {row[0]: row[1] for row in type_data}
    
    cursor.execute("SELECT severity_id, severity_name FROM EventSeverity")
    severity_data = cursor.fetchall()
    severity_ids = [row[0] for row in severity_data]
    severity_names = {row[0]: row[1] for row in severity_data}
    
    cursor.execute("SELECT status_id FROM EventStatus")
    status_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT region_id FROM GeographicRegion")
    region_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT unit_id, unit_name FROM BusinessUnit")
    unit_data = cursor.fetchall()
    unit_ids = [row[0] for row in unit_data]
    unit_names = {row[0]: row[1] for row in unit_data}
    
    cursor.execute("SELECT user_id FROM User WHERE is_active = 1")
    user_ids = [row[0] for row in cursor.fetchall()]
    
    events = []
    current_date = datetime.now()
    
    for _ in range(num_events):
        type_id = random.choice(type_ids)
        severity_id = random.choice(severity_ids)
        unit_id = random.choice(unit_ids)
        
        # Generate description using templates
        description = generate_realistic_event_description(
            type_names[type_id],
            severity_names[severity_id],
            unit_names[unit_id]
        )
        
        occurrence_date = current_date - timedelta(days=random.randint(1, 365))
        detection_delay = timedelta(minutes=random.randint(5, 1440))
        detection_date = occurrence_date + detection_delay
        
        resolution_date = None
        if (current_date - occurrence_date).days > 30 and random.random() < 0.7:
            resolution_date = detection_date + timedelta(days=random.randint(1, 30))
        
        source_ref = f"REF-{str(uuid.uuid4())[:8]}"
        
        events.append((
            type_id,
            severity_id,
            random.choice(status_ids),
            f"Event: {description[:50]}...",  # Use first 50 chars of description as title
            description,
            occurrence_date.strftime('%Y-%m-%d %H:%M:%S'),
            detection_date.strftime('%Y-%m-%d %H:%M:%S'),
            resolution_date.strftime('%Y-%m-%d %H:%M:%S') if resolution_date else None,
            random.choice(region_ids),
            unit_id,
            source_ref,
            random.choice(user_ids)
        ))
    
    cursor.executemany("""
        INSERT INTO Event (
            type_id, severity_id, status_id, event_title,
            description, occurrence_date, detection_date, resolution_date,
            region_id, business_unit_id, source_reference, created_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, events)
    
    print(f"Inserted {len(events)} fake events")
    return [event[10] for event in events]  # Return source references

def read_events_from_csv(csv_path):
    """
    Read events from a CSV file and return as a DataFrame
    
    Expected CSV columns:
    - event_title
    - description
    - event_type
    - severity
    - status
    - geographic_region
    - business_unit
    - occurrence_date (optional)
    - source (optional)
    """
    try:
        # Read CSV file
        df = pd.read_csv(csv_path)
        
        # Validate required columns
        required_columns = [
            'event_title', 'description', 'event_type', 
            'severity', 'status', 'geographic_region', 'business_unit'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns in CSV: {missing_columns}")
            
        # Convert dates if present
        if 'occurrence_date' in df.columns:
            df['occurrence_date'] = pd.to_datetime(df['occurrence_date'])
        else:
            df['occurrence_date'] = pd.Timestamp.now()
            
        # Add source if not present
        if 'source' not in df.columns:
            df['source'] = 'CSV Import'
            
        return df
        
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        raise

def insert_csv_events(cursor, csv_path):
    """Insert events from CSV file into the database"""
    
    # Read the CSV file
    df = read_events_from_csv(csv_path)
    
    # Get reference IDs from the database
    cursor.execute("""
        SELECT type_name, type_id 
        FROM EventType
    """)
    type_mapping = dict(cursor.fetchall())
    
    cursor.execute("""
        SELECT severity_name, severity_id 
        FROM EventSeverity
    """)
    severity_mapping = dict(cursor.fetchall())
    
    cursor.execute("""
        SELECT status_name, status_id 
        FROM EventStatus
    """)
    status_mapping = dict(cursor.fetchall())
    
    cursor.execute("""
        SELECT region_name, region_id 
        FROM GeographicRegion
    """)
    region_mapping = dict(cursor.fetchall())
    
    cursor.execute("""
        SELECT unit_name, unit_id 
        FROM BusinessUnit
    """)
    unit_mapping = dict(cursor.fetchall())
    
    # Get a default user for created_by
    cursor.execute("SELECT user_id FROM User WHERE is_active = 1 LIMIT 1")
    default_user_id = cursor.fetchone()[0]
    
    # Prepare events for insertion
    events = []
    errors = []
    
    for idx, row in df.iterrows():
        try:
            # Convert classification to IDs
            type_id = type_mapping.get(row['event_type'])
            severity_id = severity_mapping.get(row['severity'])
            status_id = status_mapping.get(row['status'])
            region_id = region_mapping.get(row['geographic_region'])
            unit_id = unit_mapping.get(row['business_unit'])
            
            # Validate mappings
            if not all([type_id, severity_id, status_id, region_id, unit_id]):
                missing_mappings = []
                if not type_id: missing_mappings.append(f"event_type: {row['event_type']}")
                if not severity_id: missing_mappings.append(f"severity: {row['severity']}")
                if not status_id: missing_mappings.append(f"status: {row['status']}")
                if not region_id: missing_mappings.append(f"geographic_region: {row['geographic_region']}")
                if not unit_id: missing_mappings.append(f"business_unit: {row['business_unit']}")
                
                error_msg = f"Row {idx + 2}: Invalid mappings for {', '.join(missing_mappings)}"
                errors.append(error_msg)
                continue
            
            # Get dates
            occurrence_date = row['occurrence_date']
            detection_date = occurrence_date  # For CSV events, detection is same as occurrence
            
            source_ref = f"EXT-{str(uuid.uuid4())[:8]}"
            
            events.append((
                type_id,
                severity_id,
                status_id,
                row['event_title'],
                row['description'],
                occurrence_date.strftime('%Y-%m-%d %H:%M:%S'),
                detection_date.strftime('%Y-%m-%d %H:%M:%S'),
                None,  # resolution_date
                region_id,
                unit_id,
                source_ref,
                default_user_id
            ))
            
        except Exception as e:
            errors.append(f"Row {idx + 2}: {str(e)}")
    
    # Insert valid events
    if events:
        cursor.executemany("""
            INSERT INTO Event (
                type_id, severity_id, status_id, event_title,
                description, occurrence_date, detection_date, resolution_date,
                region_id, business_unit_id, source_reference, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, events)
        
        print(f"Inserted {len(events)} events from CSV")
    
    # Report any errors
    if errors:
        print("\nErrors encountered during import:")
        for error in errors:
            print(error)
        
    return [event[10] for event in events]  # Return source references

def insert_news_events(cursor, classified_news_df):
    """Insert classified news events into the database"""
    
    # Get reference IDs from the database
    cursor.execute("""
        SELECT type_name, type_id 
        FROM EventType
    """)
    type_mapping = dict(cursor.fetchall())
    
    cursor.execute("""
        SELECT severity_name, severity_id 
        FROM EventSeverity
    """)
    severity_mapping = dict(cursor.fetchall())
    
    cursor.execute("""
        SELECT status_name, status_id 
        FROM EventStatus
    """)
    status_mapping = dict(cursor.fetchall())
    
    cursor.execute("""
        SELECT region_name, region_id 
        FROM GeographicRegion
    """)
    region_mapping = dict(cursor.fetchall())
    
    cursor.execute("""
        SELECT unit_name, unit_id 
        FROM BusinessUnit
    """)
    unit_mapping = dict(cursor.fetchall())
    
    # Get a default user for created_by
    cursor.execute("SELECT user_id FROM User WHERE is_active = 1 LIMIT 1")
    default_user_id = cursor.fetchone()[0]
    
    events = []
    for _, row in classified_news_df.iterrows():
        # Convert classification to IDs
        type_id = type_mapping.get(row['event_type'])
        severity_id = severity_mapping.get(row['severity'])
        status_id = status_mapping.get(row['status'])
        region_id = region_mapping.get(row['geographic_region'])
        unit_id = unit_mapping.get(row['business_unit'])
        
        # Use publication date as occurrence date
        occurrence_date = row['published_at']
        detection_date = occurrence_date  # For news events, detection is same as publication
        
        source_ref = f"NEWS-{str(uuid.uuid4())[:8]}"
        
        events.append((
            type_id,
            severity_id,
            status_id,
            row['event_title'],
            row['description'],
            occurrence_date.strftime('%Y-%m-%d %H:%M:%S'),
            detection_date.strftime('%Y-%m-%d %H:%M:%S'),
            None,  # resolution_date
            region_id,
            unit_id,
            source_ref,
            default_user_id
        ))
    
    cursor.executemany("""
        INSERT INTO Event (
            type_id, severity_id, status_id, event_title,
            description, occurrence_date, detection_date, resolution_date,
            region_id, business_unit_id, source_reference, created_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, events)
    
    print(f"Inserted {len(events)} news events")
    return [event[10] for event in events]  # Return source references

def generate_impact_assessments(cursor, event_refs):
    """Generate impact assessment records"""
    impact_levels = ['none', 'low', 'medium', 'high', 'critical']
    
    cursor.execute("SELECT contract_id FROM ContractHeader")
    contract_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT user_id FROM User WHERE is_active = 1")
    user_ids = [row[0] for row in cursor.fetchall()]
    
    assessments = []
    
    for ref in event_refs:
        cursor.execute("""
            SELECT event_id, occurrence_date 
            FROM Event 
            WHERE source_reference = ?
        """, (ref,))
        event_id, occurrence_date = cursor.fetchone()
        
        if isinstance(occurrence_date, str):
            occurrence_date = datetime.strptime(occurrence_date, '%Y-%m-%d %H:%M:%S')
        
        num_contracts = random.randint(1, 5)
        affected_contracts = random.sample(contract_ids, min(num_contracts, len(contract_ids)))
        
        for contract_id in affected_contracts:
            assessment_date = occurrence_date + timedelta(hours=random.randint(4, 48))
            
            assessments.append((
                event_id,
                contract_id,
                random.choice(impact_levels),
                fake.text(max_nb_chars=200),
                fake.text(max_nb_chars=200),
                assessment_date,
                random.choice(user_ids),
                True
            ))
    
    cursor.executemany("""
        INSERT INTO EventImpactAssessment (
            event_id, contract_id, impact_level,
            impact_description, recommended_actions,
            assessment_date, assessed_by, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, assessments)
    
    print(f"Inserted {len(assessments)} impact assessments")

def generate_notifications(cursor, event_refs):
    """Generate notification records"""
    notification_types = ['Email', 'SMS', 'System', 'Mobile App']
    
    cursor.execute("SELECT user_id FROM User WHERE is_active = 1")
    user_ids = [row[0] for row in cursor.fetchall()]
    
    notifications = []
    
    for ref in event_refs:
        cursor.execute("SELECT event_id FROM Event WHERE source_reference = ?", (ref,))
        event_id = cursor.fetchone()[0]
        
        num_notifications = random.randint(2, 5)
        notified_users = random.sample(user_ids, min(num_notifications, len(user_ids)))
        
        for user_id in notified_users:
            sent_at = datetime.now() - timedelta(days=random.randint(1, 30))
            read_at = sent_at + timedelta(minutes=random.randint(1, 1440)) if random.random() < 0.8 else None
            status = 'read' if read_at else 'sent'
            
            notifications.append((
                event_id,
                user_id,
                random.choice(notification_types),
                status,
                sent_at,
                read_at
            ))
    
    cursor.executemany("""
        INSERT INTO EventNotification (
            event_id, user_id, notification_type,
            notification_status, sent_at, read_at
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, notifications)
    
    print(f"Inserted {len(notifications)} notifications")

def generate_trigger_rules(cursor):
    """Generate event trigger rules"""
    # First, ensure we have automated event types
    cursor.execute("""
        UPDATE EventType 
        SET is_automated = 1 
        WHERE type_id IN (SELECT type_id FROM EventType LIMIT 5)
    """)
    
    cursor.execute("SELECT type_id, type_name FROM EventType WHERE is_automated = 1")
    automated_types = cursor.fetchall()
    
    rules = []
    rule_names = []
    
    for type_id, type_name in automated_types:
        # KPI Threshold Rule
        rule_name = f"KPI_Threshold_{type_name}"
        rule_names.append(rule_name)
        rules.append((
            type_id,
            rule_name,
            json.dumps({
                "type": "kpi_breach",
                "config": {
                    "threshold": "value",
                    "operator": ">=",
                    "duration_months": 3
                }
            }),
            True
        ))
        
        # Meta KPI Rule
        rule_name = f"MetaKPI_{type_name}"
        rule_names.append(rule_name)
        rules.append((
            type_id,
            rule_name,
            json.dumps({
                "type": "meta_kpi",
                "config": {
                    "primary_threshold": "value",
                    "trend_analysis": True,
                    "min_periods": 6
                }
            }),
            True
        ))
    
    cursor.executemany("""
        INSERT INTO EventTriggerRule (
            event_type_id, rule_name, rule_condition, is_active
        ) VALUES (?, ?, ?, ?)
    """, rules)
    
    # Get rule IDs for created rules
    rule_ids = []
    for name in rule_names:
        cursor.execute("SELECT rule_id FROM EventTriggerRule WHERE rule_name = ?", (name,))
        rule_ids.append(cursor.fetchone()[0])
    
    print(f"Inserted {len(rules)} trigger rules")
    return rule_ids

def generate_kpi_trigger_thresholds(cursor, rule_ids):
    """Generate KPI trigger thresholds"""
    cursor.execute("SELECT kpi_id FROM KPIDefinition WHERE is_active = 1")
    kpi_ids = [row[0] for row in cursor.fetchall()]
    
    thresholds = []
    for rule_id in rule_ids:
        # Associate each rule with 1-3 KPIs
        num_kpis = random.randint(1, 3)
        selected_kpis = random.sample(kpi_ids, min(num_kpis, len(kpi_ids)))
        
        for kpi_id in selected_kpis:
            thresholds.append((
                kpi_id,
                rule_id,
                round(random.uniform(50, 95), 2),
                random.choice([">", "<", ">=", "<=", "="]),
                random.randint(1, 12)
            ))
    
    cursor.executemany("""
        INSERT INTO KPITriggerThreshold (
            kpi_id, rule_id, threshold_value,
            comparison_operator, monitoring_period_months
        ) VALUES (?, ?, ?, ?, ?)
    """, thresholds)
    
    print(f"Inserted {len(thresholds)} KPI trigger thresholds")

def generate_meta_kpi_trigger_thresholds(cursor, rule_ids):
    """Generate Meta KPI trigger thresholds"""
    cursor.execute("SELECT meta_kpi_id FROM MetaKPIDefinition WHERE is_active = 1")
    meta_kpi_ids = [row[0] for row in cursor.fetchall()]
    
    thresholds = []
    for rule_id in rule_ids:
        # Associate each rule with 1-2 Meta KPIs
        num_meta_kpis = random.randint(1, 2)
        selected_meta_kpis = random.sample(meta_kpi_ids, min(num_meta_kpis, len(meta_kpi_ids)))
        
        for meta_kpi_id in selected_meta_kpis:
            threshold_config = {
                "primary": {
                    "value": round(random.uniform(80, 95), 2),
                    "operator": random.choice([">", "<", ">=", "<=", "="]),
                    "duration_months": random.randint(1, 6)
                },
                "trend": {
                    "direction": random.choice(["increasing", "decreasing", "stable"]),
                    "min_periods": random.randint(3, 12)
                }
            }
            
            thresholds.append((
                meta_kpi_id,
                rule_id,
                json.dumps(threshold_config),
                True
            ))
    
    cursor.executemany("""
        INSERT INTO MetaKPITriggerThreshold (
            meta_kpi_id, rule_id, threshold_config, is_active
        ) VALUES (?, ?, ?, ?)
    """, thresholds)
    
    print(f"Inserted {len(thresholds)} Meta KPI trigger thresholds")


def main():
    # Connect to the database
    conn = sqlite3.connect('contract_management.db')
    
    try:
        cursor = conn.cursor()
        
        # Insert base data
        try:
            insert_base_data(conn)
        except Exception as e:
            print(f"An error occurred during contract base data creation: {e}")
        
        
        # Generate contracts and related data
        try:
            contracts = generate_contracts(cursor)
            generate_contract_lines(cursor)
            generate_payment_schedules(cursor)
            generate_contract_amendments(cursor)
        except Exception as e:
            print(f"An error occurred during contract transcational data creation: {e}")
        
        
        # Generate KPI related data
        try:
            generate_kpi_categories(cursor)
            generate_kpi_types(cursor)
            generate_kpi_definitions(cursor)
            generate_kpi_measurements(cursor)
        except Exception as e:
            print(f"An error occurred during KPI data creation: {e}")

        # Generate META KPI related data
        try:
            generate_meta_kpi_definitions(cursor)
            generate_meta_kpi_components(cursor)
            generate_meta_kpi_measurements(cursor)
        except Exception as e:
            print(f"An error occurred during meta kpi data creation: {e}")

        # Generate base event data
        try:
            generate_event_categories(cursor)
            generate_event_types(cursor)
            generate_event_severities(cursor)
            generate_event_statuses(cursor)
            generate_geographic_regions(cursor)
            generate_business_units(cursor)
        except Exception as e:
            print(f"An error occurred during base event data creation: {e}")

         # Generate events and related data

        try:
            event_refs = generate_events(cursor)
            generate_impact_assessments(cursor, event_refs)
            generate_notifications(cursor, event_refs)
            event_refs = insert_csv_events(cursor,r"C:\Users\Kish Kukreja\OneDrive\Desktop\agenticai\event_classifications.csv")
            generate_impact_assessments(cursor, event_refs)
            generate_notifications(cursor, event_refs)
            rules = generate_trigger_rules(cursor)
            generate_kpi_trigger_thresholds(cursor, rules)
            generate_meta_kpi_trigger_thresholds(cursor,rules)
        except Exception as e:
            print(f"An error occurred during events transcational data creation: {e}")
        
        conn.commit()
        print("All contract and event data generated successfully!")
        
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()