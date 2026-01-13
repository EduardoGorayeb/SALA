const grid = document.getElementById("grid-relatorios");
const paginacao = document.getElementById("paginacao");
const buscaInput = document.getElementById("filtro-busca");
const temaSelect = document.getElementById("filtro-tema");
const ordenacao = document.getElementById("filtro-ordenacao");

const POR_PAGINA = 6;
let paginaAtual = 1;
let listaFiltrada = [...RELATORIOS];
let modoExclusao = false;
let selecionados = new Set();

function seguro(valor, padrao = "--") {
    if (valor === null || valor === undefined || valor === "" || (typeof valor === 'number' && Number.isNaN(valor))) {
        return padrao;
    }
    return valor;
}

function formatarTipoDiscurso(tipo) {
    const mapa = {
        "tcc": "TCC",
        "palestra_tecnica": "Palestra Técnica",
        "videoaula": "Videoaula",
        "palestra_motivacional": "Palestra Motivacional",
        "pitch_comercial": "Pitch Comercial",
        "pitch_startup": "Pitch de Startup",
        "explicacao_escolar": "Apresentação Escolar",
        "livre": "Apresentação Livre"
    };
    return seguro(mapa[tipo], tipo);
}

function extrairNotaGeral(dados) {
    const nota = seguro(dados.final_score, null);
    return nota !== null ? parseFloat(nota).toFixed(1) : "--";
}

function extrairClareza(dados) {
    const clareza = seguro(dados.scores?.clareza, null);
    return clareza !== null ? parseFloat(clareza).toFixed(1) : "--";
}

function extrairDuracao(dados) {
    const dur = seguro(dados.duration_total, 0);
    if (dur === 0) return "--";
    const min = Math.floor(dur / 60);
    const seg = Math.floor(dur % 60);
    return `${min}min ${seg}s`;
}

function extrairCalma(dados) {
    const calma = seguro(dados.linguagem?.human_nervousness, null);
    return calma !== null ? (calma * 100).toFixed(0) + "%" : "--";
}

function extrairFoco(dados) {
    const foco = seguro(dados.linguagem?.semantic_redundancy, null);
    return foco !== null ? (foco * 100).toFixed(0) + "%" : "--";
}

function renderizarCards() {
    grid.innerHTML = "";

    if (listaFiltrada.length === 0) {
        const div = document.createElement("div");
        div.className = "historico-vazio";
        div.innerHTML = `
            <i class="fas fa-clipboard-list"></i>
            <p>Nenhum relatório encontrado.</p>
        `;
        grid.appendChild(div);
        paginacao.innerHTML = "";
        return;
    }

    const inicio = (paginaAtual - 1) * POR_PAGINA;
    const fim = inicio + POR_PAGINA;
    const pagina = listaFiltrada.slice(inicio, fim);

    pagina.forEach(r => {
        const dados = r.dados || {};

        const notaGeral = extrairNotaGeral(dados);
        const clareza = extrairClareza(dados);
        const duracao = extrairDuracao(dados);
        const calma = extrairCalma(dados);
        const foco = extrairFoco(dados);

        const temaApresentacao = seguro(dados.tema_fornecido, "Tema não informado");
        const tipoDiscurso = formatarTipoDiscurso(seguro(dados.tipo_discurso, "Não definido"));

        const card = document.createElement("div");
        card.className = "card-relatorio";
        if (modoExclusao) {
            card.classList.add("modo-exclusao");
            if (selecionados.has(r.id)) {
                card.classList.add("selecionado");
            }
        }

        card.innerHTML = `
            ${modoExclusao ? `<input type="checkbox" class="checkbox-selecao" data-id="${r.id}" ${selecionados.has(r.id) ? 'checked' : ''}>` : ''}
            <div class="card-header">
                <h3 title="${temaApresentacao}">${temaApresentacao}</h3>
                <span>${seguro(r.criado_em, "")}</span>
            </div>

            <div class="card-tag">${tipoDiscurso}</div>

            <div class="card-scores">
                <div class="score-item">
                    <span class="score-valor">${notaGeral}</span>
                    <span class="score-label">Nota Geral</span>
                </div>
                <div class="score-item">
                    <span class="score-valor">${clareza}</span>
                    <span class="score-label">Clareza</span>
                </div>
            </div>

            <ul class="card-detalhes">
                <li><span>Duração</span><strong>${duracao}</strong></li>
                <li><span>Calma (Concentração)</span><strong>${calma}</strong></li>
                <li><span>Foco no Tema</span><strong>${foco}</strong></li>
            </ul>

            <div class="card-botoes">
                <a href="/sala/relatorio/${r.id}/" class="btn-ver-relatorio" title="Abrir relatório completo">
                    <i class="fas fa-chart-pie"></i> Ver Relatório
                </a>

                <a href="/relatorio/${r.id}/pdf/" class="btn-pdf" title="Baixar PDF">
                    <i class="fas fa-file-pdf"></i> PDF
                </a>
            </div>
        `;

        if (modoExclusao) {
            card.addEventListener('click', (e) => {
                if (e.target.type !== 'checkbox') {
                    const checkbox = card.querySelector('.checkbox-selecao');
                    checkbox.checked = !checkbox.checked;
                    toggleSelecao(r.id);
                }
            });
        }

        grid.appendChild(card);
    });

    renderizarPaginacao();
}

