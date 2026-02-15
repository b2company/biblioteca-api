/**
 * Configuração de ambiente do frontend.
 *
 * Detecta automaticamente se está rodando em localhost (desenvolvimento)
 * ou em produção (Vercel) e configura a URL base da API.
 */

// Detecta o ambiente baseado no hostname
const isLocalhost = window.location.hostname === 'localhost' ||
                    window.location.hostname === '127.0.0.1';

// Define a URL base da API
const API_BASE_URL = isLocalhost
  ? 'http://localhost:8000'  // Desenvolvimento
  : window.location.origin + '/api';  // Produção (Vercel)

// Log para debug (remova em produção se preferir)
console.log('Ambiente:', isLocalhost ? 'Development' : 'Production');
console.log('API Base URL:', API_BASE_URL);

// Exporta para uso global
window.API_BASE_URL = API_BASE_URL;
