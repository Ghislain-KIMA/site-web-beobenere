from django import forms
from .models import ContactMessage



class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["full_name", "email", "phone", "message"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 5}),
            "phone": forms.TextInput(attrs={"class": "phone-input"}),
        }

    def clean_full_name(self):
        full_name = self.cleaned_data["full_name"].strip()
        if len(full_name) < 2 or full_name.isdigit():
            raise forms.ValidationError("Merci d'indiquer un nom valide.")
        return full_name

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        phone = cleaned_data.get("phone")

        phone_attempted = bool(self.data.get("phone", "").strip())

        if not email and not phone and not phone_attempted:
            raise forms.ValidationError(
                "Merci de renseigner au moins un moyen de vous répondre : email ou téléphone."
            )

        return cleaned_data
