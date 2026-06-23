"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { api, type Usuario } from "./api";

type AuthState = {
  token: string | null;
  usuario: Usuario | null;
  cargando: boolean;
  iniciarSesion: (token: string, usuario: Usuario) => void;
  cerrarSesion: () => void;
};

const AuthContext = createContext<AuthState | null>(null);
const CLAVE = "tramitefacil_auth";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    const guardado = localStorage.getItem(CLAVE);
    if (!guardado) {
      setCargando(false);
      return;
    }
    const { token: t } = JSON.parse(guardado);
    // Valida el token contra el backend antes de confiar en él.
    api
      .me(t)
      .then((u) => {
        setToken(t);
        setUsuario(u);
      })
      .catch(() => localStorage.removeItem(CLAVE))
      .finally(() => setCargando(false));
  }, []);

  const iniciarSesion = (t: string, u: Usuario) => {
    localStorage.setItem(CLAVE, JSON.stringify({ token: t, usuario: u }));
    setToken(t);
    setUsuario(u);
  };

  const cerrarSesion = () => {
    if (token) api.logout(token).catch(() => {});
    localStorage.removeItem(CLAVE);
    setToken(null);
    setUsuario(null);
  };

  return (
    <AuthContext.Provider
      value={{ token, usuario, cargando, iniciarSesion, cerrarSesion }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth debe usarse dentro de AuthProvider");
  return ctx;
}
