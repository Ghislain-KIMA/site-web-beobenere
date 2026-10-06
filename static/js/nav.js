document.addEventListener('DOMContentLoaded', function () {
    var toggle = document.getElementById('nav-toggle');
    var nav = document.getElementById('site-nav');

    if (!toggle || !nav) {
        return;
    }

    // Ouvre ou ferme le menu, et garde le bouton hamburger synchronisé
    // (croix, aria-expanded pour les lecteurs d'écran, libellé du bouton).
    function setMenuOpen(isOpen) {
        nav.classList.toggle('is-open', isOpen);
        toggle.classList.toggle('is-active', isOpen);
        toggle.setAttribute('aria-expanded', isOpen);
        toggle.setAttribute('aria-label', isOpen ? 'Fermer le menu' : 'Ouvrir le menu');
    }

    toggle.addEventListener('click', function () {
        setMenuOpen(!nav.classList.contains('is-open'));
    });

    // Un clic n'importe où en dehors du menu et du bouton referme le menu.
    document.addEventListener('click', function (event) {
        if (!nav.classList.contains('is-open')) {
            return;
        }
        if (nav.contains(event.target) || toggle.contains(event.target)) {
            return;
        }
        setMenuOpen(false);
    });

    // La touche Échap referme aussi le menu, et rend le focus au bouton hamburger.
    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape' && nav.classList.contains('is-open')) {
            setMenuOpen(false);
            toggle.focus();
        }
    });
});

function setHeaderHeightVar() {
    var header = document.querySelector(".site-header");
    if (header) {
        document.documentElement.style.setProperty("--header-height", header.offsetHeight + "px");
    }
}

function scrollToAnchorBelowHeader() {
    if (!window.location.hash) {
        return;
    }
    var target = document.querySelector(window.location.hash);
    var header = document.querySelector(".site-header");
    if (!target || !header) {
        return;
    }
    var headerHeight = header.offsetHeight;
    var targetTop = target.getBoundingClientRect().top + window.pageYOffset;
    window.scrollTo({ top: targetTop - headerHeight - 20, behavior: "auto" });
}

function positionForAnchor() {
    setHeaderHeightVar();
    scrollToAnchorBelowHeader();
}

// Attend que le navigateur ait vraiment fini d'afficher la page, deux images d'affichage
// de suite, avant de mesurer et de se positionner. Plus fiable que d'écouter un seul
// évènement précis, qui ne se comporte pas pareil selon le navigateur.
function positionForAnchorWhenStable() {
    requestAnimationFrame(function () {
        requestAnimationFrame(positionForAnchor);
    });
}

setHeaderHeightVar();
window.addEventListener("load", positionForAnchorWhenStable);
window.addEventListener("resize", setHeaderHeightVar);

if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(positionForAnchorWhenStable);
}
