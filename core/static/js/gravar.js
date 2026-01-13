document.addEventListener("DOMContentLoaded", () => {
    const iniciarBtn = document.getElementById("btn-iniciar");
    const pararBtn = document.getElementById("btn-parar");
    const voltarBtn = document.getElementById("btn-voltar");
    const videoContainer = document.getElementById("tela-gravacao");
    const timerDisplay = document.getElementById("timer");
    const temaInput = document.getElementById("tema-gravacao");
    const tipoSelect = document.getElementById("tipo-apresentacao");
    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

    const loader = document.getElementById("loader-sala");
    const loaderTitle = document.querySelector(".loader-title");
    const progress = document.getElementById("loader-progress");
    const percent = document.getElementById("loader-percent");

    let dotsInterval;
    function animateDots() {
        let dots = 0;
        dotsInterval = setInterval(() => {
            const baseText = loaderTitle.textContent.replace(/\.\.\.$/, '');
            dots = (dots + 1) % 4;
            loaderTitle.textContent = baseText + '.'.repeat(dots);
        }, 500);
    }

    iniciarBtn.style.display = "flex";
    pararBtn.style.display = "none";
    voltarBtn.style.display = "flex";

    let mediaRecorder;
    let stream;
    let chunks = [];
    let timerInterval;
    let startTime;
    let videoElement = null;

    function startTimer() {
        startTime = Date.now();
        timerInterval = setInterval(() => {
            const seconds = Math.floor((Date.now() - startTime) / 1000);
            const m = String(Math.floor(seconds / 60)).padStart(2, "0");
            const s = String(seconds % 60).padStart(2, "0");
            timerDisplay.textContent = `${m}:${s}`;
        }, 1000);
    }

    function textoHumano(msg) {
        const m = msg.toLowerCase();
        if (m.includes("inicializando")) return "Inicializando analisador";
        if (m.includes("preparando diretórios")) return "Preparando diretórios";
        if (m.includes("extraindo")) return "Extraindo áudio do vídeo";
        if (m.includes("áudio extraído")) return "Áudio extraído com sucesso";
        if (m.includes("iniciando transcrição")) return "Iniciando transcrição";
        if (m.includes("carregando")) return "Carregando modelos de IA";
        if (m.includes("pipeline")) return "Configurando separação de vozes";
        if (m.includes("análise de tom")) return "Analisando tom de voz";
        if (m.includes("voz concluída")) return "Análise de voz concluída";
        if (m.includes("apresentador")) return "Identificando apresentador";
        if (m.includes("limpando")) return "Limpando áudio";
        if (m.includes("gemini")) return "Transcrevendo com IA avançada";
        if (m.includes("transcrição salva")) return "Transcrição salva";
        if (m.includes("analisando linguagem")) return "Analisando linguagem";
        if (m.includes("calculando")) return "Calculando métricas";
        if (m.includes("gerando")) return "Gerando feedback personalizado";
        if (m.includes("relatório salvo")) return "Relatório salvo";
        if (m.includes("sucesso")) return "Processamento concluído!";
        if (m.includes("preparando análise")) return "Preparando análise";
        if (m.includes("transcrevendo seu vídeo")) return "Transcrevendo seu vídeo";
        if (m.includes("gerando relatório")) return "Gerando relatório";
        if (m.includes("transcrição")) return "Transcrevendo";
        if (m.includes("diarização")) return "Separando vozes";
        if (m.includes("relatório")) return "Gerando relatório";
        return "Processando";
    }

    function atualizarMensagem(t) {
        loaderTitle.textContent = t;
    }

    async function buscarStatus(id) {
        try {
            const r = await fetch(`/sala/analisar/status/${id}/`);
            const j = await r.json();

            atualizarMensagem(textoHumano(j.mensagem));
            progress.style.width = j.progresso + "%";
            percent.textContent = j.progresso + "%";

            if (j.status === "completed" && j.redirect) {
                clearInterval(dotsInterval);
                atualizarMensagem("Finalizando");
                setTimeout(() => window.location.href = j.redirect, 300);
                return;
            }

            if (j.status === "error") {
                clearInterval(dotsInterval);
                loader.style.display = "none";
                return;
            }

            setTimeout(() => buscarStatus(id), 600);
        } catch {
            loader.style.display = "none";
        }
    }

    const iniciarGravacao = async () => {
        try {
            stream = await navigator.mediaDevices.getUserMedia({
                video: { width: { ideal: 1280 }, height: { ideal: 720 } },
                audio: { echoCancellation: true, noiseSuppression: true }
            });

            videoElement = document.createElement("video");
            videoElement.srcObject = stream;
            videoElement.muted = true;
            videoElement.autoplay = true;
            videoElement.playsInline = true;
            videoContainer.innerHTML = "";
            videoContainer.appendChild(videoElement);

            mediaRecorder = new MediaRecorder(stream, { mimeType: "video/webm" });
            chunks = [];

            mediaRecorder.ondataavailable = e => chunks.push(e.data);
            mediaRecorder.onstop = uploadRecording;

            mediaRecorder.start();
            startTimer();

            iniciarBtn.style.display = "none";
            voltarBtn.style.display = "none";
            pararBtn.style.display = "flex";
            temaInput.disabled = true;
            tipoSelect.disabled = true;

        } catch {}
    };

    const startRecording = async () => {
        const tema = temaInput.value;
        const tipo = tipoSelect.value;

        if (!tema || !tipo) return;

        const r = await fetch(`/sala/verificar-duplicado/?tema=${encodeURIComponent(tema)}&tipo=${encodeURIComponent(tipo)}`);
        const j = await r.json();

        const isDark = document.documentElement.classList.contains("dark-mode");

        if (j.duplicado) {
            Swal.fire({
                title: "Apresentação já existe",
                text: "Você já possui uma apresentação com esse tema e tipo. Deseja continuar?",
                icon: "warning",
                background: isDark ? "#1e1e1e" : "#ffffff",
                color: isDark ? "#e1e5e9" : "#333333",
                showCancelButton: true,
                confirmButtonText: "Continuar",
                cancelButtonText: "Cancelar",
                confirmButtonColor: "#0F9D58",
                cancelButtonColor: "#d33"
            }).then(result => {
                if (result.isConfirmed) iniciarGravacao();
            });

            return;
        }

        iniciarGravacao();
    };

    const stopRecording = () => {
        if (mediaRecorder && mediaRecorder.state === "recording") mediaRecorder.stop();
        if (stream) stream.getTracks().forEach(t => t.stop());
        if (videoElement) videoElement.remove();
        videoContainer.innerHTML = "";
        clearInterval(timerInterval);
        pararBtn.style.display = "none";
    };

    const uploadRecording = async () => {
        loader.style.display = "flex";
        progress.style.width = "0%";
        percent.textContent = "0%";
        loaderTitle.textContent = "Preparando envio";

        const blob = new Blob(chunks, { type: "video/webm" });
        const file = new File([blob], "gravacao.webm", { type: "video/webm" });

        const formData = new FormData();
        formData.append("video", file);
        formData.append("tema", temaInput.value);
        formData.append("tipo_discurso", tipoSelect.value);
        const contexto = document.getElementById("contexto-gravacao").value || "";
        formData.append("contexto_apresentacao", contexto);
        formData.append("csrfmiddlewaretoken", csrfToken);

        try {
            const r = await fetch("/sala/iniciar-analise/", {
                method: "POST",
                body: formData
            });

            const j = await r.json();

            if (!r.ok) {
                Swal.fire({
                    title: 'Erro',
                    text: j.erro || 'Falha ao enviar vídeo',
                    icon: 'error'
                });
                loader.style.display = "none";
                return;
            }

            if (j.process_id) buscarStatus(j.process_id);
            else loader.style.display = "none";

        } catch (error) {
            console.error('Erro:', error);
            Swal.fire({
                title: 'Erro',
                text: 'Falha ao enviar vídeo. Verifique sua conexão.',
                icon: 'error'
            });
            loader.style.display = "none";
        }
    };

    iniciarBtn.addEventListener("click", startRecording);
    pararBtn.addEventListener("click", stopRecording);
});