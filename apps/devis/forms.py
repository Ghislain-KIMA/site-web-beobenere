from django import forms
from .models import Devis



class DevisForm(forms.ModelForm):
    class Meta:
        model = Devis
        fields = ["full_name", "email", "phone", "service", "message", "timeline"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 5}),
        }

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        phone = cleaned_data.get("phone")

        if not email and not phone:
            raise forms.ValidationError(
                "Merci de renseigner au moins un moyen de vous contacter : email ou téléphone."
            )

        return cleaned_data
