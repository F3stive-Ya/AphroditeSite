from django import forms


class GirdleForm(forms.Form):
    thoughts = forms.CharField(
        label='Your true thoughts',
        max_length=4000,
        strip=False,
        widget=forms.Textarea(attrs={
            'rows': 5,
            'placeholder': 'Write your true thoughts here...',
            'autocomplete': 'off',
            'maxlength': '4000',
        }),
    )