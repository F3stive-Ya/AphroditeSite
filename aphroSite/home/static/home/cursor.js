(function () {
    function setClicking(isClicking) {
        document.documentElement.classList.toggle('is-clicking', isClicking);
    }

    function clearClicking() {
        setClicking(false);
    }

    window.addEventListener('pointerdown', function (event) {
        if (event.pointerType === 'mouse') {
            setClicking(event.buttons !== 0);
        }
    }, true);

    window.addEventListener('pointerup', function (event) {
        if (event.pointerType === 'mouse') {
            setClicking(event.buttons !== 0);
        }
    }, true);

    window.addEventListener('pointercancel', function (event) {
        if (event.pointerType === 'mouse') {
            clearClicking();
        }
    }, true);

    window.addEventListener('blur', clearClicking);
    document.addEventListener('visibilitychange', function () {
        if (document.hidden) {
            clearClicking();
        }
    });
})();
