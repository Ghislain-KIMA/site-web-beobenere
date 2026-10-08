// Textes du sélecteur de pays en français. Les noms des pays sont fournis par le
// navigateur lui-même (Intl.DisplayNames) : aucun fichier de traduction à télécharger.
// Si le navigateur est trop ancien, les noms restent en anglais, sans erreur.
function frenchI18n() {
    var i18n = {
        searchPlaceholder: "Rechercher un pays",
        zeroSearchResults: "Aucun résultat",
        oneSearchResult: "1 résultat",
        multipleSearchResults: "${count} résultats",
        selectedCountryAriaLabel: "Pays sélectionné",
        noCountrySelected: "Aucun pays sélectionné",
        countryListAriaLabel: "Liste des pays"
    };
    if (window.Intl && Intl.DisplayNames) {
        var names = new Intl.DisplayNames(["fr"], { type: "region" });
        window.intlTelInput.getCountryData().forEach(function (country) {
            i18n[country.iso2] = names.of(country.iso2.toUpperCase());
        });
    }
    return i18n;
}


document.addEventListener("DOMContentLoaded", function () {
    var inputs = document.querySelectorAll(".phone-input");

    inputs.forEach(function (input) {
        var iti = window.intlTelInput(input, {
            initialCountry: "bf",
            countryOrder: ["bf", "ml", "ci", "sn", "ne", "tg", "gh"],
            i18n: frenchI18n(),
            loadUtils: function () {
                return import("/static/vendor/intl-tel-input/js/utils.min.js");
            }
        });

        var form = input.closest("form");
        if (form) {
            form.addEventListener("submit", function () {
                // getNumber() renvoie "" tant que utils.min.js n'est pas chargé
                // (connexion lente, échec du chargement) : on garde alors le numéro
                // tel que tapé, que Django sait lire grâce à PHONENUMBER_DEFAULT_REGION.
                var fullNumber = iti.getNumber();
                if (fullNumber) {
                    input.value = fullNumber;
                }
            });
        }
    });
});
