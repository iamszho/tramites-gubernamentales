# BRD — Business Requirements Document
**Proyecto:** TramiteFácil  
**Versión:** 1.0  
**Fecha:** 2026-03-15  
**Autor:** [Tu nombre]  
**Estado:** Draft

**Referencias cruzadas:**
- `00_Project_Charter/problem_statement.md` — contexto y alcance
- `01_Discovery/user_personas.md` — perfiles de usuario
- `02_Requirements/epics_and_stories.md` — descomposición detallada

---

## 1. Propósito del Documento

Este documento define **qué debe hacer el sistema** desde la perspectiva del negocio y del usuario, sin entrar en decisiones de implementación técnica. Es la fuente de verdad para el equipo de desarrollo sobre el alcance funcional del MVP.

Cualquier funcionalidad no descrita en este documento está fuera del alcance del MVP y requiere aprobación explícita para ser incorporada.

---

## 2. Contexto y Resumen Ejecutivo

TramiteFácil es una plataforma web que ayuda a ciudadanos mexicanos a prepararse para realizar trámites vehiculares (licencia de conducir, verificación vehicular, cambio de placas) mediante un chatbot especializado que responde preguntas factuales en lenguaje natural.

El MVP resuelve un problema concreto y acotado: el ciudadano no sabe qué llevar, cuánto cuesta, ni dónde ir — y busca esa información en fuentes dispersas e inconsistentes. TramiteFácil centraliza esa información en una interfaz conversacional de bajo roce.

---

## 3. Stakeholders

| Rol | Descripción | Responsabilidad en este proyecto |
|---|---|---|
| Product Owner | Responsable del producto y sus decisiones | Define prioridades, aprueba requerimientos |
| Developer | Equipo de desarrollo (puede ser el mismo PO en proyecto personal) | Implementa y valida los requerimientos |
| Usuario final | Ciudadano mexicano que realiza trámites vehiculares | Beneficiario del sistema |

---

## 4. Alcance del MVP

### 4.1 Incluido

| # | Módulo | Descripción |
|---|---|---|
| M1 | Autenticación | Registro, inicio de sesión, cierre de sesión y recuperación de contraseña |
| M2 | Gestión de trámites | Creación, visualización y eliminación del espacio de trabajo por trámite |
| M3 | Chatbot de asistencia | Asistente conversacional acotado a los 3 trámites vehiculares del MVP |
| M4 | Perfil progresivo | Recopilación de datos adicionales del usuario de forma contextual, no en el onboarding |

### 4.2 Explícitamente fuera del alcance

| Feature | Versión destino |
|---|---|
| Llenado asistido de formularios PDF (Chat Form) | V2 |
| Catálogo descargable de documentos | V2 |
| Sección de opiniones sobre módulos | V3 |
| Trámites no vehiculares (SAT, INE, IMSS, etc.) | V2+ |
| Aplicación móvil nativa | No definido |
| Agendamiento de citas | Fuera del roadmap |

---

## 5. Requerimientos Funcionales por Módulo

### M1 — Autenticación

**Objetivo de negocio:** Permitir que el usuario tenga una sesión persistente y segura para guardar sus trámites activos.

| ID | Requerimiento | Prioridad |
|---|---|---|
| RF-001 | El sistema debe permitir registrar un usuario nuevo con nombre, correo electrónico y contraseña | Alta |
| RF-002 | El sistema debe validar que el correo no esté registrado previamente antes de crear la cuenta | Alta |
| RF-003 | El sistema debe permitir iniciar sesión con correo y contraseña | Alta |
| RF-004 | El sistema debe permitir cerrar sesión en cualquier momento | Alta |
| RF-005 | El sistema debe ofrecer un flujo de recuperación de contraseña vía correo electrónico | Media |
| RF-006 | El sistema debe mantener la sesión activa entre visitas (recordar sesión) | Media |

---

### M2 — Gestión de Trámites

**Objetivo de negocio:** Dar al usuario un espacio de trabajo dedicado por trámite para que su contexto e historial de chat sean persistentes y organizados.

| ID | Requerimiento | Prioridad |
|---|---|---|
| RF-007 | El sistema debe mostrar al usuario un catálogo con los 3 trámites disponibles (licencia, verificación, cambio de placas) | Alta |
| RF-008 | El sistema debe permitir al usuario crear un espacio de trabajo para un trámite seleccionado | Alta |
| RF-009 | El sistema debe mostrar en el dashboard todos los trámites activos del usuario | Alta |
| RF-010 | El sistema debe permitir al usuario acceder a un trámite previo y retomar su historial de chat | Alta |
| RF-011 | El sistema debe permitir al usuario eliminar un trámite de su lista | Media |
| RF-012 | El sistema debe impedir que el usuario cree dos espacios de trabajo para el mismo trámite de forma simultánea | Baja |

---

### M3 — Chatbot de Asistencia

**Objetivo de negocio:** Resolver las dudas del usuario sobre su trámite en lenguaje natural, con información factual, sin que el usuario tenga que navegar portales gubernamentales.