function renderizarPaginacao() {
    paginacao.innerHTML = "";

    const totalPaginas = Math.ceil(listaFiltrada.length / POR_PAGINA);
    if (totalPaginas <= 1) return;

    const criarBotao = (txt, pag) => {
        const a = document.createElement("a");
        a.textContent = txt;
        a.href = "#";

        if (pag === paginaAtual) {
            a.classList.add("pagina-ativa");
        }

        a.onclick = e => {
            e.preventDefault();
            paginaAtual = pag;
            renderizarCards();
            document.querySelector('.filtros-relatorios').scrollIntoView({ behavior: 'smooth' });
        };

        return a;
    };

    if (paginaAtual > 1) {
        paginacao.appendChild(criarBotao("«", paginaAtual - 1));
    }

    let inicio = Math.max(1, paginaAtual - 2);
    let fim = Math.min(totalPaginas, paginaAtual + 2);

    if (paginaAtual < 3) {
        fim = Math.min(totalPaginas, 5);
    }
    if (paginaAtual > totalPaginas - 2) {
        inicio = Math.max(1, totalPaginas - 4);
    }

    if (inicio > 1) {
        paginacao.appendChild(criarBotao(1, 1));
        if (inicio > 2) {
            const span = document.createElement('span');
            span.textContent = '...';
            span.className = 'paginacao-ellipsis';
            paginacao.appendChild(span);
        }
    }

    for (let i = inicio; i <= fim; i++) {
        paginacao.appendChild(criarBotao(i, i));
    }

    if (fim < totalPaginas) {
        if (fim < totalPaginas - 1) {
            const span = document.createElement('span');
            span.textContent = '...';
            span.className = 'paginacao-ellipsis';
            paginacao.appendChild(span);
        }
        paginacao.appendChild(criarBotao(totalPaginas, totalPaginas));
    }

    if (paginaAtual < totalPaginas) {
        paginacao.appendChild(criarBotao("»", paginaAtual + 1));
    }
}

function preencherTemas() {
    const temas = new Set();

    RELATORIOS.forEach(r => {
        const tipo = r.dados?.tipo_discurso;
        if (tipo) temas.add(tipo);
    });

    temaSelect.innerHTML = '<option value="">Todos os tipos</option>';

    [...temas].sort().forEach(t => {
        const op = document.createElement("option");
        op.value = t;
        op.textContent = formatarTipoDiscurso(t);
        temaSelect.appendChild(op);
    });
}

