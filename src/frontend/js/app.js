const { createApp } = Vue;

// CONFIGURAÇÃO
// Se a API estiver em outra porta, altere aqui.
const API_BASE_URL = "http://localhost:8000/api";

createApp({
    data() {
        return {
            // --- ESTADO DA APLICAÇÃO ---
            viewAtual: 'dashboard', // Controla qual aba está visível
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

            // --- DADOS DE BUSCA ---
            termoBusca: "",
            operadoras: [],
            page: 1,
            limit: 10,
            totalRegistros: 0,
            loadingOps: false,
            erroOps: null,
            iniciouBusca: false, // Para não mostrar "Nenhum resultado" ao abrir a tela
            searchTimeout: null, // Para debounce da busca

            // --- DADOS DE DETALHES (DESPESAS) ---
            // Cache: { '12345678000100': [ ...array de despesas... ] }
            cacheDespesas: {},
            // Estado visual: { 321456: true } (Registro ANS -> Boolean)
            despesasAbertas: {},
            loadingDespesas: {},

            // --- MODAL DE DETALHES ---
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
        },

        formatMoney(value) {
            if (value === undefined || value === null) return 'R$ -';
            return Number(value).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
        },

        calcularEstiloDinamico(numero) {
            const texto = String(numero);
            const tamanho = texto.length;

            // Calcula font-size progressivo baseado no comprimento
            let fontSize;
            if (tamanho <= 12) fontSize = '3rem';
            else if (tamanho <= 18) fontSize = '2.4rem';
            else if (tamanho <= 24) fontSize = '2rem';
            else fontSize = '1.5rem';

            // Calcula width baseado no número de caracteres (aproximado)
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

                // Scroll para o topo da página
                window.scrollTo(0, 0);

            } catch (error) {
                console.error("Erro na busca:", error);
                this.erroOps = "Falha ao buscar dados. Tente novamente.";
            } finally {
                this.loadingOps = false;
            }
        },

        buscarEmTempoReal() {
            // Limpa timeout anterior
            clearTimeout(this.searchTimeout);

            // Define novo timeout para fazer a busca (debounce de 300ms)
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

        // --- DETALHES E CACHE ---
        async toggleDespesas(op) {
            const id = op.registro_ans;
            const cnpj = op.cnpj;

            // 1. Toggle Visual (Abrir/Fechar)
            if (this.despesasAbertas[id]) {
                this.despesasAbertas[id] = false;
                return; // Se fechou, não precisa fazer mais nada
            }
            this.despesasAbertas[id] = true;

            // 2. Verifica Cache (Economia de Requisição)
            if (this.cacheDespesas[cnpj]) {
                console.log(`Usando cache para ${op.razao_social}`);
                return;
            }

            // 3. Busca na API se não tiver no cache
            this.loadingDespesas[id] = true;
            try {
                const response = await axios.get(`${API_BASE_URL}/operadoras/${cnpj}/despesas`);
                // Salva no cache indexado pelo CNPJ
                this.cacheDespesas[cnpj] = response.data;
            } catch (error) {
                console.error("Erro ao buscar despesas:", error);
                // Mesmo com erro, salvamos array vazio para evitar loop infinito de erros
                this.cacheDespesas[cnpj] = [];
                alert("Não foi possível carregar os detalhes desta operadora.");
            } finally {
                this.loadingDespesas[id] = false;
            }
        },

        // --- MODAL ---
        async abrirModal(operadora) {
            this.operadoraSelecionada = operadora;
            this.modalAberto = true;
            this.carregandoOperadora = true;

            // Bloqueia scroll da página
            document.body.style.overflow = 'hidden';

            try {
                // Buscar detalhes completos da operadora
                const response = await axios.get(`${API_BASE_URL}/operadoras/${operadora.cnpj}`);
                this.operadoraSelecionada = response.data;

                // Carregar despesas se não estão em cache
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
            // operadoraTop5 agora contém razao_social, cnpj e total
            this.modalAberto = true;
            this.carregandoOperadora = true;

            // Bloqueia scroll da página
            document.body.style.overflow = 'hidden';

            try {
                // Buscar detalhes da operadora diretamente pelo CNPJ
                const response = await axios.get(`${API_BASE_URL}/operadoras/${operadoraTop5.cnpj}`);
                this.operadoraSelecionada = response.data;

                // Carregar despesas se não estão em cache
                if (!this.cacheDespesas[operadoraTop5.cnpj]) {
                    const despesasResponse = await axios.get(`${API_BASE_URL}/operadoras/${operadoraTop5.cnpj}/despesas`);
                    this.cacheDespesas[operadoraTop5.cnpj] = despesasResponse.data;
                }
            } catch (error) {
                console.error("Erro ao carregar detalhes:", error);
                alert("Não foi possível encontrar os detalhes desta operadora.");
            } finally {
                this.carregandoOperadora = false;
            }
        },

        fecharModal() {
            this.modalAberto = false;
            this.operadoraSelecionada = null;

            // Restaura scroll da página
            document.body.style.overflow = 'auto';
        }
    },
    mounted() {
        // Inicialização
        this.carregarStats();
        // Carrega uma lista inicial para a tela não ficar vazia
        this.buscarOperadoras(1);
    }
}).mount('#app');