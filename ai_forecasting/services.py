from groq import Groq
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from sales.models import SaleItem
from products.models import Product
import json

def calculate_sales_velocity(product, days=30):
    since = timezone.now() - timedelta(days=days)
    total_sold = SaleItem.objects.filter(
        product=product,
        sale__status='completed',
        sale__created_at__gte=since,
    ).aggregate(
        total=__import__('django.db.models', fromlist=['Sum']).Sum('quantity')
    )['total'] or 0
    
    daily_rate = total_sold / days if days > 0 else 0
    
    days_until_stockout = None
    if daily_rate:
        days_until_stockout = product.current_stock / daily_rate
        
    return {
        'total_sold': total_sold,
        'daily_rate': round(daily_rate, 2),
        'days_until_stockout': round(days_until_stockout,1) if days_until_stockout else None,
        'period_days': days,
    }
    
def generate_forecast(product):
    """
    Calls Groq API to generate an AI forecast for a product.
    Returns structured analysis and recommendations.
    """
    velocity = calculate_sales_velocity(product)

    # Build context for the AI
    prompt = f"""
You are an inventory management AI assistant. Analyze this product data and provide recommendations.

Product: {product.name}
SKU: {product.sku}
Current Stock: {product.current_stock} {product.unit}
Minimum Stock Level: {product.minimum_stock} {product.unit}
Maximum Stock Level: {product.maximum_stock} {product.unit}
Unit Price: ${product.unit_price}
Cost Price: ${product.cost_price}

Sales Data (Last 30 Days):
- Total Units Sold: {velocity['total_sold']}
- Average Daily Sales Rate: {velocity['daily_rate']} units/day
- Estimated Days Until Stockout: {velocity['days_until_stockout'] or 'N/A (no recent sales)'}

Please provide:
1. A brief analysis of the stock situation (2-3 sentences)
2. A specific reorder recommendation with quantity
3. Urgency level (high/medium/low)

Respond in this exact JSON format:
{{
    "analysis": "your analysis here",
    "recommendation": "your specific recommendation here",
    "reorder_quantity": <integer or null>,
    "confidence_level": "high|medium|low"
}}
"""

    client = Groq(api_key=settings.GROQ_API_KEY)

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {
                "role": "system",
                "content": "You are an inventory management AI. Always respond with valid JSON only."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=500,
    )

    raw_response = response.choices[0].message.content.strip()

    try:
        data = json.loads(raw_response)
    except json.JSONDecodeError:
        # Fallback if Groq doesn't return valid JSON
        data = {
            "analysis": raw_response,
            "recommendation": "Please review stock levels manually.",
            "reorder_quantity": None,
            "confidence_level": "low"
        }

    return {
        'velocity': velocity,
        'ai_data': data,
    }