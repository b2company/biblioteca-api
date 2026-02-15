/**
 * Lógica de Aplicação e Utilities
 * Funções auxiliares para o frontend da biblioteca
 */

// ============================================================================
// FORMATAÇÃO DE DADOS
// ============================================================================

/**
 * Formata data ISO para DD/MM/YYYY
 * @param {string} isoString - Data em formato ISO (ex: 2026-02-14T10:30:00)
 * @returns {string} Data formatada (ex: 14/02/2026)
 */
function formatDate(isoString) {
    if (!isoString) return '-';

    try {
        const date = new Date(isoString);
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();

        return `${day}/${month}/${year}`;
    } catch (error) {
        console.error('Erro ao formatar data:', error);
        return '-';
    }
}

/**
 * Formata data ISO para DD/MM/YYYY HH:MM
 * @param {string} isoString - Data em formato ISO
 * @returns {string} Data e hora formatadas (ex: 14/02/2026 10:30)
 */
function formatDateTime(isoString) {
    if (!isoString) return '-';

    try {
        const date = new Date(isoString);
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');

        return `${day}/${month}/${year} ${hours}:${minutes}`;
    } catch (error) {
        console.error('Erro ao formatar data/hora:', error);
        return '-';
    }
}

/**
 * Verifica se uma data está vencida
 * @param {string} dueDate - Data de vencimento em formato ISO
 * @returns {boolean} True se a data já passou
 */
function isOverdue(dueDate) {
    if (!dueDate) return false;

    try {
        const due = new Date(dueDate);
        const now = new Date();
        return due < now;
    } catch (error) {
        console.error('Erro ao verificar vencimento:', error);
        return false;
    }
}

// ============================================================================
// NAVEGAÇÃO
// ============================================================================

/**
 * Redireciona para uma página
 * @param {string} page - Caminho da página (ex: 'dashboard.html', '/admin/users.html')
 */
function navigate(page) {
    window.location.href = page;
}

/**
 * Verifica autenticação e redireciona para login se necessário
 * Deve ser chamada em páginas que requerem autenticação
 */
function requireAuth() {
    if (!window.API.isAuthenticated()) {
        navigate('/login.html');
    }
}

/**
 * Faz logout do usuário
 */
function logout() {
    window.API.clearToken();
    navigate('/login.html');
}

// ============================================================================
// GESTÃO DE USUÁRIO
// ============================================================================

/**
 * Retorna dados do usuário atual do localStorage
 * @returns {Object|null} Objeto com dados do usuário ou null
 */
function getCurrentUser() {
    try {
        const userJson = localStorage.getItem('user');
        return userJson ? JSON.parse(userJson) : null;
    } catch (error) {
        console.error('Erro ao obter usuário atual:', error);
        return null;
    }
}

/**
 * Verifica se o usuário atual possui uma das roles especificadas
 * @param {string|Array<string>} roles - Role ou array de roles (ex: 'admin' ou ['admin', 'librarian'])
 * @returns {boolean} True se usuário tem uma das roles
 */
function hasRole(roles) {
    const user = getCurrentUser();
    if (!user || !user.role) return false;

    const roleArray = Array.isArray(roles) ? roles : [roles];
    return roleArray.includes(user.role);
}

/**
 * Verifica se usuário é admin
 * @returns {boolean}
 */
function isAdmin() {
    return hasRole('admin');
}

/**
 * Verifica se usuário é bibliotecário
 * @returns {boolean}
 */
function isLibrarian() {
    return hasRole('librarian');
}

/**
 * Verifica se usuário é admin ou bibliotecário
 * @returns {boolean}
 */
function isStaff() {
    return hasRole(['admin', 'librarian']);
}

// ============================================================================
// COMPONENTES DE UI - BADGES E STATUS
// ============================================================================

/**
 * Retorna HTML para badge de status de empréstimo
 * @param {string} status - Status do empréstimo (active, returned, overdue)
 * @param {string} dueDate - Data de vencimento (opcional, para verificar atraso)
 * @returns {string} HTML do badge
 */
