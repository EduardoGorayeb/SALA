document.addEventListener('DOMContentLoaded', () => {
    const senhaInput = document.getElementById('senha');
    const confirmarInput = document.getElementById('confirmar-senha');
    const submitBtn = document.getElementById('submitBtn');
    const reqItems = document.querySelectorAll('#passwordReqs .req-item');
    const termosCheckbox = document.getElementById('termos');
    const form = document.getElementById('signupForm');

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
            li.classList.remove('passed', 'failed');
            if (passed) {
                li.classList.add('passed');
            } else if (typing) {
                li.classList.add('failed');
            }
            li.dataset.passed = passed ? '1' : '0';
            if (!passed) ok = false;
        });
        const match = v && confirmarInput.value && v === confirmarInput.value;
        if (confirmarInput.value.length) {
            confirmarInput.style.borderColor = match ? 'rgba(15,157,88,0.6)' : 'rgba(220,38,38,0.6)';
        } else {
            confirmarInput.style.borderColor = '';
        }
        if (termosCheckbox) ok = ok && termosCheckbox.checked;
        submitBtn.disabled = !ok;
    }

    senhaInput.addEventListener('input', validateAll);
    confirmarInput.addEventListener('input', validateAll);
    if (termosCheckbox) termosCheckbox.addEventListener('change', validateAll);

    const EMAILJS_SERVICE = 'service_zk717q9';
    const EMAILJS_TEMPLATE_VERIFY = 'template_pvhj71b';
    const EMAILJS_PUBLIC_KEY = 'XE9PNIyORSCFuvkQG';

    function ensureEmailJSInit() {
        return new Promise(resolve => {
            if (window.emailjs && window.emailjs.init) {
                try { window.emailjs.init(EMAILJS_PUBLIC_KEY); } catch (e) {}
                return resolve(true);
            }
            const url = 'https://cdn.jsdelivr.net/npm/emailjs-com@3/dist/email.min.js';
            let loaded = false;
            const s = document.createElement('script');
            s.src = url;
            s.async = true;
            s.onload = () => {
                loaded = true;
                try { window.emailjs.init(EMAILJS_PUBLIC_KEY); } catch (e) {}
                resolve(true);
            };
            s.onerror = () => {
                resolve(false);
            };
            document.head.appendChild(s);
            setTimeout(() => {
                if (!loaded) resolve(false);
            }, 8000);
        });
    }

    async function sendVerificationEmail() {
        if (!window.CADASTRO_SUCESSO) return;
        if (!window.VERIFY_LINK) return;
        await ensureEmailJSInit();
        if (!window.emailjs || !window.emailjs.send) return;
        const payload = {
            to_name: window.VERIFY_NAME || '',
            to_email: window.VERIFY_EMAIL || '',
            verify_link: window.VERIFY_LINK
        };
        try {
            await window.emailjs.send(EMAILJS_SERVICE, EMAILJS_TEMPLATE_VERIFY, payload);
        } catch (err) {
            Swal.fire({icon: 'error', title: 'Falha ao enviar e-mail', text: 'Não foi possível enviar o e-mail de verificação. Tente reenviar ou aguarde alguns minutos.'});
        }
    }

    async function handleSubmit(e) {
        e.preventDefault();
        submitBtn.disabled = true;
        const csrfInput = form.querySelector('[name="csrfmiddlewaretoken"]');
        const csrf = csrfInput ? csrfInput.value : '';
        const formData = new FormData(form);
        try {
            const res = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrf
                },
                body: formData,
                credentials: 'same-origin'
            });
            const data = await res.json().catch(() => null);
            if (!res.ok) {
                const errors = data && data.errors ? data.errors.join('\n') : 'Erro ao enviar cadastro';
                Swal.fire({icon: 'error', title: 'Erro', text: errors});
                submitBtn.disabled = false;
                return;
            }
            window.CADASTRO_SUCESSO = true;
            window.VERIFY_LINK = data.verify_link || '';
            window.VERIFY_NAME = data.nome || '';
            window.VERIFY_EMAIL = data.email || formData.get('email') || '';
            Swal.fire({icon: 'info', title: 'Cadastro realizado', text: `Enviamos um e-mail para ${window.VERIFY_EMAIL}. É necessário clicar no link enviado para ativar sua conta (válido por 24 horas). Verifique sua caixa de entrada e spam.`});
            sendVerificationEmail();
            form.reset();
            validateAll();
        } catch (err) {
            Swal.fire({icon: 'error', title: 'Erro', text: 'Erro na requisição'});
            submitBtn.disabled = false;
        }
    }

    form.addEventListener('submit', handleSubmit);
    validateAll();
});