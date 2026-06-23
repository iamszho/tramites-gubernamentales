"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  api,
  type TramiteCatalogo,
  type Workspace,
} from "../../lib/api";
import { useAuth } from "../../lib/auth";

export default function DashboardPage() {
  const { token, usuario, cargando, cerrarSesion } = useAuth();
  const router = useRouter();
  const [catalogo, setCatalogo] = useState<TramiteCatalogo[]>([]);
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [error, setError] = useState("");
  const [cargandoDatos, setCargandoDatos] = useState(true);

  useEffect(() => {
    if (!cargando && !usuario) router.replace("/login");
  }, [cargando, usuario, router]);

  const cargar = useCallback(async () => {
    if (!token) return;
    try {
      const [cat, ws] = await Promise.all([
        api.catalogo(token),
        api.workspaces(token),
      ]);
      setCatalogo(cat);
      setWorkspaces(ws);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al cargar.");
    } finally {
      setCargandoDatos(false);
    }
  }, [token]);

  useEffect(() => {
    if (token) cargar();
  }, [token, cargar]);

  async function abrir(tramiteId: string) {
    if (!token) return;
    try {
      const ws = await api.crearWorkspace(token, tramiteId);
      router.push(`/tramite/${ws.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al abrir el trámite.");
    }
  }

  async function eliminar(id: number, e: React.MouseEvent) {
    e.stopPropagation();
    if (!token) return;
    if (!confirm("¿Eliminar este trámite? Se perderá el historial de chat.")) return;
    try {
      await api.eliminarWorkspace(token, id);
      setWorkspaces((prev) => prev.filter((w) => w.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al eliminar.");
    }
  }

  if (cargando || !usuario) return <div className="centro-cargando">Cargando…</div>;

  return (
    <div className="app-shell">
      <header className="barra-superior">
        <span className="marca-pequena">TramiteFácil</span>
        <div className="barra-derecha">
          <span className="usuario-nombre">Hola, {usuario.nombre}</span>
          <button className="btn-texto" onClick={cerrarSesion}>
            Cerrar sesión
          </button>
        </div>
      </header>

      <main className="contenido">
        {error && <div className="alerta">{error}</div>}

        <section>
          <h2>Trámites disponibles</h2>
          <p className="seccion-sub">Elige un trámite para abrir tu asistente.</p>
          <div className="grid-tarjetas">
            {catalogo.map((t) => (
              <button key={t.id} className="tarjeta-tramite" onClick={() => abrir(t.id)}>
                <span className="icono">{t.icono}</span>
                <span className="tarjeta-nombre">{t.nombre}</span>
                <span className="tarjeta-desc">{t.descripcion}</span>
              </button>
            ))}
          </div>
        </section>

        <section>
          <h2>Mis trámites</h2>
          {cargandoDatos ? (
            <p className="seccion-sub">Cargando…</p>
          ) : workspaces.length === 0 ? (
            <p className="vacio-lista">
              Aún no has iniciado ningún trámite. Elige uno de arriba para empezar.
            </p>
          ) : (
            <ul className="lista-workspaces">
              {workspaces.map((w) => (
                <li
                  key={w.id}
                  className="item-workspace"
                  onClick={() => router.push(`/tramite/${w.id}`)}
                >
                  <span className="icono">{w.icono}</span>
                  <span className="item-info">
                    <span className="item-nombre">{w.nombre}</span>
                    <span className="item-fecha">Creado: {w.created_at}</span>
                  </span>
                  <button
                    className="btn-eliminar"
                    onClick={(e) => eliminar(w.id, e)}
                    aria-label="Eliminar trámite"
                  >
                    Eliminar
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>
      </main>
    </div>
  );
}
