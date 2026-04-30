from django import forms

# This is the checkout form — like a paper form but on a website
class CheckoutForm(forms.Form):
    full_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Your full name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'your@email.com'})
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Street, City, Country',
            'rows': 3
        })
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': '+263 77 000 0000'})
    )