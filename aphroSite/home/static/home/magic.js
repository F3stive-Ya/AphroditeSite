(function () {
    const form = document.querySelector('.magic-form[data-static-mode="true"]');
    if (!form) {
        return;
    }

    const configElement = document.getElementById('cipher-config');
    let config = {
        secretKey: 'aphrodite',
        greekGlyphs: 'αβγδεζηθικλμνξοπρστυφχψω',
    };
    if (configElement) {
        try {
            config = JSON.parse(configElement.textContent);
        } catch (_err) {
            // Fall back to default cipher config.
        }
    }

    const SECRET_KEY = config.secretKey || 'aphrodite';
    const GREEK_GLYPHS = Array.from(config.greekGlyphs || 'αβγδεζηθικλμνξοπρστυφχψω');

    function randomGlyph() {
        if (window.crypto && window.crypto.getRandomValues) {
            const limit = Math.floor(0x100000000 / GREEK_GLYPHS.length) * GREEK_GLYPHS.length;
            const buf = new Uint32Array(1);
            let value;
            do {
                window.crypto.getRandomValues(buf);
                value = buf[0];
            } while (value >= limit);
            return GREEK_GLYPHS[value % GREEK_GLYPHS.length];
        }
        return GREEK_GLYPHS[Math.floor(Math.random() * GREEK_GLYPHS.length)];
    }

    function encryptTrueThoughts(plaintext) {
        const lower = plaintext.toLowerCase();
        if (lower === 'athena') {
            return { ciphertext: plaintext, decoyGreek: 'Ἀθηνᾶ' };
        }
        if (lower === 'artemis') {
            return { ciphertext: plaintext, decoyGreek: 'Ἄρτεμις' };
        }
        if (lower === 'hestia') {
            return { ciphertext: plaintext, decoyGreek: 'Ἑστία' };
        }

        const ciphertextChars = [];
        let letterIndex = 0;

        for (const character of plaintext) {
            if (/^[A-Za-z]$/.test(character)) {
                const plainValue = character.toLowerCase().charCodeAt(0) - 97;
                const keyCharacter = SECRET_KEY[letterIndex % SECRET_KEY.length];
                const keyValue = keyCharacter.charCodeAt(0) - 97;
                const encryptedValue = (plainValue + keyValue) % 26;
                let encryptedCharacter = String.fromCharCode(encryptedValue + 97);
                if (character >= 'A' && character <= 'Z') {
                    encryptedCharacter = encryptedCharacter.toUpperCase();
                }
                ciphertextChars.push(encryptedCharacter);
                letterIndex += 1;
            } else {
                ciphertextChars.push(character);
            }
        }

        let decoyGreek = '';
        for (let i = 0; i < letterIndex; i += 1) {
            decoyGreek += randomGlyph();
        }

        return {
            ciphertext: ciphertextChars.join(''),
            decoyGreek: decoyGreek,
        };
    }

    function createKeyDust() {
        const dust = document.createElement('span');
        dust.className = 'key-dust';
        dust.setAttribute('aria-hidden', 'true');
        for (let i = 0; i < 6; i += 1) {
            dust.appendChild(document.createElement('span'));
        }
        return dust;
    }

    function renderResult(submittedThoughts, result) {
        const workbench = form.closest('.magic-workbench');
        if (!workbench) {
            return;
        }

        const section = document.createElement('section');
        section.className = 'cipher-output';
        section.setAttribute('aria-live', 'polite');
        section.setAttribute('aria-label', 'Cipher results');

        const step1 = document.createElement('div');
        step1.className = 'cipher-output-step';
        const eyebrow1 = document.createElement('p');
        eyebrow1.className = 'eyebrow';
        eyebrow1.textContent = '01 / PLAINTEXT';
        const heading1 = document.createElement('h2');
        heading1.textContent = 'Your thoughts';
        const pre1 = document.createElement('pre');
        pre1.className = 'cipher-plaintext';
        pre1.textContent = submittedThoughts;
        step1.append(eyebrow1, heading1, pre1);

        const step2 = document.createElement('div');
        step2.className = 'cipher-output-step';
        const eyebrow2 = document.createElement('p');
        eyebrow2.className = 'eyebrow';
        eyebrow2.textContent = '02 / ANCIENT GREEK';
        const heading2 = document.createElement('h2');
        heading2.textContent = 'Veiled key';
        const keyWrap = document.createElement('div');
        keyWrap.className = 'cipher-key-wrap';
        const pre2 = document.createElement('pre');
        pre2.className = 'cipher-key';
        const keyLetters = document.createElement('span');
        keyLetters.className = 'cipher-key-letters';
        keyLetters.textContent = result.decoyGreek;
        keyLetters.appendChild(createKeyDust());
        pre2.appendChild(keyLetters);
        keyWrap.appendChild(pre2);
        step2.append(eyebrow2, heading2, keyWrap);

        const step3 = document.createElement('div');
        step3.className = 'cipher-output-step';
        const eyebrow3 = document.createElement('p');
        eyebrow3.className = 'eyebrow';
        eyebrow3.textContent = '03 / CIPHERTEXT';
        const heading3 = document.createElement('h2');
        heading3.textContent = '"Your thoughts"';
        const pre3 = document.createElement('pre');
        pre3.className = 'cipher-text';
        const textLetters = document.createElement('span');
        textLetters.className = 'cipher-text-letters';
        textLetters.textContent = result.ciphertext;
        textLetters.appendChild(createKeyDust());
        pre3.appendChild(textLetters);
        step3.append(eyebrow3, heading3, pre3);

        section.append(step1, step2, step3);

        const existingOutput = workbench.querySelector('.cipher-output, .cipher-placeholder');
        if (existingOutput) {
            existingOutput.replaceWith(section);
        } else {
            workbench.appendChild(section);
        }
    }

    function showError(field, message) {
        let errorEl = field.querySelector('.form-error');
        if (!message) {
            if (errorEl) {
                errorEl.remove();
            }
            return;
        }
        if (!errorEl) {
            errorEl = document.createElement('p');
            errorEl.className = 'form-error';
            errorEl.setAttribute('role', 'alert');
            field.appendChild(errorEl);
        }
        errorEl.textContent = message;
    }

    form.addEventListener('submit', function (event) {
        event.preventDefault();
        const textarea = form.querySelector('textarea[name="thoughts"]');
        const field = form.querySelector('.magic-field');
        if (!textarea || !field) {
            return;
        }

        const thoughts = textarea.value;
        if (thoughts.length === 0) {
            showError(field, 'This field is required.');
            return;
        }
        if (thoughts.length > 4000) {
            showError(field, `Ensure this value has at most 4000 characters (it has ${thoughts.length}).`);
            return;
        }

        showError(field, '');
        const result = encryptTrueThoughts(thoughts);
        renderResult(thoughts, result);
    });
})();

