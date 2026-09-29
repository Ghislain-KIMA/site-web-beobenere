from django import forms
from .models import ContactMessage



class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["full_name", "email", "phone", "message"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 5}),
        }

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data.get("email") and not cleaned_data.get("phone"):
            raise forms.ValidationError(
                "Merci de renseigner au moins un moyen de vous répondre : email ou téléphone."
            )

        return cleaned_data
