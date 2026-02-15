/**
 * Cliente API para Sistema de Biblioteca
 * Gerencia todas as comunicações com o backend
 */

// Configuração
const API_URL = 'http://localhost:8000';

// ============================================================================
// AUTENTICAÇÃO E TOKEN
// ============================================================================

/**
 * Retorna o token JWT armazenado
 * @returns {string|null} Token ou null se não existir
 */
function getToken() {
    return localStorage.getItem('token');
}

/**
 * Salva o token JWT no localStorage
 * @param {string} token - Token JWT
 */
function setToken(token) {
    localStorage.setItem('token', token);
}

/**
 * Remove o token e redireciona para login
 */
function clearToken() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login.html';
}

/**
 * Verifica se o usuário está autenticado
 * @returns {boolean} True se houver token válido
 */
function isAuthenticated() {
    return !!getToken();
}

// ============================================================================
// FUNÇÕES HTTP BASE
// ============================================================================

/**
 * Função base para requisições à API
 * @param {string} endpoint - Endpoint da API (ex: '/auth/login')
 * @param {Object} options - Opções do fetch
 * @returns {Promise<any>} Response JSON parseado
 * @throws {Error} Se a requisição falhar
 */
async function apiRequest(endpoint, options = {}) {
    const url = `${API_URL}${endpoint}`;

    // Configuração padrão
    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
        ...options
    };

    // Adiciona token de autenticação se existir
    const token = getToken();
    if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(url, config);

        // Trata erro 401 (não autorizado)
        if (response.status === 401) {
            clearToken();
            throw new Error('Sessão expirada. Faça login novamente.');
        }

        // Trata outros erros HTTP
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || `Erro HTTP ${response.status}`);
        }

        // Retorna resposta vazia para 204 No Content
        if (response.status === 204) {
            return null;
        }

        return await response.json();
    } catch (error) {
        console.error(`Erro na requisição ${endpoint}:`, error);
        throw error;
    }
}

// ============================================================================
// API DE AUTENTICAÇÃO
// ============================================================================

const auth = {
    /**
     * Registra novo usuário
     * @param {string} username - Nome de usuário
     * @param {string} email - Email
     * @param {string} password - Senha
     * @returns {Promise<Object>} Dados do usuário criado
     */
    async register(username, email, password) {
        return await apiRequest('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ username, email, password })
        });
    },

    /**
     * Faz login do usuário
     * @param {string} username - Nome de usuário
     * @param {string} password - Senha
     * @returns {Promise<Object>} Token e dados do usuário
     */
    async login(username, password) {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await apiRequest('/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData
        });

        // Salva token e dados do usuário
        setToken(response.access_token);
        localStorage.setItem('user', JSON.stringify(response.user));

        return response;
    },

    /**
     * Busca dados do usuário atual
     * @returns {Promise<Object>} Dados do usuário
     */
    async getMe() {
        return await apiRequest('/auth/me');
    }
};

// ============================================================================
// API DE USUÁRIOS
// ============================================================================

const users = {
    /**
     * Lista usuários com paginação
     * @param {number} page - Página (padrão: 1)
     * @param {number} limit - Itens por página (padrão: 10)
     * @param {string} role - Filtro por role (opcional)
     * @returns {Promise<Object>} Lista paginada de usuários
     */
    async list(page = 1, limit = 10, role = null) {
        const params = new URLSearchParams({
            skip: (page - 1) * limit,
            limit: limit
        });

        if (role) {
            params.append('role', role);
        }

        return await apiRequest(`/users?${params}`);
    },

    /**
     * Busca usuário por ID
     * @param {number} id - ID do usuário
     * @returns {Promise<Object>} Dados do usuário
     */
    async get(id) {
        return await apiRequest(`/users/${id}`);
    },

    /**
     * Atualiza role do usuário
     * @param {number} id - ID do usuário
     * @param {string} role - Nova role (user, librarian, admin)
     * @returns {Promise<Object>} Usuário atualizado
     */
    async updateRole(id, role) {
        return await apiRequest(`/users/${id}/role`, {
            method: 'PUT',
            body: JSON.stringify({ role })
        });
    },

    /**
     * Busca estatísticas de um usuário
     * @param {number} id - ID do usuário
     * @returns {Promise<Object>} Estatísticas (total_loans, active_loans, etc)
     */
    async getStats(id) {
        return await apiRequest(`/users/${id}/stats`);
    }
};

// ============================================================================
// API DE CATEGORIAS
// ============================================================================

const categories = {
    /**
     * Lista todas as categorias
     * @returns {Promise<Array>} Lista de categorias
     */
    async list() {
        return await apiRequest('/categories');
    },

    /**
     * Busca categoria por ID
     * @param {number} id - ID da categoria
     * @returns {Promise<Object>} Dados da categoria
     */
    async get(id) {
        return await apiRequest(`/categories/${id}`);
    },

    /**
     * Cria nova categoria
     * @param {string} name - Nome da categoria
     * @param {string} description - Descrição (opcional)
     * @returns {Promise<Object>} Categoria criada
     */
    async create(name, description = null) {
        return await apiRequest('/categories', {
            method: 'POST',
            body: JSON.stringify({ name, description })
        });
    },

    /**
     * Atualiza categoria existente
     * @param {number} id - ID da categoria
     * @param {string} name - Novo nome
     * @param {string} description - Nova descrição
     * @returns {Promise<Object>} Categoria atualizada
     */
    async update(id, name, description = null) {
        return await apiRequest(`/categories/${id}`, {
            method: 'PUT',
            body: JSON.stringify({ name, description })
        });
    },

    /**
     * Remove categoria
     * @param {number} id - ID da categoria
     * @returns {Promise<null>} Sem retorno
     */
    async delete(id) {
        return await apiRequest(`/categories/${id}`, {
            method: 'DELETE'
        });
    }
};

