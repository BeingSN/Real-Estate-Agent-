// Dev: leave empty — Vite proxies /api → http://localhost:8000
// Prod: set VITE_API_BASE_URL=http://localhost:8000 in .env
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''
