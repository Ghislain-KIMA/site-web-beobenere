document.addEventListener("DOMContentLoaded", function () {
    var inputs = document.querySelectorAll(".phone-input");

    inputs.forEach(function (input) {
        var iti = window.intlTelInput(input, {
            initialCountry: "bf",
            preferredCountries: ["bf", "ml", "ci", "sn", "ne", "tg", "gh"],
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
