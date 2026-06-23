"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "../../lib/api";
import { useAuth } from "../../lib/auth";

export default function RegisterPage() {
  const { iniciarSesion } = useAuth();
  const router = useRouter();
  const [nombre, setNombre] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [enviando, setEnviando] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (password.length < 8) {
      setError("La contraseña debe tener al menos 8 caracteres.");
      return;
    }
    setEnviando(true);
    try {
      const auth = await api.register(nombre, email, password);
      iniciarSesion(auth.token, auth.usuario);
      router.replace("/dashboard"); // AC-001-4: redirige sin login manual
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al registrarte.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="auth-pantalla">
      <form className="auth-tarjeta" onSubmit={onSubmit}>
        <h1 className="marca">TramiteFácil</h1>
        <p className="auth-sub">Crea tu cuenta — solo lo esencial</p>

        {error && <div className="alerta">{error}</div>}

        <label>Nombre completo</label>
        <input value={nombre} onChange={(e) => setNombre(e.target.value)} required />

        <label>Correo electrónico</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <label>Contraseña (mínimo 8 caracteres)</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        <button type="submit" disabled={enviando}>
          {enviando ? "Creando cuenta…" : "Crear cuenta"}
        </button>

        <p className="auth-pie">
          ¿Ya tienes cuenta? <Link href="/login">Inicia sesión</Link>
        </p>
      </form>
    </div>
  );
}
