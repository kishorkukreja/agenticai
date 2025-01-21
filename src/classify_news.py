import pandas as pd
from typing import List, Dict
from pydantic import BaseModel, Field
from enum import Enum
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

# Enum definitions
class EventCategory(str, Enum):
    SUPPLIER_ISSUE = "Supplier Issue"
    QUALITY_INCIDENT = "Quality Incident"
    COMPLIANCE_BREACH = "Compliance Breach"
    MARKET_EVENT = "Market Event"
    RESOURCE_SHORTAGE = "Resource Shortage"
    NATURAL_DISASTER = "Natural Disaster"
    SECURITY_INCIDENT = "Security Incident"
    FINANCIAL_EVENT = "Financial Event"
    OPERATIONAL_ISSUE = "Operational Issue"
    REGULATORY_CHANGE = "Regulatory Change"

class EventType(str, Enum):
    LATE_DELIVERY = "Late Delivery"
    QUALITY_DEFECT = "Quality Defect"
    PRODUCTION_DEFECT = "Production Defect"
    SERVICE_QUALITY = "Service Quality"
    POLICY_VIOLATION = "Policy Violation"
    REGULATORY_NONCOMPLIANCE = "Regulatory Non-compliance"
    PRICE_FLUCTUATION = "Price Fluctuation"
    SUPPLY_CHAIN_DISRUPTION = "Supply Chain Disruption"
    STAFF_SHORTAGE = "Staff Shortage"
    MATERIAL_SHORTAGE = "Material Shortage"

class Severity(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    NEGLIGIBLE = "Negligible"

class Status(str, Enum):
    NEW = "New"
    UNDER_INVESTIGATION = "Under Investigation"
    ACTION_REQUIRED = "Action Required"
    IN_PROGRESS = "In Progress"
    MONITORING = "Monitoring"
    RESOLVED = "Resolved"
    CLOSED = "Closed"

class GeographicRegion(str, Enum):
    GLOBAL = "Global Operations"
    NORTH_AMERICA = "North America"
    EUROPE = "Europe"
    ASIA_PACIFIC = "Asia Pacific"
    UNITED_STATES = "United States"
    CANADA = "Canada"
    UK = "United Kingdom"
    GERMANY = "Germany"
    JAPAN = "Japan"
    CHINA = "China"

class BusinessUnit(str, Enum):
    GLOBAL_OPS = "Global Operations"
    MANUFACTURING = "Manufacturing"
    SALES_DISTRIBUTION = "Sales & Distribution"
    RESEARCH_DEVELOPMENT = "Research & Development"
    PRODUCTION = "Production"
    QUALITY_CONTROL = "Quality Control"
    SUPPLY_CHAIN = "Supply Chain"
    NA_SALES = "North America Sales"
    EU_SALES = "Europe Sales"
    APAC_SALES = "Asia Pacific Sales"
    PRODUCT_DEV = "Product Development"
    INNOVATION_LAB = "Innovation Lab"
    TECH_SERVICES = "Technical Services"

# Pydantic model for classification
class EventClassification(BaseModel):
    category: EventCategory
    event_type: EventType
    severity: Severity
    status: Status
    geographic_region: GeographicRegion
    business_unit: BusinessUnit
    confidence_score: float 
    explanation: str

# Create prompt template
classification_prompt = ChatPromptTemplate.from_template(
"""Analyze the following news article and classify it according to our event classification system. Consider the content carefully and provide classifications with explanations.

Article Title: {title}
Article Description: {description}
Source: {source}
Published Date: {published_at}

Please classify this event according to the following criteria:
1. Event Category: Based on whether it's internal/external and its primary impact
2. Event Type: The specific nature of the event
3. Severity: Impact level on operations and stakeholders
4. Status: Current state of the event
5. Geographic Region: Primary region affected
6. Business Unit: Primary business unit impacted

Provide a confidence score (0-1) for your classification and a brief explanation of your reasoning.

Only return the properties defined in the EventClassification model."""
)

async def classify_event_async(event_data: Dict, llm) -> EventClassification:
    """Classify a single event asynchronously"""
    prompt = classification_prompt.invoke({
        "title": event_data["title"],
        "description": event_data["description"],
        "source": event_data["source"],
        "published_at": event_data["published_at"]
    })
    return await llm.ainvoke(prompt)

async def process_events(events: List[Dict]) -> pd.DataFrame:
    """Process multiple events and return a DataFrame"""
    # Initialize LLM
    
    llm = ChatOpenAI(temperature=0, model="gpt-4o-mini").with_structured_output(EventClassification)
    
    # Process events concurrently
    tasks = [classify_event_async(event, llm) for event in events]
    classifications = await asyncio.gather(*tasks)
    
    # Create DataFrame
    df_data = []
    for event, classification in zip(events, classifications):
        row = {
            'event_title': event['title'],
            'description':event['description'],
            'event_source': event['source'],
            'published_at': datetime.fromisoformat(event['published_at'].replace('Z', '+00:00')),
            'category': classification.category.value,
            'event_type': classification.event_type.value,
            'severity': classification.severity.value,
            'status': classification.status.value,
            'geographic_region': classification.geographic_region.value,
            'business_unit': classification.business_unit.value,
            'confidence_score': classification.confidence_score,
            'explanation': classification.explanation,
            'url': event['url']
        }
        df_data.append(row)
    
    # Create DataFrame and set index
    df = pd.DataFrame(df_data)
    df['published_at'] = pd.to_datetime(df['published_at'])
    df = df.sort_values('published_at', ascending=False)
    
    return df

# Load the .env file
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please add it to your .env file.")
    

# Example usage
async def main(events):
    df = await process_events(events)
    return df

# Run the processing
import json

# Sample events data
events = [
    {
        "title": "Aprio Wealth Management LLC Boosts Holdings in Duke Energy Co. (NYSE:DUK)",
        "description": "Aprio Wealth Management LLC grew its holdings in Duke Energy Co. (NYSE:DUK – Free Report) by 62.0% during the 4th quarter...",
        "source": "ETF Daily News",
        "published_at": "2025-01-14T12:23:04Z",
        "url": "https://www.etfdailynews.com/2025/01/14/aprio-wealth-management-llc-boosts-holdings-in-duke-energy-co-nyseduk/"
    },
    {
        "title": "Matrix Trust Co Makes New Investment in Moody's Co. (NYSE:MCO)",
        "description": "Matrix Trust Co purchased a new stake in Moody's Co. (NYSE:MCO – Free Report) in the 4th quarter...",
        "source": "ETF Daily News",
        "published_at": "2025-01-14T12:22:59Z",
        "url": "https://www.etfdailynews.com/2025/01/14/matrix-trust-co-makes-new-investment-in-moodys-co-nysemco/"
    }
]

# Process events and create DataFrame
df = asyncio.run(main(events))

# Display the results
print("\nEvent Classification Results:")
print(df.to_string())

# Save to CSV (optional)
df.to_csv('event_classifications.csv', index=False)