| ID | Requerimiento | Prioridad |
|---|---|---|
| RF-013 | El sistema debe presentar una interfaz de chat dentro de cada espacio de trámite | Alta |
| RF-014 | El chatbot debe responder preguntas sobre el trámite activo: documentos requeridos, costos, vigencia, lugares de atención, horarios y requisitos previos | Alta |
| RF-015 | El chatbot debe responder únicamente sobre los trámites vehiculares del MVP. Si el usuario pregunta sobre otro tema, debe indicarlo claramente y redirigir | Alta |
| RF-016 | El chatbot debe declarar explícitamente cuando no tiene información suficiente para responder una pregunta, en lugar de inventar una respuesta | Alta |
| RF-017 | El sistema debe mostrar un aviso visible en la interfaz del chat indicando que la información puede no reflejar cambios recientes | Alta |
| RF-018 | El historial de conversación debe persistir dentro de la sesión del usuario para ese trámite | Media |
| RF-019 | El chatbot debe responder en español y con un tono conversacional, sin lenguaje burocrático | Media |

---

### M4 — Perfil Progresivo

**Objetivo de negocio:** Recopilar datos adicionales del usuario (ubicación, teléfono) solo cuando sean relevantes para personalizar la respuesta de un trámite, reduciendo la fricción del onboarding.

| ID | Requerimiento | Prioridad |
|---|---|---|
| RF-020 | El sistema debe solicitar la ubicación del usuario solo cuando el trámite requiere sugerir módulos cercanos | Media |
| RF-021 | El sistema debe permitir al usuario proporcionar datos adicionales desde su perfil en cualquier momento | Baja |
| RF-022 | El sistema debe permitir al usuario actualizar o corregir sus datos de perfil | Baja |

---

## 6. Requerimientos No Funcionales (Resumen)

*Detalle completo en `02_Requirements/non_functional_requirements.md`*

| ID | Categoría | Requerimiento |
|---|---|---|
| RNF-001 | Usabilidad | La interfaz debe ser funcional en navegadores modernos (Chrome, Firefox, Safari, Edge) en sus últimas 2 versiones |
| RNF-002 | Usabilidad | El flujo de registro no debe requerir más de 3 campos ni más de 2 pasos |
| RNF-003 | Rendimiento | El chatbot debe responder en menos de 5 segundos en condiciones normales de red |
| RNF-004 | Seguridad | Las contraseñas deben almacenarse con hash (nunca en texto plano) |
| RNF-005 | Seguridad | Las sesiones deben expirar tras un período de inactividad definido |
| RNF-006 | Confiabilidad | El sistema debe mostrar mensajes de error claros cuando el chatbot no esté disponible |
| RNF-007 | Contenido | El chatbot nunca debe presentar información inventada como si fuera factual (no hallucinate) |

---

## 7. Reglas de Negocio

| ID | Regla |
|---|---|
| RN-001 | Un usuario solo puede tener un espacio de trabajo activo por tipo de trámite |
| RN-002 | El chatbot no puede opinar sobre calidad de atención de módulos gubernamentales en MVP |
| RN-003 | El chatbot debe siempre acompañar su respuesta con la fuente o una recomendación de verificar en el portal oficial correspondiente |
| RN-004 | El disclaimer de información desactualizada debe ser visible antes de que el usuario haga su primera pregunta |
| RN-005 | El registro requiere únicamente nombre, correo y contraseña — ningún otro dato es obligatorio en el onboarding |

---

## 8. Criterios de Aceptación del Producto (Product-Level)

El MVP se considera completo cuando:

- [ ] Un usuario puede registrarse, iniciar sesión y cerrar sesión sin errores.
- [ ] Un usuario puede crear un trámite de los 3 disponibles y acceder a su espacio de trabajo.
- [ ] El chatbot responde preguntas sobre licencia, verificación y cambio de placas con información factual.
- [ ] El chatbot rechaza preguntas fuera de su dominio de forma clara y sin inventar.
- [ ] El disclaimer de información aparece en la interfaz antes de la primera interacción.
- [ ] El historial de chat persiste dentro de la sesión del usuario.

---

## 9. Glosario

| Término | Definición |
|---|---|
| Espacio de trabajo / Trámite | Unidad de trabajo que agrupa el historial de chat y contexto de un trámite específico para un usuario |
| Chatbot / Asistente | El componente de IA conversacional alimentado por un LLM con knowledge base de trámites vehiculares |
| Knowledge base | Archivos Markdown por trámite que contienen la información factual inyectada al chatbot como contexto |
| Perfil progresivo | Modelo de recopilación de datos del usuario donde solo se piden los datos necesarios en el momento en que son relevantes |
| Disclaimer | Aviso visible en la interfaz que indica que la información del chatbot puede no estar actualizada |

---

*Referencia: para la descomposición detallada en Epics y User Stories con Criterios de Aceptación, ver `epics_and_stories.md`.*