function aplicarFiltros() {
    const busca = buscaInput.value.toLowerCase();
    const tema = temaSelect.value;
    const ord = ordenacao.value;

    listaFiltrada = RELATORIOS.filter(r => {
        const dados = r.dados || {};
        const tituloRelatorio = seguro(r.tema, "").toLowerCase();
        const temaApresentacao = seguro(dados.tema_fornecido, "").toLowerCase();

        const tNome = tituloRelatorio.includes(busca) || temaApresentacao.includes(busca);
        const tTema = !tema || dados.tipo_discurso === tema;

        return tNome && tTema;
    });

    
    listaFiltrada.forEach(r => {
        if (!r.criado_em_iso) {
             
             const partes = r.criado_em.split('/');
             r.criado_em_iso = new Date(partes[2], partes[1] - 1, partes[0]);
        }
    });

    if (ord === "antigos") {
        listaFiltrada.sort((a, b) => a.criado_em_iso - b.criado_em_iso);
    } else if (ord === "recentes") {
        listaFiltrada.sort((a, b) => b.criado_em_iso - a.criado_em_iso);
    } else if (ord === "maior-nota") {
        listaFiltrada.sort((a, b) => {
            const notaA = extrairNotaGeral(a.dados);
            const notaB = extrairNotaGeral(b.dados);
            if (notaA === "--") return 1;
            if (notaB === "--") return -1;
            return notaB - notaA;
        });
    }

    paginaAtual = 1;
    renderizarCards();
}


RELATORIOS.forEach(r => {
    
    if (!r.criado_em_iso) {
        const partes = r.criado_em.split('/'); 
        if (partes.length === 3) {
            r.criado_em_iso = new Date(partes[2], partes[1] - 1, partes[0]);
        } else {
            
            r.criado_em_iso = new Date(null);
        }
    }
});


listaFiltrada = [...RELATORIOS];
aplicarFiltros(); 

buscaInput.oninput = aplicarFiltros;
temaSelect.onchange = aplicarFiltros;
ordenacao.onchange = aplicarFiltros;

preencherTemas();


document.addEventListener('click', function(e) {
    if (e.target.closest('.btn-excluir')) {
        const btn = e.target.closest('.btn-excluir');
        const relatorioId = btn.getAttribute('data-id');

        Swal.fire({
            title: 'Tem certeza?',
            text: "Esta ação não pode ser desfeita!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Sim, excluir!',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                fetch(`/excluir-relatorio/${relatorioId}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        Swal.fire(
                            'Excluído!',
                            'O relatório foi excluído com sucesso.',
                            'success'
                        ).then(() => {
                            location.reload();
                        });
                    } else {
                        Swal.fire(
                            'Erro!',
                            'Não foi possível excluir o relatório.',
                            'error'
                        );
                    }
                })
                .catch(error => {
                    console.error('Erro:', error);
                    Swal.fire(
                        'Erro!',
                        'Ocorreu um erro ao excluir o relatório.',
                        'error'
                    );
                });
            }
        });
    }
});


document.getElementById('btn-entrar-modo-exclusao').addEventListener('click', function() {
    modoExclusao = true;
    selecionados.clear();
    document.getElementById('barra-exclusao').style.display = 'block';
    atualizarContador();
    renderizarCards();
});


document.getElementById('btn-confirmar-exclusao').addEventListener('click', function() {
    if (selecionados.size === 0) return;

    Swal.fire({
        title: 'Tem certeza?',
        text: `Você está prestes a excluir ${selecionados.size} relatório(s). Esta ação não pode ser desfeita!`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sim, excluir!',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            const ids = Array.from(selecionados);
            fetch('/excluir-relatorios/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({ ids: ids })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Swal.fire(
                        'Excluídos!',
                        `${selecionados.size} relatório(s) foram excluído(s) com sucesso.`,
                        'success'
                    ).then(() => {
                        location.reload();
                    });
                } else {
                    Swal.fire(
                        'Erro!',
                        'Não foi possível excluir os relatórios.',
                        'error'
                    );
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                Swal.fire(
                    'Erro!',
                    'Ocorreu um erro ao excluir os relatórios.',
                    'error'
                );
            });
        }
    });
});


document.getElementById('btn-cancelar-exclusao').addEventListener('click', function() {
    modoExclusao = false;
    selecionados.clear();
    document.getElementById('barra-exclusao').style.display = 'none';
    renderizarCards();
});

function toggleSelecao(id) {
    if (selecionados.has(id)) {
        selecionados.delete(id);
    } else {
        selecionados.add(id);
    }
    atualizarContador();
}

function atualizarContador() {
    const contador = document.getElementById('contador-selecionados');
    contador.textContent = `${selecionados.size} selecionado(s)`;
    document.getElementById('btn-confirmar-exclusao').disabled = selecionados.size === 0;
}


