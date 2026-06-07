from django.db import models

# Create your models here.
class DailySalesReport(models.Model):
    date = models.DateField(unique=True)
    total_sales = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_items_sold = models.PositiveIntegerField(default=0)
    top_product = models.ForeignKey("products.Product", on_delete=models.SET_NULL, null=True,blank=True, related_name='top_sales_day')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        
    def __str__(self):
        return f"Report {self.date} - {self.total_sales} sales"
    