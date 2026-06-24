import { api } from "./api";

export const authService = {
  login: (identifier, password) => api.post("/auth/login", { identifier, password }).then((r) => r.data),
  register: (payload) => api.post("/auth/register", payload).then((r) => r.data),
  logout: (refresh_token) => api.post("/auth/logout", { refresh_token }).then((r) => r.data),
  forgotPassword: (email) => api.post("/auth/forgot-password", { email }).then((r) => r.data),
  resetPassword: (token, new_password) => api.post("/auth/reset-password", { token, new_password }).then((r) => r.data),
  me: () => api.get("/auth/me").then((r) => r.data),
};
