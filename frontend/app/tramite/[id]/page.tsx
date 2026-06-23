"use client";

import { useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { api, type Mensaje } from "../../../lib/api";
import { useAuth } from "../../../lib/auth";

export default function TramitePage() {
  const { token, usuario, cargando, cerrarSesion } = useAuth();
  const router = useRouter();
  const params = useParams();
  const workspaceId = Number(params.id);

  const [nombre, setNombre] = useState("");
  const [icono, setIcono] = useState("");
  const [disclaimer, setDisclaimer] = useState("");
  const [mensajes, setMensajes] = useState<Mensaje[]>([]);
  const [entrada, setEntrada] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState("");
  const [cargandoWs, setCargandoWs] = useState(true);
  const finRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!cargando && !usuario) router.replace("/login");
  }, [cargando, usuario, router]);

  useEffect(() => {
    if (!token || Number.isNaN(workspaceId)) return;
    api
      .verWorkspace(token, workspaceId)
      .then((ws) => {
        setNombre(ws.nombre);
        setIcono(ws.icono);
        setDisclaimer(ws.disclaimer);
        setMensajes(ws.mensajes);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Error al cargar."))
      .finally(() => setCargandoWs(false));
  }, [token, workspaceId]);

  useEffect(() => {
    requestAnimationFrame(() =>
      finRef.current?.scrollIntoView({ behavior: "smooth" })
    );
  }, [mensajes, enviando]);

  async function enviar(e: React.FormEvent) {
    e.preventDefault();
    const texto = entrada.trim();
    if (!texto || !token || enviando) return;

    setError("");
    setEntrada("");
    setMensajes((prev) => [
      ...prev,
      { rol: "user", contenido: texto, created_at: "" },
    ]);
    setEnviando(true);
    try {
      const respuesta = await api.chat(token, workspaceId, texto);
      setMensajes((prev) => [...prev, respuesta]);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "El asistente no está disponible."
      );
    } finally {
      setEnviando(false);
    }
  }

  if (cargando || !usuario) return <div className="centro-cargando">Cargando…</div>;

  return (
    <div className="app-shell">
      <header className="barra-superior">
        <Link href="/dashboard" className="btn-texto">
          ← Mis trámites
        </Link>
        <div className="barra-derecha">
          <span className="usuario-nombre">{usuario.nombre}</span>
          <button className="btn-texto" onClick={cerrarSesion}>
            Cerrar sesión
          </button>
        </div>
      </header>

      <div className="chat-encabezado">
        <span className="icono">{icono}</span>
        <h2>{nombre}</h2>
      </div>

      {/* US-011: disclaimer visible y permanente */}
      {disclaimer && <div className="disclaimer">⚠️ {disclaimer}</div>}

      <div className="chat-mensajes">
        {cargandoWs ? (
          <div className="vacio">Cargando…</div>
        ) : mensajes.length === 0 ? (
          <div className="vacio">
            Pregúntame sobre <strong>{nombre.toLowerCase()}</strong>: documentos,
            costos, requisitos, dónde y cómo hacerlo.
          </div>
        ) : (
          mensajes.map((m, i) => (
            <div key={i} className={`burbuja ${m.rol === "user" ? "usuario" : "bot"}`}>
              {m.contenido}
            </div>
          ))
        )}
        {enviando && <div className="cargando">Escribiendo…</div>}
        {error && <div className="burbuja error">{error}</div>}
        <div ref={finRef} />
      </div>

      <form className="entrada" onSubmit={enviar}>
        <input
          value={entrada}
          onChange={(e) => setEntrada(e.target.value)}
          placeholder={`Escribe tu pregunta sobre ${nombre.toLowerCase()}…`}
          disabled={enviando || cargandoWs}
        />
        <button type="submit" disabled={enviando || cargandoWs || !entrada.trim()}>
          Enviar
        </button>
      </form>
    </div>
  );
}
