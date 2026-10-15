import axios from "axios";

// The token lives only in this browser's localStorage, never in the bundle:
// the dev server is reachable by others and would serve it to them.
export const TOKEN_STORAGE_KEY = "agenticseek_api_token";

const listeners = new Set();

/** Returns the saved API token, or null when none is saved. */
export const getToken = () => localStorage.getItem(TOKEN_STORAGE_KEY);

/** Saves the API token that later backend requests will carry. */
export const saveToken = (token) =>
  localStorage.setItem(TOKEN_STORAGE_KEY, token);

/** Forgets the saved API token. */
export const clearToken = () => localStorage.removeItem(TOKEN_STORAGE_KEY);

/**
 * Registers `listener({ tokenRejected })`, called when the backend answers
 * 401 to a request that carried the current token (or no token when none is
 * saved). `tokenRejected` is true when a saved token was refused.
 * Returns a function that unregisters the listener.
 */
export const onAuthRequired = (listener) => {
  listeners.add(listener);
  return () => listeners.delete(listener);
};

const bearer = (token) => (token ? `Bearer ${token}` : null);

const attachToken = (config) => {
  const token = getToken();
  if (token) config.headers.set("Authorization", bearer(token));
  return config;
};

const reportUnauthorized = (error) => {
  if (error.response?.status !== 401) return Promise.reject(error);
  const current = bearer(getToken());
  const sent = error.config.headers.get("Authorization") ?? null;
  // A 401 for a token that was replaced meanwhile says nothing about the new one.
  if (sent === current) {
    listeners.forEach((listener) =>
      listener({ tokenRejected: current !== null })
    );
  }
  return Promise.reject(error);
};

axios.interceptors.request.use(attachToken);
axios.interceptors.response.use(undefined, reportUnauthorized);
