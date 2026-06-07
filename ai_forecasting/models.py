from django.db import models

# Create your models here.
class ForecastReport(models.Model):
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE,related_name='forecasts')
    current_stock = models.PositiveIntegerField()
    daily_sales_rate = models.FloatField()
    days_until_stockout = models.FloatField(null=True, blank=True)
    recommended_reorder_quantity = models.PositiveIntegerField(null=True, blank=True)
    ai_analysis = models.TextField()
    ai_recommendation = models.TextField()
    confidence_level = models.CharField(
        max_length=20,
        choices=[
            ('high','High'),
            ('medium','Medium'),
            ('low','Low'),
        ],
        default='medium'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Forecast for {self.product.name} - {self.created_at.date()}"