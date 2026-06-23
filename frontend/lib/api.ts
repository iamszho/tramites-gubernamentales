// Se usa 127.0.0.1 (IPv4) en vez de "localhost": en muchos sistemas Linux
// "localhost" resuelve a ::1 (IPv6) y uvicorn, por defecto, solo escucha en
// 127.0.0.1 (IPv4), lo que haría que el navegador no pudiera conectar.
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export type Usuario = { id: number; nombre: string; email: string };
export type Auth = { token: string; usuario: Usuario };
export type TramiteCatalogo = {
  id: string;
  nombre: string;
  descripcion: string;
  icono: string;
};
export type Workspace = {
  id: number;
  tramite_id: string;
  nombre: string;
  icono: string;
  created_at: string;
};
export type Mensaje = { rol: string; contenido: string; created_at: string };
export type WorkspaceDetalle = Workspace & {
  disclaimer: string;
  mensajes: Mensaje[];
};

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function pedir<T>(
  ruta: string,
  opciones: RequestInit = {},
  token?: string
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(opciones.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  let resp: Response;
  try {
    resp = await fetch(`${API_URL}${ruta}`, { ...opciones, headers });
  } catch {
    throw new ApiError(0, `No se pudo conectar con el servidor (${API_URL}).`);
  }

  if (resp.status === 204) return undefined as T;

  const datos = await resp.json().catch(() => ({}));
  if (!resp.ok) {
    const detalle =
      typeof datos?.detail === "string"
        ? datos.detail
        : "Ocurrió un error inesperado.";
    throw new ApiError(resp.status, detalle);
  }
  return datos as T;
}

export const api = {
  register: (nombre: string, email: string, password: string) =>
    pedir<Auth>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ nombre, email, password }),
    }),
  login: (email: string, password: string) =>
    pedir<Auth>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  logout: (token: string) =>
    pedir<void>("/auth/logout", { method: "POST" }, token),
  me: (token: string) => pedir<Usuario>("/auth/me", {}, token),

  catalogo: (token: string) =>
    pedir<TramiteCatalogo[]>("/catalogo", {}, token),
  workspaces: (token: string) => pedir<Workspace[]>("/tramites", {}, token),
  crearWorkspace: (token: string, tramite_id: string) =>
    pedir<Workspace>(
      "/tramites",
      { method: "POST", body: JSON.stringify({ tramite_id }) },
      token
    ),
  verWorkspace: (token: string, id: number) =>
    pedir<WorkspaceDetalle>(`/tramites/${id}`, {}, token),
  eliminarWorkspace: (token: string, id: number) =>
    pedir<void>(`/tramites/${id}`, { method: "DELETE" }, token),
  chat: (token: string, id: number, mensaje: string) =>
    pedir<Mensaje>(
      `/tramites/${id}/chat`,
      { method: "POST", body: JSON.stringify({ mensaje }) },
      token
    ),
};
