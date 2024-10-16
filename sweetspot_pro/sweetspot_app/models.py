from django.db import models

class Customer(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    password = models.CharField(max_length=100)
    phone_no = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=6)

    def __str__(self):
        return self.email


class Cake(models.Model):
    name = models.CharField(max_length=100)
    flavour = models.CharField(max_length=50)
    size = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='cakes/')
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class CakeCustomization(models.Model):
    message = models.CharField(max_length=100, blank=True)
    egg_version = models.BooleanField(default=False)
    toppings = models.TextField(blank=True)
    shape = models.CharField(max_length=50, blank=True)
    cake = models.ForeignKey(Cake, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.cake.name} - {self.customer.email}"


class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    cakes = models.ManyToManyField(Cake)
    quantity = models.PositiveIntegerField(default=1)
    customization = models.ForeignKey(CakeCustomization, on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Cart - {self.customer.email}"


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    cake_customization = models.ForeignKey(CakeCustomization, on_delete=models.CASCADE, null=True, blank=True)
    items = models.ManyToManyField(Cake)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_address = models.TextField()
    order_status = models.CharField(max_length=50, default="Pending")
    payment_status = models.CharField(max_length=50, default="Pending")
    payment_method = models.CharField(max_length=50)

    def __str__(self):
        return f"Order - {self.customer.email}"

