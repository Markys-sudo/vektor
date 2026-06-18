from django import forms

PAYMENT_CHOICES = [
    ("debit", "Debit Card"),
    ("wallet", "Digital Wallet"),
    ("cod", "Cash On Delivery"),
]


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=255, label="Full Name")
    phone = forms.CharField(max_length=40, label="Phone number")
    city = forms.CharField(max_length=120, label="City")
    address = forms.CharField(widget=forms.Textarea, label="Shipping address")
    payment_method = forms.ChoiceField(choices=PAYMENT_CHOICES, initial="debit")
