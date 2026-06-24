import React, { createContext, useCallback, useContext, useEffect, useState } from "react";
import { authService } from "../services/authService";
import { setTokens, clearTokens, apiErrorMessage } from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadUser = useCallback(async () => {
    const access = localStorage.getItem("access_token");
    if (!access) {
      setLoading(false);
      return;
    }
    try {
      const me = await authService.me();
      setUser(me);
    } catch {
      clearTokens();
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  const login = async (identifier, password) => {
    try {
      const data = await authService.login(identifier, password);
      setTokens(data);
      setUser(data.user);
      return { success: true };
    } catch (error) {
      return { success: false, message: apiErrorMessage(error, "Incorrect username/email or password.") };
    }
  };

  const register = async (payload) => {
    try {
      const data = await authService.register(payload);
      setTokens(data);
      setUser(data.user);
      return { success: true };
    } catch (error) {
      return { success: false, message: apiErrorMessage(error, "Could not create your account.") };
    }
  };

  const logout = async () => {
    const refresh = localStorage.getItem("refresh_token");
    try {
      if (refresh) await authService.logout(refresh);
    } catch {
      // Ignore network errors on logout; tokens are cleared locally regardless.
    }
    clearTokens();
    setUser(null);
  };

  const updateLocalUser = (patch) => setUser((prev) => ({ ...prev, ...patch }));

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, updateLocalUser, reloadUser: loadUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
