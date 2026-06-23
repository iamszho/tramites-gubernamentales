# Epics y User Stories
**Proyecto:** TramiteFácil  
**Versión:** 1.0  
**Fecha:** 2026-03-15  
**Autor:** [Tu nombre]  
**Estado:** Draft

**Referencia cruzada:** `02_Requirements/BRD.md` — requerimientos funcionales de origen

---

## Convenciones

**Formato de User Story:**
> Como [tipo de usuario], quiero [acción], para [beneficio].

**Criterios de Aceptación (AC):** Condiciones verificables que determinan si la historia está completa. Cada AC debe poder responderse con ✅ sí / ❌ no.

**Prioridad:** Alta / Media / Baja — define el orden de desarrollo dentro del sprint.

**Estado:** 🔲 Pendiente · 🔄 En progreso · ✅ Completo

---

## Epic 1 — Autenticación y Gestión de Cuenta

**Descripción:** El usuario puede crear una cuenta, acceder a ella de forma segura y recuperarla si pierde el acceso. Este Epic es prerequisito de todos los demás.

**Requerimientos funcionales origen:** RF-001 al RF-006

---

### US-001 — Registro de usuario nuevo
**Prioridad:** Alta | **Estado:** 🔲

> Como ciudadano sin cuenta, quiero registrarme con mi nombre, correo y contraseña, para poder guardar mis trámites y acceder a mi historial.

**Criterios de Aceptación:**
- AC-001-1: El formulario de registro solicita únicamente: nombre completo, correo electrónico y contraseña.
- AC-001-2: Si el correo ya existe en el sistema, se muestra un mensaje de error claro antes de crear la cuenta.
- AC-001-3: La contraseña debe tener mínimo 8 caracteres. Si no cumple, se muestra el requisito al usuario.
- AC-001-4: Al completar el registro exitosamente, el usuario es redirigido al dashboard sin necesidad de iniciar sesión manualmente.
- AC-001-5: El sistema no solicita ningún dato adicional (teléfono, ubicación, etc.) durante el registro.

---

### US-002 — Inicio de sesión
**Prioridad:** Alta | **Estado:** 🔲

> Como usuario registrado, quiero iniciar sesión con mi correo y contraseña, para acceder a mis trámites guardados.

**Criterios de Aceptación:**
- AC-002-1: El formulario de login solicita correo y contraseña.
- AC-002-2: Si las credenciales son incorrectas, se muestra un mensaje de error genérico (no especifica cuál campo es incorrecto por seguridad).
- AC-002-3: Después de 5 intentos fallidos consecutivos, el sistema bloquea el intento por 5 minutos y lo indica al usuario.
- AC-002-4: Al iniciar sesión exitosamente, el usuario es redirigido a su dashboard.

---

### US-003 — Cierre de sesión
**Prioridad:** Alta | **Estado:** 🔲

> Como usuario autenticado, quiero cerrar mi sesión, para proteger mi cuenta cuando uso un dispositivo compartido.

**Criterios de Aceptación:**
- AC-003-1: Existe una opción visible de "Cerrar sesión" accesible desde cualquier pantalla de la plataforma.
- AC-003-2: Al cerrar sesión, el usuario es redirigido a la pantalla de inicio/login.
- AC-003-3: Tras cerrar sesión, el usuario no puede acceder a rutas protegidas sin volver a autenticarse.

---

### US-004 — Recuperación de contraseña
**Prioridad:** Media | **Estado:** 🔲

> Como usuario que olvidó su contraseña, quiero recibir un enlace de recuperación en mi correo, para poder volver a acceder a mi cuenta.

**Criterios de Aceptación:**
- AC-004-1: Existe un enlace de "¿Olvidaste tu contraseña?" visible en la pantalla de login.
- AC-004-2: El sistema solicita únicamente el correo registrado para enviar el enlace.
- AC-004-3: Si el correo no existe en el sistema, el mensaje de respuesta es el mismo que si existiera (no revela si el correo está registrado).
- AC-004-4: El enlace de recuperación expira en 24 horas.
- AC-004-5: Una vez usada el enlace, este queda inválido para usos posteriores.

---

## Epic 2 — Gestión de Trámites

**Descripción:** El usuario puede crear, visualizar y eliminar espacios de trabajo para sus trámites. Cada trámite agrupa el historial de chat y el contexto de esa gestión específica.

**Requerimientos funcionales origen:** RF-007 al RF-012

---

### US-005 — Ver catálogo de trámites disponibles
**Prioridad:** Alta | **Estado:** 🔲

> Como usuario autenticado, quiero ver los trámites vehiculares disponibles en la plataforma, para elegir el que necesito realizar.

