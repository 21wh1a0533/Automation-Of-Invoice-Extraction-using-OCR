from django.db import models


class User(models.Model):
    full_name = models.CharField(max_length=100, verbose_name="User Name")
    email = models.EmailField(verbose_name="Email")
    password = models.CharField(max_length=128, verbose_name="Password")
    phone_number = models.CharField(max_length=15, verbose_name="Phone Number")
    age =models.CharField(max_length=15, verbose_name="age")
    address = models.TextField(verbose_name="Address")
    photo = models.ImageField(upload_to='profiles/', verbose_name="Upload Profile", null=True, blank=True)
    otp = models.CharField(max_length=6, default='000000', help_text='Enter OTP for verification')
    otp_status = models.CharField(max_length=15, default='Not Verified', help_text='OTP status')
    status = models.CharField(max_length=15,default='Accepted')

    def __str__(self):
        return self.full_name




class Invoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    pdf_file = models.FileField(upload_to='invoices/')
    extracted_text = models.TextField()
    date_uploaded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice {self.id} for {self.user.full_name}"


class Conversation(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='conversations')
    question = models.TextField()
    answer = models.TextField()
    date_asked = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.id} for Invoice {self.invoice.id}"


class InvoiceProduct(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='products')
    product_name = models.CharField(max_length=255)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    taxable_value = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} for Invoice {self.invoice.id}"
