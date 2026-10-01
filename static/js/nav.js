document.addEventListener('DOMContentLoaded', function () {
    var toggle = document.getElementById('nav-toggle');
    var nav = document.getElementById('site-nav');

    if (toggle && nav) {
        toggle.addEventListener('click', function () {
            var isOpen = nav.classList.toggle('is-open');
            toggle.classList.toggle('is-active', isOpen);
            toggle.setAttribute('aria-expanded', isOpen);
        });
    }
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
