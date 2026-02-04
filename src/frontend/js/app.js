const { createApp } = Vue;

// CONFIGURAÇÃO
const API_BASE_URL = "http://localhost:8000/api";

createApp({
    data() {
        return {
            // --- ESTADO DA APLICAÇÃO ---
            viewAtual: 'dashboard',
            apiStatusText: 'Conectando...',
            apiStatusClass: '',

            // --- DADOS DO DASHBOARD ---
            stats: {
                total_geral: 0,
                media_por_lancamento: 0,
                top_5: []
            },
            loadingStats: false,
            erroStats: null,

            // --- DADOS DO GRÁFICO (NOVO) ---
            chartInstance: null,
            dadosGrafico: [],

            // --- DADOS DE BUSCA ---
            termoBusca: "",
            operadoras: [],
            page: 1,
            limit: 10,
            totalRegistros: 0,
            loadingOps: false,
            erroOps: null,
            iniciouBusca: false,
            searchTimeout: null,

            // --- DADOS DE DETALHES ---
            cacheDespesas: {},
            despesasAbertas: {},
            loadingDespesas: {},

            // --- MODAL ---
            modalAberto: false,
            operadoraSelecionada: null,
            carregandoOperadora: false
        }
    },
    computed: {
        totalPages() {
            if (this.totalRegistros === 0) return 1;
            return Math.ceil(this.totalRegistros / this.limit);
        }
    },
    methods: {
        // --- UTILITÁRIOS ---
        navegarPara(view) {
            this.viewAtual = view;
            window.scrollTo({ top: 0, behavior: 'smooth' });

            // Re-renderiza o gráfico (Top 10) ao voltar para o dashboard
            if (view === 'dashboard' && this.dadosGrafico.length > 0) {
                setTimeout(() => {
                    const top10 = this.dadosGrafico.slice(0, 10);
                    const labels = top10.map(item => item.uf);
                    const values = top10.map(item => item.total);
                    this.renderizarChart(labels, values);
                }, 100);
            }
        },

        formatMoney(value) {
            if (value === undefined || value === null) return 'R$ -';
            return Number(value).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
        },

        calcularEstiloDinamico(numero) {
            const texto = String(numero);
            const tamanho = texto.length;
            let fontSize;
            if (tamanho <= 12) fontSize = '3rem';
            else if (tamanho <= 18) fontSize = '2.4rem';
            else if (tamanho <= 24) fontSize = '2rem';
            else fontSize = '1.5rem';
            const width = Math.max(14, tamanho * 0.58 + 1) + 'em';
            return {
                fontSize: fontSize,
                width: width,
                whiteSpace: 'nowrap',
                display: 'inline-block'
            };
        },

        // --- DASHBOARD ---
        async carregarStats() {
            this.loadingStats = true;
            this.erroStats = null;
            try {
                const response = await axios.get(`${API_BASE_URL}/estatisticas`);
                this.stats = response.data;
                this.apiStatusText = "Online";
                this.apiStatusClass = "online";
            } catch (error) {
                console.error("Erro ao carregar estatísticas:", error);
                this.erroStats = "Não foi possível conectar ao servidor. Verifique se a API está rodando.";
                this.apiStatusText = "Offline";
                this.apiStatusClass = "offline";
            } finally {
                this.loadingStats = false;
            }
        },

        // --- MÉTODO PARA CARREGAR DADOS DO GRÁFICO ---
        async carregarGrafico() {
            try {
                const response = await axios.get(`${API_BASE_URL}/estatisticas/uf`);
                const dados = response.data; // Todos os dados

                this.dadosGrafico = dados; // Salva TODOS para a lista abaixo

                // ALTERAÇÃO: Voltamos a usar slice(0, 10) APENAS para o gráfico
                const top10 = dados.slice(0, 10);
                const labels = top10.map(d => d.uf);
                const values = top10.map(d => d.total);

                this.renderizarChart(labels, values);

            } catch (e) {
                console.error("Erro ao carregar gráfico de UFs:", e);
            }
        },

        // --- RENDERIZAR CHART.JS ---
        renderizarChart(labels, values) {
            const ctx = document.getElementById('graficoUF');
            if (!ctx) return;

            if (this.chartInstance) {
                this.chartInstance.destroy();
            }

            this.chartInstance = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Total de Despesas',
                        data: values,
                        backgroundColor: '#3498db',
                        borderColor: '#2980b9',
                        borderWidth: 1,
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: (context) => this.formatMoney(context.raw)
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: { color: '#f0f0f0' },
                            ticks: {
                                callback: function (value) {
                                    if (value >= 1000000000) return (value / 1000000000).toFixed(1) + 'B';
                                    if (value >= 1000000) return (value / 1000000).toFixed(1) + 'M';
                                    return value;
                                }
                            }
                        },
                        x: {
                            grid: { display: false }
                        }
                    }
                }
            });
        },

        // --- BUSCA DE OPERADORAS ---
        async buscarOperadoras(novaPagina) {
            this.loadingOps = true;
            this.erroOps = null;
            this.iniciouBusca = true;
            if (novaPagina) this.page = novaPagina;

            try {
                const response = await axios.get(`${API_BASE_URL}/operadoras`, {
                    params: {
                        cnpj: this.termoBusca,
                        page: this.page,
                        limit: this.limit
                    }
                });
                this.operadoras = response.data.items;
                this.totalRegistros = response.data.total;
                window.scrollTo(0, 0);
            } catch (error) {
                console.error("Erro na busca:", error);
                this.erroOps = "Falha ao buscar dados. Tente novamente.";
            } finally {
                this.loadingOps = false;
            }
        },

        buscarEmTempoReal() {
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(() => {
                this.buscarOperadoras(1);
            }, 300);
        },

        mudarPagina(delta) {
            const proxima = this.page + delta;
            if (proxima > 0 && proxima <= this.totalPages) {
                this.buscarOperadoras(proxima);
            }
        },

        async toggleDespesas(op) {
            const id = op.registro_ans;
            const cnpj = op.cnpj;
            if (this.despesasAbertas[id]) {
                this.despesasAbertas[id] = false;
                return;
            }
            this.despesasAbertas[id] = true;
            if (this.cacheDespesas[cnpj]) return;
            this.loadingDespesas[id] = true;
            try {
                const response = await axios.get(`${API_BASE_URL}/operadoras/${cnpj}/despesas`);
                this.cacheDespesas[cnpj] = response.data;
            } catch (error) {
                this.cacheDespesas[cnpj] = [];
                alert("Não foi possível carregar os detalhes.");
            } finally {
                this.loadingDespesas[id] = false;
            }
        },

        async abrirModal(operadora) {
            this.operadoraSelecionada = operadora;
            this.modalAberto = true;
            this.carregandoOperadora = true;
            document.body.style.overflow = 'hidden';
            try {
                const response = await axios.get(`${API_BASE_URL}/operadoras/${operadora.cnpj}`);
                this.operadoraSelecionada = response.data;
                if (!this.cacheDespesas[operadora.cnpj]) {
                    const despesasResponse = await axios.get(`${API_BASE_URL}/operadoras/${operadora.cnpj}/despesas`);
                    this.cacheDespesas[operadora.cnpj] = despesasResponse.data;
                }
            } catch (error) {
                console.error("Erro ao carregar detalhes:", error);
            } finally {
                this.carregandoOperadora = false;
            }
        },

        async abrirModalTop5(operadoraTop5) {
            this.modalAberto = true;
            this.carregandoOperadora = true;
            document.body.style.overflow = 'hidden';
            try {
                const response = await axios.get(`${API_BASE_URL}/operadoras/${operadoraTop5.cnpj}`);
                this.operadoraSelecionada = response.data;
                if (!this.cacheDespesas[operadoraTop5.cnpj]) {
                    const despesasResponse = await axios.get(`${API_BASE_URL}/operadoras/${operadoraTop5.cnpj}/despesas`);
                    this.cacheDespesas[operadoraTop5.cnpj] = despesasResponse.data;
                }
            } catch (error) {
                console.error("Erro:", error);
                alert("Não foi possível encontrar detalhes.");
            } finally {
                this.carregandoOperadora = false;
            }
        },

        fecharModal() {
            this.modalAberto = false;
            this.operadoraSelecionada = null;
            document.body.style.overflow = 'auto';
        }
    },
    mounted() {
        this.carregarStats();
        this.carregarGrafico();
        this.buscarOperadoras(1);
    }
}).mount('#app');