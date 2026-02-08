import re
from typing import Optional, Tuple
from datetime import datetime

def validate_query(query: str) -> Tuple[bool, Optional[str]]:
    """Validate user query for safety and relevance"""
    
    # Check for potentially harmful content
    harmful_patterns = [
        r"drop\s+table",
        r"delete\s+from",
        r"update\s+.+\s+set",
        r"insert\s+into",
        r"exec\(|eval\(",
        r"__import__",
        r"os\.system",
        r"subprocess\."
    ]
    
    for pattern in harmful_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            return False, "Query contains potentially harmful content"
    
    # Check for minimum length
    if len(query.strip()) < 2:
        return False, "Query is too short"
    
    # Check for maximum length
    if len(query) > 500:
        return False, "Query is too long (max 500 characters)"
    
    # Check if query is relevant to retail analytics
    retail_keywords = [
        'visitor', 'customer', 'section', 'cashier', 'queue',
        'wait', 'busy', 'traffic', 'heatmap', 'analytics',
        'report', 'prediction', 'forecast', 'compare', 'how many',
        'what is', 'show me', 'tell me', 'analyze'
    ]
    
    query_lower = query.lower()
    has_retail_keyword = any(keyword in query_lower for keyword in retail_keywords)
    
    if not has_retail_keyword:
        return False, "Query doesn't appear to be about retail analytics"
    
    return True, None

def validate_section_name(section: str) -> bool:
    """Validate store section name"""
    if not section or not section.strip():
        return False
    
    # Basic validation - section names should be alphanumeric with spaces
    if not re.match(r'^[a-zA-Z0-9\s\-_]+$', section):
        return False
    
    # Check length
    if len(section) > 50:
        return False
    
    return True

def validate_time_range(start_time: str, end_time: str) -> Tuple[bool, Optional[str]]:
    """Validate time range for queries"""
    try:
        start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        if start > end:
            return False, "Start time must be before end time"
        
        if (end - start).days > 30:
            return False, "Time range cannot exceed 30 days"
        
        return True, None
    except ValueError:
        return False, "Invalid time format"