function getLoanStatusBadge(status, dueDate = null) {
    // Verifica se está atrasado mesmo com status active
    const overdue = status === 'active' && dueDate && isOverdue(dueDate);

    const badges = {
        'active': overdue
            ? '<span class="badge badge-danger">Atrasado</span>'
            : '<span class="badge badge-warning">Ativo</span>',
        'returned': '<span class="badge badge-success">Devolvido</span>',
        'overdue': '<span class="badge badge-danger">Atrasado</span>'
    };

    return badges[status] || '<span class="badge badge-secondary">Desconhecido</span>';
}

/**
 * Retorna HTML para badge de role de usuário
 * @param {string} role - Role do usuário (user, librarian, admin)
 * @returns {string} HTML do badge
 */
function getRoleBadge(role) {
    const badges = {
        'admin': '<span class="badge badge-danger">Administrador</span>',
        'librarian': '<span class="badge badge-primary">Bibliotecário</span>',
        'user': '<span class="badge badge-secondary">Usuário</span>'
    };

    return badges[role] || '<span class="badge badge-secondary">Desconhecido</span>';
}

/**
 * Retorna HTML para badge de disponibilidade de livro
 * @param {boolean} available - Se o livro está disponível
 * @returns {string} HTML do badge
 */
function getAvailabilityBadge(available) {
    return available
        ? '<span class="badge badge-success">Disponível</span>'
        : '<span class="badge badge-warning">Indisponível</span>';
}

// ============================================================================
// PAGINAÇÃO
// ============================================================================

/**
 * Renderiza controles de paginação
 * @param {Object} pagination - Objeto com {page, total_pages, total_items}
 * @param {Function} onPageChange - Callback chamado ao mudar de página
 * @returns {string} HTML dos controles de paginação
 */
function renderPagination(pagination, onPageChange) {
    if (!pagination || pagination.total_pages <= 1) {
        return '';
    }

    const { page, total_pages } = pagination;
    let html = '<nav><ul class="pagination">';

    // Botão anterior
    html += `
        <li class="page-item ${page === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" data-page="${page - 1}">Anterior</a>
        </li>
    `;

    // Números das páginas
    for (let i = 1; i <= total_pages; i++) {
        // Mostra apenas páginas próximas (para não sobrecarregar com muitas páginas)
        if (i === 1 || i === total_pages || (i >= page - 2 && i <= page + 2)) {
            html += `
                <li class="page-item ${i === page ? 'active' : ''}">
                    <a class="page-link" href="#" data-page="${i}">${i}</a>
                </li>
            `;
        } else if (i === page - 3 || i === page + 3) {
            html += '<li class="page-item disabled"><span class="page-link">...</span></li>';
        }
    }

    // Botão próximo
    html += `
        <li class="page-item ${page === total_pages ? 'disabled' : ''}">
            <a class="page-link" href="#" data-page="${page + 1}">Próximo</a>
        </li>
    `;

    html += '</ul></nav>';

    // Adiciona event listeners após renderizar
    setTimeout(() => {
        document.querySelectorAll('.pagination .page-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const newPage = parseInt(e.target.dataset.page);
                if (newPage && !e.target.parentElement.classList.contains('disabled')) {
                    onPageChange(newPage);
                }
            });
        });
    }, 0);

    return html;
}

// ============================================================================
// VALIDAÇÃO DE FORMULÁRIOS
// ============================================================================

/**
 * Valida email
 * @param {string} email - Email para validar
 * @returns {boolean} True se email é válido
 */
function isValidEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

/**
 * Valida ISBN (10 ou 13 dígitos)
 * @param {string} isbn - ISBN para validar
 * @returns {boolean} True se ISBN é válido
 */
function isValidISBN(isbn) {
    const cleaned = isbn.replace(/[-\s]/g, '');
    return /^\d{10}$/.test(cleaned) || /^\d{13}$/.test(cleaned);
}

/**
 * Mostra erro de validação em campo de formulário
 * @param {HTMLElement} field - Campo do formulário
 * @param {string} message - Mensagem de erro
 */
function showFieldError(field, message) {
    field.classList.add('is-invalid');

    // Remove feedback anterior se existir
    const existingFeedback = field.parentElement.querySelector('.invalid-feedback');
    if (existingFeedback) {
        existingFeedback.remove();
    }

    // Adiciona novo feedback
    const feedback = document.createElement('div');
    feedback.className = 'invalid-feedback';
    feedback.textContent = message;
    field.parentElement.appendChild(feedback);
}

/**
 * Remove erro de validação de campo
 * @param {HTMLElement} field - Campo do formulário
 */
