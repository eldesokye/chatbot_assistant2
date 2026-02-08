from typing import Dict, List, Any
from datetime import datetime

def format_visitor_response(data: Dict) -> str:
    """Format visitor count response"""
    if not data or 'current_visitors' not in data:
        return "📭 Current visitor data is unavailable."
    
    count = data.get('current_visitors', 0)
    timestamp = data.get('timestamp', datetime.now().isoformat())
    
    # Contextual messages
    if count == 0:
        context = "The store is currently empty. Perfect time for restocking! 🛒"
        emoji = "🕳️"
    elif count < 10:
        context = "It's very quiet. Consider running a promotion? 📢"
        emoji = "😴"
    elif count < 30:
        context = "Moderate activity. Normal operations recommended. 👍"
        emoji = "😊"
    elif count < 50:
        context = "Busy! Ensure staff are adequately distributed. 👥"
        emoji = "🔥"
    else:
        context = "Very busy! Consider opening additional cashiers. ⚡"
        emoji = "🚀"
    
    return f"""## {emoji} Current Store Status

**Visitors in store**: {count} people

**Analysis**: {context}

*Last updated: {timestamp}*
"""

def format_cashier_response(data: Dict) -> str:
    """Format cashier status response"""
    if not data or 'queue_length' not in data:
        return "💳 Cashier status data is currently unavailable."
    
    queue_length = data.get('queue_length', 0)
    status = data.get('status', 'unknown').title()
    wait_time = data.get('wait_time_minutes', queue_length * 2)
    timestamp = data.get('timestamp', datetime.now().isoformat())
    
    # Recommendations based on queue
    if queue_length == 0:
        recommendation = "✅ Perfect time for customers to checkout!"
        action = "No action needed."
        emoji = "✅"
    elif queue_length <= 2:
        recommendation = "✅ Good checkout conditions."
        action = "Monitor but no immediate action required."
        emoji = "👍"
    elif queue_length <= 5:
        recommendation = "⚠️ Moderate wait expected."
        action = "Consider preparing an additional cashier."
        emoji = "⚠️"
    elif queue_length <= 8:
        recommendation = "🚨 Long queue forming."
        action = "Open additional cashier immediately."
        emoji = "🚨"
    else:
        recommendation = "🔥 Critical queue length!"
        action = "Open all available cashiers and inform management."
        emoji = "🔥"
    
    return f"""## {emoji} Cashier Status

**Queue Length**: {queue_length} people
**Status**: {status}
**Estimated Wait**: {wait_time} minutes

**Recommendation**: {recommendation}
**Action Required**: {action}

*Last updated: {timestamp}*
"""

def format_heatmap_response(data: List[Dict]) -> str:
    """Format heatmap data response"""
    if not data:
        return "🌡️ No heatmap data available at the moment."
    
    # Categorize by density
    high_traffic = []
    medium_traffic = []
    low_traffic = []
    
    for area in data:
        section = area.get('section', 'Unknown')
        density = area.get('density_level', 'low')
        
        if density == 'high':
            high_traffic.append(section)
        elif density == 'medium':
            medium_traffic.append(section)
        else:
            low_traffic.append(section)
    
    response = "## 🗺️ Store Heatmap Analysis\n\n"
    
    if high_traffic:
        response += "### 🔥 High Traffic Areas\n"
        response += "Consider adding staff or optimizing layout:\n"
        for section in high_traffic:
            response += f"- **{section}**\n"
        response += "\n"
    
    if medium_traffic:
        response += "### ⚠️ Medium Traffic Areas\n"
        response += "Normal operations, monitor for changes:\n"
        for section in medium_traffic:
            response += f"- **{section}**\n"
        response += "\n"
    
    if low_traffic:
        response += "### ✅ Low Traffic Areas\n"
        response += "Opportunities for improvement:\n"
        for section in low_traffic:
            response += f"- **{section}** (consider promotions or relocation)\n"
        response += "\n"
    
    # Add summary
    total_areas = len(high_traffic) + len(medium_traffic) + len(low_traffic)
    response += f"### 📊 Summary\n"
    response += f"- **Total monitored areas**: {total_areas}\n"
    response += f"- **High traffic**: {len(high_traffic)} areas\n"
    response += f"- **Medium traffic**: {len(medium_traffic)} areas\n"
    response += f"- **Low traffic**: {len(low_traffic)} areas\n"
    
    return response