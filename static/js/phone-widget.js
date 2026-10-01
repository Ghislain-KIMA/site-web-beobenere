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
                if (input.value.trim() !== "") {
                    input.value = iti.getNumber();
                }
            });
        }
    });
});
