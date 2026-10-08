from django import forms
from .models import ContactMessage



class ContactForm(forms.ModelForm):
    # Piège à robots : caché aux humains, il doit rester vide (voir la vue)
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}),
    )

    class Meta:
        model = ContactMessage
        fields = ["full_name", "email", "phone", "message"]
        widgets = {
            "full_name": forms.TextInput(attrs={"autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "phone": forms.TextInput(attrs={"class": "phone-input", "type": "tel", "autocomplete": "tel"}),
            "message": forms.Textarea(attrs={"rows": 5}),
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

        # Un champ invalide est retiré de cleaned_data par Django : on regarde donc aussi
        # ce que le visiteur a tapé, pour ne pas ajouter le message générique à son erreur.
        email_attempted = bool(self.data.get("email", "").strip())
        phone_attempted = bool(self.data.get("phone", "").strip())

        if not email and not phone and not email_attempted and not phone_attempted:
            raise forms.ValidationError(
                "Merci de renseigner au moins un moyen de vous répondre : email ou téléphone."
            )

        return cleaned_data