function clearFieldError(field) {
    field.classList.remove('is-invalid');
    const feedback = field.parentElement.querySelector('.invalid-feedback');
    if (feedback) {
        feedback.remove();
    }
}

// ============================================================================
// LOADING E ESTADOS
// ============================================================================

/**
 * Mostra indicador de loading em elemento
 * @param {HTMLElement} element - Elemento para mostrar loading
 * @param {string} message - Mensagem opcional
 */
function showLoading(element, message = 'Carregando...') {
    element.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="sr-only">${message}</span>
            </div>
            <p class="mt-3">${message}</p>
        </div>
    `;
}

/**
 * Mostra mensagem de "sem dados"
 * @param {HTMLElement} element - Elemento para mostrar mensagem
 * @param {string} message - Mensagem personalizada
 */
function showEmptyState(element, message = 'Nenhum item encontrado') {
    element.innerHTML = `
        <div class="text-center py-5 text-muted">
            <i class="fas fa-inbox fa-3x mb-3"></i>
            <p>${message}</p>
        </div>
    `;
}

/**
 * Desabilita botão e mostra loading
 * @param {HTMLButtonElement} button - Botão para desabilitar
 * @param {string} loadingText - Texto durante loading
 * @returns {Function} Função para restaurar estado original
 */
function setButtonLoading(button, loadingText = 'Carregando...') {
    const originalText = button.innerHTML;
    const originalDisabled = button.disabled;

    button.disabled = true;
    button.innerHTML = `
        <span class="spinner-border spinner-border-sm mr-2" role="status" aria-hidden="true"></span>
        ${loadingText}
    `;

    // Retorna função para restaurar estado
    return () => {
        button.disabled = originalDisabled;
        button.innerHTML = originalText;
    };
}

// ============================================================================
// DEBOUNCE E THROTTLE
// ============================================================================

/**
 * Cria função debounced (atrasa execução até parar de chamar)
 * Útil para campos de busca
 * @param {Function} func - Função para debounce
 * @param {number} wait - Tempo de espera em ms
 * @returns {Function} Função debounced
 */
function debounce(func, wait = 300) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Cria função throttled (executa no máximo uma vez por intervalo)
 * Útil para scroll events
 * @param {Function} func - Função para throttle
 * @param {number} wait - Intervalo mínimo em ms
 * @returns {Function} Função throttled
 */
function throttle(func, wait = 300) {
    let timeout = null;
    let previous = 0;

    return function executedFunction(...args) {
        const now = Date.now();
        const remaining = wait - (now - previous);

        if (remaining <= 0 || remaining > wait) {
            if (timeout) {
                clearTimeout(timeout);
                timeout = null;
            }
            previous = now;
            func(...args);
        } else if (!timeout) {
            timeout = setTimeout(() => {
                previous = Date.now();
                timeout = null;
                func(...args);
            }, remaining);
        }
    };
}

// ============================================================================
// TOAST NOTIFICATIONS (OPCIONAL)
// ============================================================================

/**
 * Mostra notificação toast
 * @param {string} message - Mensagem para mostrar
 * @param {string} type - Tipo (success, error, warning, info)
 */
function showToast(message, type = 'info') {
    // Remove toasts antigos
    const existingToast = document.querySelector('.toast-notification');
    if (existingToast) {
        existingToast.remove();
    }

    // Cria toast
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.textContent = message;

    // Estilos inline (pode ser movido para CSS)
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : type === 'warning' ? '#ffc107' : '#17a2b8'};
        color: white;
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        z-index: 9999;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(toast);

    // Remove após 3 segundos
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ============================================================================
// EXPORTAÇÃO GLOBAL
// ============================================================================

window.App = {
    // Formatação
    formatDate,
    formatDateTime,
    isOverdue,

    // Navegação
    navigate,
    requireAuth,
    logout,

    // Gestão de usuário
    getCurrentUser,
    hasRole,
    isAdmin,
    isLibrarian,
    isStaff,

    // UI Components
    getLoanStatusBadge,
    getRoleBadge,
    getAvailabilityBadge,
    renderPagination,

    // Validação
    isValidEmail,
    isValidISBN,
    showFieldError,
    clearFieldError,

    // Loading e estados
    showLoading,
    showEmptyState,
    setButtonLoading,

    // Utilities
    debounce,
    throttle,
    showToast
};
