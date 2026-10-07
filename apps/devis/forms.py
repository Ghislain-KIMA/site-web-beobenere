from django import forms
from .models import Devis



class DevisForm(forms.ModelForm):
    class Meta:
        model = Devis
        fields = ["full_name", "email", "phone", "service", "message", "timeline"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 5}),
            "phone": forms.TextInput(attrs={"class": "phone-input"}),
        }

    def clean_full_name(self):
        # Ramène tous les blancs (retours à la ligne, tabulations, espaces multiples) à un seul espace
        full_name = " ".join(self.cleaned_data["full_name"].split())
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

