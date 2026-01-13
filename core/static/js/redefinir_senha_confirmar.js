document.addEventListener('DOMContentLoaded', () => {
    const senhaInput = document.getElementById('senha');
    const confirmarInput = document.getElementById('confirmar-senha');
    const submitBtn = document.getElementById('submitBtn');
    const reqItems = document.querySelectorAll('#passwordReqs .req-item');

    const checks = {
        length: v => v.length >= 8,
        uppercase: v => /[A-ZÀ-Ý]/.test(v),
        number: v => /[0-9]/.test(v),
        special: v => /[!@#$%^&*(),.?":{}|<>_\-\\\/\[\];'`~+=]/.test(v)
    };

    function validateAll() {
        const v = senhaInput.value || '';
        let ok = true;

        reqItems.forEach(li => {
            const key = li.getAttribute('data-check');
            const passed = checks[key] ? checks[key](v) : false;
            const typing = v.length > 0;

            li.classList.toggle('passed', passed);
            li.classList.toggle('failed', typing && !passed);
            li.dataset.passed = passed ? '1' : '0';

            if (!passed) ok = false;
        });

        const match = v && confirmarInput.value && (v === confirmarInput.value);

        if (confirmarInput.value.length) {
            confirmarInput.style.borderColor = match ? 'rgba(15,157,88,0.6)' : 'rgba(220,38,38,0.6)';
        } else {
            confirmarInput.style.borderColor = '';
        }

        if (!match) ok = false;

        submitBtn.disabled = !ok;
    }

    senhaInput.addEventListener('input', validateAll);
    confirmarInput.addEventListener('input', validateAll);
    validateAll();
});