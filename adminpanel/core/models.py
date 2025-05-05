from django.db import models

class User(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=150)
    email = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    initial_balance = models.FloatField(default=10000.0)
    # ...otros campos

    class Meta:
        managed = False  # ¡Importante! Así Django no intentará crear/modificar la tabla
        db_table = 'users'

class Stock(models.Model):
    id = models.IntegerField(primary_key=True)
    symbol = models.CharField(max_length=50)
    name = models.CharField(max_length=150)
    current_price = models.FloatField()
    sector_id = models.IntegerField()
    # ...otros campos

    class Meta:
        managed = False
        db_table = 'stocks'

class Transaction(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField()
    stock_id = models.IntegerField()
    quantity = models.IntegerField()
    price = models.FloatField()
    timestamp = models.DateTimeField()
    # ...otros campos

    class Meta:
        managed = False
        db_table = 'transactions'

class Sector(models.Model):
    id = models.IntegerField(primary_key=True)
    sector_name = models.CharField(max_length=150)
    # ...otros campos

    class Meta:
        managed = False
        db_table = 'sectors'