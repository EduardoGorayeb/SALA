document.addEventListener('DOMContentLoaded', () => {
    const EMAILJS_SERVICE = 'service_zk717q9';
    const EMAILJS_TEMPLATE = 'template_8y9s5du';
    const EMAILJS_PUBLIC_KEY = 'XE9PNIyORSCFuvkQG';

    function ensureEmailJSInit() {
        return new Promise(resolve => {
            if (window.emailjs && window.emailjs.init) {
                try { window.emailjs.init(EMAILJS_PUBLIC_KEY); } catch (e) {}
                return resolve(true);
            }
            const s = document.createElement('script');
            s.src = 'https:
            s.async = true;
            s.onload = () => {
                try { window.emailjs.init(EMAILJS_PUBLIC_KEY); } catch (e) {}
                resolve(true);
            };
            s.onerror = () => resolve(false);
            document.head.appendChild(s);
        });
    }

    async function sendResetEmail() {
        if (!window.RESET_SENT) return;
        if (!window.RESET_LINK) return;
        if (!window.RESET_EMAIL) return;
        await ensureEmailJSInit();
        if (!window.emailjs || !window.emailjs.send) return;

        const payload = {
            to_email: window.RESET_EMAIL,
            reset_link: window.RESET_LINK
        };

        try {
            await window.emailjs.send(EMAILJS_SERVICE, EMAILJS_TEMPLATE, payload);
            Swal.fire({
                icon: 'success',
                title: 'Instruções enviadas!',
                text: 'Enviamos um link para redefinição no seu e-mail.',
                confirmButtonColor: '#0F9D58'
            });
        } catch (err) {
            Swal.fire({
                icon: 'error',
                title: 'Erro ao enviar e-mail',
                text: 'Tente novamente em alguns minutos.',
                confirmButtonColor: '#d33'
            });
        }
    }

    sendResetEmail();
});