const inputArquivo = document.getElementById("input-arquivo");
const areaUpload = document.getElementById("area-upload");
const botaoEnviar = document.getElementById("btn-enviar-video");
const inputTema = document.getElementById("tema-upload");
const selectDiscurso = document.getElementById("tipo-discurso");
const loader = document.getElementById("loader-sala");
const loaderTitle = document.querySelector(".loader-title");
const progress = document.getElementById("loader-progress");
const percent = document.getElementById("loader-percent");

const uploadIcon = document.getElementById("upload-icon");
const uploadText = document.getElementById("upload-text");
const uploadSeparator = document.getElementById("upload-separator");
const labelInputArquivo = document.getElementById("label-input-arquivo");
const btnDesanexar = document.getElementById("btn-desanexar");

let arquivoSelecionado = null;

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
    return null;
}

function mensagem(titulo, texto, tipo) {
    if (typeof Swal !== "undefined") {
        Swal.fire({
            title: titulo,
            text: texto,
            icon: tipo,
            confirmButtonColor: "#0F9D58",
            confirmButtonText: "Ok",
            backdrop: "rgba(0,0,0,0.45)"
        });
    } else {
        alert(`${titulo}: ${texto}`);
    }
}

function handleFile(file) {
    if (!file) return;

    if (!file.type.startsWith("video/")) {
        mensagem("Tipo inválido", "Selecione um arquivo de vídeo.", "warning");
        return;
    }

    arquivoSelecionado = file;
    areaUpload.classList.add("file-selected");
    uploadIcon.className = "fas fa-file-video";
    uploadText.innerText = file.name;
    uploadSeparator.style.display = "none";
    labelInputArquivo.style.display = "none";
    btnDesanexar.style.display = "inline-flex";
}

function resetUploadArea() {
    arquivoSelecionado = null;
    inputArquivo.value = null;
    areaUpload.classList.remove("file-selected");
    areaUpload.classList.remove("dragover");
    uploadIcon.className = "fas fa-cloud-arrow-up";
    uploadText.innerText = "Arraste e solte seu vídeo aqui";
    uploadSeparator.style.display = "block";
    labelInputArquivo.style.display = "inline-flex";
    btnDesanexar.style.display = "none";
}

areaUpload.addEventListener("click", e => {
    if (e.target.id === "btn-desanexar" || e.target.closest("#btn-desanexar")) return;
    inputArquivo.click();
});

btnDesanexar.addEventListener("click", e => {
    e.stopPropagation();
    resetUploadArea();
});

inputArquivo.addEventListener("change", function () {
    handleFile(this.files[0] || null);
});

areaUpload.addEventListener("dragover", e => {
    e.preventDefault();
    areaUpload.classList.add("dragover");
    uploadIcon.className = "fas fa-file-video";
    uploadText.innerText = "Solte o vídeo para carregar";
});

areaUpload.addEventListener("dragleave", () => {
    areaUpload.classList.remove("dragover");
    if (!arquivoSelecionado) {
        uploadIcon.className = "fas fa-cloud-arrow-up";
        uploadText.innerText = "Arraste e solte seu vídeo aqui";
    }
});

areaUpload.addEventListener("drop", e => {
    e.preventDefault();
    areaUpload.classList.remove("dragover");
    const arquivo = e.dataTransfer.files[0];
    handleFile(arquivo);
});

function textoHumano(msg) {
    const m = msg.toLowerCase();
    if (m.includes("transcrição")) return "Transcrevendo seu vídeo...";
    if (m.includes("carregando")) return "Preparando análise...";
    if (m.includes("análise de voz")) return "Analisando voz...";
    if (m.includes("identificado")) return "Identificando apresentador...";
    if (m.includes("limpando")) return "Limpando áudio...";
    if (m.includes("gemini")) return "Transcrevendo com IA...";
    if (m.includes("relatório")) return "Gerando relatório...";
    return "Processando...";
}

function atualizarMensagemSuave(t) {
    if (loaderTitle.dataset.textoAtual === t) return;
    loaderTitle.dataset.textoAtual = t;
    loaderTitle.style.transition = "opacity .2s";
    loaderTitle.style.opacity = "0";
    setTimeout(() => {
        loaderTitle.textContent = t;
        loaderTitle.style.opacity = "1";
    }, 150);
}

async function buscarStatus(id) {
    try {
        const r = await fetch(`/sala/analisar/status/${id}/`);
        const j = await r.json();

        if (!j || j.status === "not_found") {
            setTimeout(() => buscarStatus(id), 1000);
            return;
        }

        atualizarMensagemSuave(textoHumano(j.mensagem));
        progress.style.width = j.progresso + "%";
        percent.innerText = j.progresso + "%";

        if (j.status === "completed" && j.redirect) {
            atualizarMensagemSuave("Análise concluída");
            setTimeout(() => window.location.href = j.redirect, 400);
            return;
        }

        if (j.status === "error") {
            atualizarMensagemSuave("Erro ao processar");
            mensagem("Erro", j.mensagem || "Falha ao analisar.", "error");
            loader.style.display = "none";
            return;
        }

        setTimeout(() => buscarStatus(id), 600);

    } catch {
        atualizarMensagemSuave("Erro de conexão");
        mensagem("Erro", "Falha ao verificar o status.", "error");
        loader.style.display = "none";
    }
}

botaoEnviar.addEventListener("click", async () => {
    if (!arquivoSelecionado) {
        mensagem("Nenhum vídeo", "Selecione um arquivo.", "warning");
        return;
    }
    if (!inputTema.value.trim()) {
        mensagem("Informe o tema", "Digite o tema da apresentação.", "warning");
        return;
    }
    if (!selectDiscurso.value.trim()) {
        mensagem("Selecione o tipo", "Escolha o tipo de apresentação.", "warning");
        return;
    }

    const tema = inputTema.value.trim();
    const tipo = selectDiscurso.value.trim();

    const req = await fetch(`/sala/verificar-duplicado/?tema=${encodeURIComponent(tema)}&tipo=${encodeURIComponent(tipo)}`);
    const duplicado = await req.json();

    const isDark = document.documentElement.classList.contains("dark-mode");

    if (duplicado.duplicado) {
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
            if (result.isConfirmed) enviarVideo();
        });

        return;
    }

    enviarVideo();
});

async function enviarVideo() {
    loader.style.display = "flex";
    progress.style.width = "0%";
    percent.innerText = "0%";
    loaderTitle.dataset.textoAtual = "";
    atualizarMensagemSuave("Preparando envio...");

    const formData = new FormData();
    formData.append("video", arquivoSelecionado);
    formData.append("tema", inputTema.value);
    formData.append("tipo_discurso", selectDiscurso.value);
    const contexto = document.getElementById("contexto-upload").value || "";
    formData.append("contexto_apresentacao", contexto);


    try {
        const r = await fetch("/sala/analisar/iniciar/", {
            method: "POST",
            headers: { "X-CSRFToken": getCookie("csrftoken") },
            body: formData
        });

        const j = await r.json();

        if (r.ok && j.process_id) buscarStatus(j.process_id);
        else {
            loader.style.display = "none";
            mensagem("Erro", j.error || "Não foi possível iniciar a análise.", "error");
        }

    } catch {
        loader.style.display = "none";
        mensagem("Erro", "Falha ao enviar o vídeo.", "error");
    }
}