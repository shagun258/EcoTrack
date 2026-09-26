import axios, { AxiosError } from "axios";

export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({ baseURL: API_URL });

function getStoredTokens() {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem("ecotrack_tokens");
  return raw ? (JSON.parse(raw) as { access_token: string; refresh_token: string }) : null;
}

function storeTokens(tokens: { access_token: string; refresh_token: string }) {
  localStorage.setItem("ecotrack_tokens", JSON.stringify(tokens));
}

export function clearTokens() {
  localStorage.removeItem("ecotrack_tokens");
}

api.interceptors.request.use((config) => {
  const tokens = getStoredTokens();
  if (tokens?.access_token) {
    config.headers.Authorization = `Bearer ${tokens.access_token}`;
  }
  return config;
});

// If a request 401s, try to silently refresh the access token once, then retry.
let refreshPromise: Promise<string | null> | null = null;

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as (typeof error.config & { _retried?: boolean }) | undefined;
    if (error.response?.status !== 401 || !original || original._retried) {
      throw error;
    }

    const tokens = getStoredTokens();
    if (!tokens?.refresh_token) throw error;

    original._retried = true;

    if (!refreshPromise) {
      refreshPromise = axios
        .post(`${API_URL}/api/auth/refresh`, { refresh_token: tokens.refresh_token })
        .then((res) => {
          storeTokens(res.data);
          return res.data.access_token as string;
        })
        .catch(() => {
          clearTokens();
          return null;
        })
        .finally(() => {
          refreshPromise = null;
        });
    }

    const newAccessToken = await refreshPromise;
    if (!newAccessToken) throw error;

    original.headers = original.headers ?? {};
    original.headers.Authorization = `Bearer ${newAccessToken}`;
    return api.request(original);
  }
);

export { storeTokens };