// ============================================================================
// API DE LIVROS
// ============================================================================

const books = {
    /**
     * Lista livros com filtros e paginação
     * @param {Object} filters - Filtros {title, author, category_id, available}
     * @param {number} page - Página (padrão: 1)
     * @param {number} limit - Itens por página (padrão: 10)
     * @returns {Promise<Object>} Lista paginada de livros
     */
    async list(filters = {}, page = 1, limit = 10) {
        const params = new URLSearchParams({
            skip: (page - 1) * limit,
            limit: limit
        });

        // Adiciona filtros opcionais
        if (filters.title) params.append('title', filters.title);
        if (filters.author) params.append('author', filters.author);
        if (filters.category_id) params.append('category_id', filters.category_id);
        if (filters.available !== undefined) params.append('available', filters.available);

        return await apiRequest(`/books?${params}`);
    },

    /**
     * Busca livro por ID
     * @param {number} id - ID do livro
     * @returns {Promise<Object>} Dados do livro
     */
    async get(id) {
        return await apiRequest(`/books/${id}`);
    },

    /**
     * Cria novo livro
     * @param {Object} data - Dados do livro {title, author, isbn, category_id, publication_year, total_copies}
     * @returns {Promise<Object>} Livro criado
     */
    async create(data) {
        return await apiRequest('/books', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    /**
     * Atualiza livro existente
     * @param {number} id - ID do livro
     * @param {Object} data - Dados a atualizar
     * @returns {Promise<Object>} Livro atualizado
     */
    async update(id, data) {
        return await apiRequest(`/books/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    /**
     * Remove livro
     * @param {number} id - ID do livro
     * @returns {Promise<null>} Sem retorno
     */
    async delete(id) {
        return await apiRequest(`/books/${id}`, {
            method: 'DELETE'
        });
    }
};

// ============================================================================
// API DE EMPRÉSTIMOS
// ============================================================================

const loans = {
    /**
     * Lista empréstimos com filtros e paginação
     * @param {Object} filters - Filtros {status, user_id, book_id}
     * @param {number} page - Página (padrão: 1)
     * @param {number} limit - Itens por página (padrão: 10)
     * @returns {Promise<Object>} Lista paginada de empréstimos
     */
    async list(filters = {}, page = 1, limit = 10) {
        const params = new URLSearchParams({
            skip: (page - 1) * limit,
            limit: limit
        });

        // Adiciona filtros opcionais
        if (filters.status) params.append('status', filters.status);
        if (filters.user_id) params.append('user_id', filters.user_id);
        if (filters.book_id) params.append('book_id', filters.book_id);

        return await apiRequest(`/loans?${params}`);
    },

    /**
     * Lista empréstimos do usuário atual
     * @returns {Promise<Array>} Lista de empréstimos
     */
    async myLoans() {
        return await apiRequest('/loans/my-loans');
    },

    /**
     * Lista empréstimos atrasados
     * @returns {Promise<Array>} Lista de empréstimos atrasados
     */
    async overdue() {
        return await apiRequest('/loans/overdue');
    },

    /**
     * Cria novo empréstimo
     * @param {number} book_id - ID do livro
     * @returns {Promise<Object>} Empréstimo criado
     */
    async create(book_id) {
        return await apiRequest('/loans', {
            method: 'POST',
            body: JSON.stringify({ book_id })
        });
    },

    /**
     * Registra devolução de empréstimo
     * @param {number} id - ID do empréstimo
     * @returns {Promise<Object>} Empréstimo atualizado
     */
    async return(id) {
        return await apiRequest(`/loans/${id}/return`, {
            method: 'PUT'
        });
    }
};

// ============================================================================
// HELPERS DE UI
// ============================================================================

/**
 * Exibe mensagem de erro
 * @param {string} message - Mensagem de erro
 */
function showError(message) {
    // Verifica se existe função customizada de toast/alert
    if (window.showToast) {
        window.showToast(message, 'error');
    } else {
        alert(`Erro: ${message}`);
    }
}

/**
 * Exibe mensagem de sucesso
 * @param {string} message - Mensagem de sucesso
 */
function showSuccess(message) {
    // Verifica se existe função customizada de toast/alert
    if (window.showToast) {
        window.showToast(message, 'success');
    } else {
        alert(message);
    }
}

// ============================================================================
// EXPORTAÇÃO GLOBAL
// ============================================================================

window.API = {
    // Configuração
    API_URL,

    // Autenticação
    getToken,
    setToken,
    clearToken,
    isAuthenticated,

    // Request base
    apiRequest,

    // Módulos da API
    auth,
    users,
    categories,
    books,
    loans,

    // Helpers
    showError,
    showSuccess
};
