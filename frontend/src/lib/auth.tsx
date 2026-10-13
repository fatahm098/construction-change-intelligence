"use client";

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import type { User } from "./types";
import {
  clearToken,
  fetchMe,
  getToken,
  login as apiLogin,
  logout as apiLogout,
  register as apiRegister,
} from "./api";

/**
 * Apakah autentikasi dipaksa aktif di UI.
 * Sumbernya env NEXT_PUBLIC_AUTH_ENABLED (selaras dengan backend `auth_enabled`).
 * Saat false (default Fase 4), UI tetap menampilkan halaman publik dan TIDAK
 * memaksa redirect global — login hanya perlu bila user membukanya sendiri.
 */
export const AUTH_ENABLED = process.env.NEXT_PUBLIC_AUTH_ENABLED === "true";

interface AuthContextValue {
  user: User | null;
  token: string | null;
  /** true selama sesi awal dihidrasi dari token tersimpan. */
  loading: boolean;
  authEnabled: boolean;
  login: (email: string, password: string) => Promise<User>;
  register: (email: string, password: string, fullName?: string) => Promise<User>;
  logout: () => void;
  refresh: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setTokenState] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    const current = getToken();
    setTokenState(current);
    if (!current) {
      setUser(null);
      return;
    }
    try {
      setUser(await fetchMe());
    } catch {
      // Token kedaluwarsa/invalid → bersihkan, jangan paksa redirect.
      clearToken();
      setTokenState(null);
      setUser(null);
    }
  }, []);

  useEffect(() => {
    let active = true;
    (async () => {
      await refresh();
      if (active) setLoading(false);
    })();
    return () => {
      active = false;
    };
  }, [refresh]);

  const login = useCallback(async (email: string, password: string) => {
    const res = await apiLogin({ email, password });
    setTokenState(res.access_token);
    setUser(res.user);
    return res.user;
  }, []);

  const register = useCallback(
    async (email: string, password: string, fullName?: string) => {
      return apiRegister({ email, password, full_name: fullName || null });
    },
    [],
  );

  const logout = useCallback(() => {
    apiLogout();
    setTokenState(null);
    setUser(null);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      loading,
      authEnabled: AUTH_ENABLED,
      login,
      register,
      logout,
      refresh,
    }),
    [user, token, loading, login, register, logout, refresh],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth harus dipakai di dalam <AuthProvider>.");
  }
  return ctx;
}
