from typing import Optional, Dict, List, Any
from datetime import datetime
from langchain.tools import StructuredTool
from api_client import api_client
from utils.formatters import format_visitor_response, format_cashier_response, format_heatmap_response

def get_current_visitors(query: Optional[str] = None) -> str:
    """
    Get the current number of visitors in the store.
    Use when asked about footfall, people count, or how busy the store is.
    """
    try:
        data = api_client.get_current_visitors()
        return format_visitor_response(data)
    except Exception as e:
        return f"❌ Error fetching visitor count: {str(e)}"

def get_section_traffic(query: Optional[str] = None) -> str:
    """
    Get visitor traffic distribution across different store sections.
    Use when asked about crowded areas, popular sections, or traffic distribution.
    """
    try:
        sections = api_client.get_section_traffic()
        if not sections:
            return "📭 No section traffic data available at the moment."
        
        response = "## 📊 Section Traffic Analysis\n\n"
        total_visitors = 0
        
        for i, section in enumerate(sections, 1):
            section_name = section.get('section', 'Unknown')
            visitors = section.get('total_visitors', 0)
            records = section.get('records_count', 0)
            total_visitors += visitors
            
            # Add emoji based on traffic level
            if i == 1:
                emoji = "🔥"
            elif i <= 3:
                emoji = "⚠️"
            else:
                emoji = "📈"
            
            response += f"{emoji} **{section_name}**: {visitors} visitors ({records} records)\n"
        
        # Add summary
        if sections:
            busiest = sections[0]
            busiest_name = busiest.get('section', 'Unknown')
            busiest_count = busiest.get('total_visitors', 0)
            percentage = (busiest_count / total_visitors * 100) if total_visitors > 0 else 0
            
            response += f"\n### 🏆 Summary\n"
            response += f"- **Total tracked visitors**: {total_visitors}\n"
            response += f"- **Busiest section**: {busiest_name} ({percentage:.1f}% of traffic)\n"
            response += f"- **Recommendation**: Consider adding staff to {busiest_name} during peak hours."
        
        return response
    except Exception as e:
        return f"❌ Error fetching section traffic: {str(e)}"

def get_cashier_status(query: Optional[str] = None) -> str:
    """
    Get current cashier queue status and wait time.
    Use when asked about checkout lines, waiting time, or cashier busyness.
    """
    try:
        status = api_client.get_cashier_status()
        return format_cashier_response(status)
    except Exception as e:
        return f"❌ Error fetching cashier status: {str(e)}"

def get_heatmap_data(query: Optional[str] = None) -> str:
    """
    Get store heatmap showing high, medium, and low traffic areas.
    Use when asked about store layout, traffic patterns, or specific area busyness.
    """
    try:
        heatmap_data = api_client.get_heatmap_data()
        return format_heatmap_response(heatmap_data)
    except Exception as e:
        return f"❌ Error fetching heatmap data: {str(e)}"

def get_daily_analytics(query: Optional[str] = None) -> str:
    """
    Get daily store performance metrics including total visitors, busiest section, and peak hours.
    Use for summary reports, performance questions, or daily reviews.
    """
    try:
        analytics = api_client.get_daily_analytics()
        
        if not analytics:
            return "📭 Daily analytics are not available yet."
        
        total_visitors = analytics.get('total_visitors_today', 0)
        busiest_section = analytics.get('busiest_section', 'N/A')
        avg_queue = analytics.get('avg_queue_length', 0)
        peak_hour = analytics.get('peak_hour', 'N/A')
        timestamp = analytics.get('timestamp', datetime.now().isoformat())
        
        # Create performance rating
        if total_visitors > 100:
            performance = "Excellent 🚀"
            suggestion = "Consider extending hours to capture more demand."
        elif total_visitors > 50:
            performance = "Good 👍"
            suggestion = "Normal operations recommended."
        else:
            performance = "Quiet 📉"
            suggestion = "Consider promotions or marketing to increase footfall."
        
        response = f"""## 📈 Daily Performance Report

### 🎯 Key Metrics
- **Total Visitors Today**: {total_visitors} people
- **Performance Rating**: {performance}
- **Busiest Section**: {busiest_section}
- **Average Queue Length**: {avg_queue:.1f} people
- **Peak Hour**: {peak_hour}

### 💡 Insights & Recommendations
{suggestion}

### 📋 Action Items
1. Review staffing for {busiest_section}
2. Monitor cashier queues during {peak_hour}
3. Consider restocking low-traffic sections

*Report generated: {timestamp}*
"""
        return response
    except Exception as e:
        return f"❌ Error fetching daily analytics: {str(e)}"