**Criterios de Aceptación:**
- AC-005-1: El dashboard muestra los 3 trámites disponibles: Licencia de conducir, Verificación vehicular, Cambio de placas.
- AC-005-2: Cada trámite muestra al menos: nombre, ícono o imagen representativa y una descripción de una línea.
- AC-005-3: El catálogo es visible en la pantalla principal sin necesidad de navegar a una sección diferente.

---

### US-006 — Crear nuevo espacio de trabajo para un trámite
**Prioridad:** Alta | **Estado:** 🔲

> Como usuario autenticado, quiero crear un espacio de trabajo para un trámite, para tener un chat dedicado donde resolver mis dudas sobre ese proceso.

**Criterios de Aceptación:**
- AC-006-1: Al seleccionar un trámite del catálogo, el sistema crea automáticamente un espacio de trabajo y redirige al usuario al chat.
- AC-006-2: Si el usuario ya tiene un espacio activo para ese trámite, el sistema lo redirige al existente en lugar de crear uno nuevo.
- AC-006-3: El espacio de trabajo muestra el nombre del trámite de forma clara en la interfaz.
- AC-006-4: El espacio de trabajo se crea con el historial de chat vacío.

---

### US-007 — Ver trámites activos en el dashboard
**Prioridad:** Alta | **Estado:** 🔲

> Como usuario autenticado, quiero ver todos mis trámites activos en una vista central, para acceder rápidamente a los que ya inicié.

**Criterios de Aceptación:**
- AC-007-1: El dashboard muestra una lista de los trámites que el usuario ha creado.
- AC-007-2: Cada trámite en la lista muestra: nombre del trámite y fecha de creación.
- AC-007-3: Al hacer clic en un trámite de la lista, el usuario accede a su espacio de trabajo y retoma el historial de chat.
- AC-007-4: Si el usuario no tiene trámites creados, se muestra un mensaje de invitación a crear el primero.

---

### US-008 — Eliminar un trámite
**Prioridad:** Media | **Estado:** 🔲

> Como usuario, quiero eliminar un trámite que ya no necesito, para mantener mi dashboard ordenado.

**Criterios de Aceptación:**
- AC-008-1: Cada trámite en el dashboard tiene una opción para eliminarlo.
- AC-008-2: Antes de eliminar, el sistema muestra un mensaje de confirmación que advierte que se perderá el historial de chat.
- AC-008-3: Tras la confirmación, el trámite y su historial son eliminados y el usuario regresa al dashboard.
- AC-008-4: Si el usuario cancela la confirmación, el trámite no se elimina.

---

## Epic 3 — Chatbot de Asistencia Vehicular

**Descripción:** El núcleo del MVP. El usuario puede hacer preguntas en lenguaje natural sobre su trámite y recibir respuestas factuales, dentro de los límites definidos de la knowledge base.

**Requerimientos funcionales origen:** RF-013 al RF-019

---

### US-009 — Hacer preguntas al chatbot sobre el trámite
**Prioridad:** Alta | **Estado:** 🔲

> Como usuario dentro de un espacio de trámite, quiero hacer preguntas en lenguaje natural al chatbot, para resolver mis dudas sobre qué necesito y cómo hacer el trámite.

**Criterios de Aceptación:**
- AC-009-1: La interfaz del chat tiene un campo de texto y un botón de envío visibles.
- AC-009-2: El chatbot responde en menos de 5 segundos en condiciones normales de red.
- AC-009-3: El chatbot puede responder preguntas sobre: documentos requeridos, costos, vigencia, lugares de atención, horarios y requisitos previos del trámite activo.
- AC-009-4: Las respuestas están en español y en tono conversacional, sin lenguaje burocrático.
- AC-009-5: El usuario puede enviar múltiples preguntas de forma consecutiva sin recargar la página.

---

### US-010 — El chatbot rechaza preguntas fuera de su dominio
**Prioridad:** Alta | **Estado:** 🔲

> Como usuario, quiero que el chatbot me avise cuando no puede responder algo, para no actuar con información incorrecta o incompleta.

**Criterios de Aceptación:**
- AC-010-1: Si el usuario pregunta sobre un trámite fuera del dominio (SAT, INE, IMSS, etc.), el chatbot indica que no cubre ese tema en esta versión y sugiere al usuario buscar en el portal oficial correspondiente.
- AC-010-2: Si el chatbot no tiene información suficiente para responder una pregunta dentro de su dominio, declara explícitamente que no cuenta con esa información, en lugar de inventar una respuesta.
- AC-010-3: El chatbot nunca presenta información inventada como si fuera factual.
- AC-010-4: Cuando el chatbot redirige al usuario a fuentes externas, proporciona el nombre del portal oficial relevante.

---

### US-011 — Disclaimer de información visible antes de interactuar
**Prioridad:** Alta | **Estado:** 🔲

> Como usuario, quiero ver un aviso claro sobre la naturaleza de la información del chatbot, para saber que debo verificar datos críticos antes de ir a un módulo.

**Criterios de Aceptación:**
- AC-011-1: El aviso aparece en la interfaz del chat antes de que el usuario envíe su primera pregunta.
- AC-011-2: El aviso indica de forma clara y concisa que la información puede no reflejar cambios recientes en los requisitos del trámite.
- AC-011-3: El aviso recomienda verificar la información en el portal oficial antes de acudir al módulo.
- AC-011-4: El aviso no desaparece ni se oculta tras la primera interacción — permanece visible (puede ser en un banner o nota al pie de la interfaz).

---

### US-012 — Persistencia del historial de chat en sesión
**Prioridad:** Media | **Estado:** 🔲

> Como usuario, quiero que mi conversación con el chatbot se mantenga cuando regreso a un trámite, para no perder el contexto de mis preguntas anteriores.

**Criterios de Aceptación:**
- AC-012-1: Al regresar a un trámite previamente creado, el historial de chat de sesiones anteriores es visible.
- AC-012-2: El historial muestra los mensajes del usuario y las respuestas del chatbot en orden cronológico.
- AC-012-3: El historial se mantiene mientras el trámite no haya sido eliminado.

---

## Epic 4 — Perfil Progresivo

**Descripción:** El usuario no es bombardeado con preguntas de datos personales en el onboarding. Los datos adicionales (ubicación, teléfono) se solicitan solo cuando el contexto del trámite los hace relevantes.

**Requerimientos funcionales origen:** RF-020 al RF-022

---

### US-013 — Solicitud contextual de ubicación
**Prioridad:** Media | **Estado:** 🔲

> Como usuario, quiero que el sistema me pida mi ubicación solo cuando sea útil para recomendarme módulos cercanos, para no dar información que no es necesaria desde el inicio.

**Criterios de Aceptación:**
- AC-013-1: Durante el registro no se solicita ubicación.
- AC-013-2: La ubicación se solicita únicamente cuando el chatbot necesita sugerir módulos de atención cercanos al usuario.
- AC-013-3: La solicitud de ubicación incluye una explicación de por qué se necesita ese dato en ese momento.
- AC-013-4: El usuario puede optar por no proporcionar su ubicación y el chatbot responde con información general de módulos sin filtrar por zona.

---

### US-014 — Editar datos de perfil
**Prioridad:** Baja | **Estado:** 🔲

> Como usuario, quiero poder editar mis datos de perfil (nombre, correo, datos adicionales), para mantener mi información correcta.

**Criterios de Aceptación:**
- AC-014-1: Existe una sección de perfil accesible desde el dashboard.
- AC-014-2: El usuario puede actualizar su nombre.
- AC-014-3: El usuario puede actualizar su correo, previa verificación del nuevo correo.
- AC-014-4: El usuario puede eliminar datos opcionales que haya proporcionado previamente (ubicación, teléfono).

---

## Resumen del Backlog

| ID | Historia | Epic | Prioridad | Estado |
|---|---|---|---|---|
| US-001 | Registro de usuario nuevo | Auth | Alta | 🔲 |
| US-002 | Inicio de sesión | Auth | Alta | 🔲 |
| US-003 | Cierre de sesión | Auth | Alta | 🔲 |
| US-004 | Recuperación de contraseña | Auth | Media | 🔲 |
| US-005 | Ver catálogo de trámites | Trámites | Alta | 🔲 |
| US-006 | Crear espacio de trabajo | Trámites | Alta | 🔲 |
| US-007 | Ver trámites activos en dashboard | Trámites | Alta | 🔲 |
| US-008 | Eliminar un trámite | Trámites | Media | 🔲 |
| US-009 | Hacer preguntas al chatbot | Chatbot | Alta | 🔲 |
| US-010 | Chatbot rechaza preguntas fuera de dominio | Chatbot | Alta | 🔲 |
| US-011 | Disclaimer de información visible | Chatbot | Alta | 🔲 |
| US-012 | Persistencia del historial de chat | Chatbot | Media | 🔲 |
| US-013 | Solicitud contextual de ubicación | Perfil | Media | 🔲 |
| US-014 | Editar datos de perfil | Perfil | Baja | 🔲 |

**Total historias MVP:** 14  
**Historias Alta prioridad:** 9 — estas conforman el núcleo mínimo del producto.

---

*Para el detalle de requerimientos funcionales de cada historia, ver `BRD.md §5`.*  
*Para la planificación de sprints, ver `04_Planning/backlog.md` (pendiente).*