def get_traffic_forecast(query: Optional[str] = None) -> str:
    """
    Get traffic predictions for the next few hours.
    Use when asked about future busyness, planning, or forecasting.
    """
    try:
        forecast = api_client.get_traffic_forecast()
        
        if not forecast or 'visitors_forecast' not in forecast:
            return "📭 Traffic forecast is not available at the moment."
        
        visitors_pred = forecast.get('visitors_forecast', {})
        queue_pred = forecast.get('queue_forecast', {})
        recommendation = forecast.get('recommendation', 'No specific recommendation')
        
        response = "## 🔮 Traffic Forecast\n\n"
        
        if visitors_pred:
            pred_value = visitors_pred.get('predicted_value', 0)
            confidence = visitors_pred.get('confidence_level', 0) * 100
            horizon = visitors_pred.get('forecast_horizon', 'N/A')
            
            response += f"### 👥 Visitor Prediction ({horizon})\n"
            response += f"- **Expected visitors**: {pred_value:.0f}\n"
            response += f"- **Confidence**: {confidence:.1f}%\n\n"
        
        if queue_pred:
            queue_value = queue_pred.get('predicted_value', 0)
            
            response += f"### ⏳ Queue Prediction\n"
            response += f"- **Expected queue length**: {queue_value:.1f} people\n"
            response += f"- **Estimated wait**: {queue_value * 2:.0f} minutes\n\n"
        
        response += f"### 📋 Recommendation\n{recommendation}\n\n"
        response += "*Note: Predictions are based on historical patterns*"
        
        return response
    except Exception as e:
        return f"❌ Error fetching traffic forecast: {str(e)}"

def compare_sections(section1: str, section2: str) -> str:
    """
    Compare traffic between two specific store sections.
    
    Args:
        section1: First section to compare
        section2: Second section to compare
    """
    try:
        sections = api_client.get_section_traffic()
        
        # Find the requested sections
        sec1_data = next((s for s in sections if s['section'].lower() == section1.lower()), None)
        sec2_data = next((s for s in sections if s['section'].lower() == section2.lower()), None)
        
        if not sec1_data or not sec2_data:
            missing = []
            if not sec1_data:
                missing.append(section1)
            if not sec2_data:
                missing.append(section2)
            return f"❌ Could not find data for: {', '.join(missing)}"
        
        sec1_count = sec1_data.get('total_visitors', 0)
        sec2_count = sec2_data.get('total_visitors', 0)
        total = sec1_count + sec2_count
        
        if total == 0:
            return "Both sections have zero visitors."
        
        response = f"## 📊 Section Comparison: {section1} vs {section2}\n\n"
        response += f"| Metric | {section1} | {section2} |\n"
        response += "|--------|------------|------------|\n"
        response += f"| **Visitors** | {sec1_count} | {sec2_count} |\n"
        response += f"| **Percentage** | {(sec1_count/total*100):.1f}% | {(sec2_count/total*100):.1f}% |\n"
        response += f"| **Records** | {sec1_data.get('records_count', 0)} | {sec2_data.get('records_count', 0)} |\n"
        
        # Add analysis
        if sec1_count > sec2_count:
            diff = sec1_count - sec2_count
            response += f"\n### 📈 Analysis\n"
            response += f"**{section1}** has {diff} more visitors than **{section2}**.\n"
            response += "Consider analyzing product placement or promotions in the lower-traffic section."
        elif sec2_count > sec1_count:
            diff = sec2_count - sec1_count
            response += f"\n### 📈 Analysis\n"
            response += f"**{section2}** has {diff} more visitors than **{section1}**.\n"
            response += "The higher traffic in this section suggests better product visibility or placement."
        else:
            response += "\n### 📊 Analysis\nBoth sections have equal visitor traffic."
        
        return response
    except Exception as e:
        return f"❌ Error comparing sections: {str(e)}"

# Create LangChain tools
tools = [
    StructuredTool.from_function(
        func=get_current_visitors,
        name="CurrentVisitorCount",
        description="Get current number of visitors in store. Use for footfall queries."
    ),
    StructuredTool.from_function(
        func=get_section_traffic,
        name="SectionTrafficAnalysis",
        description="Analyze visitor distribution across store sections. Use for crowded area queries."
    ),
    StructuredTool.from_function(
        func=get_cashier_status,
        name="CashierQueueStatus",
        description="Get cashier queue length and wait time. Use for checkout queries."
    ),
    StructuredTool.from_function(
        func=get_heatmap_data,
        name="StoreHeatmap",
        description="Get visual heatmap of store traffic. Use for layout analysis."
    ),
    StructuredTool.from_function(
        func=get_daily_analytics,
        name="DailyPerformanceReport",
        description="Get comprehensive daily store metrics. Use for summary reports."
    ),
    StructuredTool.from_function(
        func=get_traffic_forecast,
        name="TrafficForecast",
        description="Get predictions for future store traffic. Use for planning."
    ),
    StructuredTool.from_function(
        func=compare_sections,
        name="CompareSections",
        description="Compare traffic between two store sections. Use for section analysis."
    )
]