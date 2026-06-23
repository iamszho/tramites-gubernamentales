# User Personas
**Proyecto:** TramiteFácil  
**Versión:** 0.2 — MVP Actualizado  
**Fecha:** 2026-03-15  
**Autor:** [Tu nombre]  
**Estado:** Hipótesis — pendiente validación con usuarios reales

---

> ⚠️ **Nota importante:** Estas personas son hipótesis basadas en el conocimiento del dominio, **acotadas al MVP de trámites vehiculares** (licencia, verificación, cambio de placas). Deben validarse con usuarios reales antes de usarse como base para decisiones de diseño o desarrollo.

---

## Persona 1 — El Freelancer Fiscal

**Nombre ficticio:** Carlos, 29 años  
**Ocupación:** Diseñador gráfico independiente, CDMX  
**Perfil tecnológico:** Alto — usa apps diariamente, cómodo con interfaces web

### Contexto
Carlos factura mensualmente y debe interactuar con el SAT de forma regular. Conoce los trámites pero encuentra frustrante que la información cambie sin aviso y que los formularios del SAT sean confusos. Ha tenido que ir dos veces al módulo por documentos que creía tener completos.

### Objetivos
- Completar trámites fiscales sin ir físicamente a oficinas cuando sea posible.
- Tener certeza de que lleva los documentos correctos antes de ir.
- Saber qué módulo SAT tiene menor tiempo de espera en su zona.

### Frustraciones
- El portal del SAT tiene UX deficiente y cambia constantemente.
- Busca información en Reddit o YouTube pero la información suele estar desactualizada.
- Pierde horas productivas en trámites que deberían tomar 30 minutos.

### Relación con TramiteFácil
Usuario frecuente. Usa principalmente el **Chat** para resolver dudas rápidas sobre requisitos y costos de trámites vehiculares. Valora mucho que las respuestas sean directas y sin burocracia.

---

## Persona 2 — La Mamá que Tramita por la Familia

**Nombre ficticio:** Margarita, 47 años  
**Ocupación:** Ama de casa, Guadalajara  
**Perfil tecnológico:** Medio — usa WhatsApp y Facebook cómodamente, menos fluida con formularios web

### Contexto
Margarita gestiona los trámites de toda su familia: renovación de credencial INE, trámites del IMSS para sus hijos, constancias escolares. No es experta en trámites pero es el punto de contacto familiar para resolverlos. Depende mucho de lo que le dicen familiares o de grupos de Facebook para saber "cómo se hace".

### Objetivos
- Entender qué necesita para cada trámite sin leer documentos oficiales densos.
- No tener que hacer una segunda visita por documentos faltantes.
- Sentir que "alguien le explica" en lugar de leer instrucciones frías.

### Frustraciones
- La información oficial usa lenguaje burocrático que no entiende.
- Los grupos de Facebook tienen información contradictoria y desactualizada.
- Le da desconfianza proporcionar sus datos en sitios que no conoce.

### Relación con TramiteFácil
Usuaria ocasional. Llega principalmente por trámites vehiculares de su familia (licencia de sus hijos, verificación del coche). Usa el **Chat** para preguntas en lenguaje natural. El registro mínimo (solo nombre y correo) reduce su fricción de entrada significativamente.

> ⚠️ **Riesgo de adopción:** Aunque el onboarding es más simple en el MVP, este perfil puede tener fricción si las respuestas del chatbot son técnicas o usan lenguaje burocrático. El tono del LLM debe ser conversacional.

---

## Persona 3 — El Ciudadano de Primera Vez

**Nombre ficticio:** Sebastián, 18 años  
**Ocupación:** Estudiante, Monterrey  
**Perfil tecnológico:** Alto — nativo digital

### Contexto
Sebastián acaba de cumplir 18 años y necesita sacar por primera vez su CURP oficial, INE, y posiblemente su RFC. No sabe por dónde empezar, qué necesita ni en qué orden hacer los trámites. Sus padres tampoco recuerdan bien el proceso.

### Objetivos
- Entender el "camino completo" de los trámites que necesita hacer.
- No cometer errores en formularios por ser su primera vez.
- Hacerlo de la forma más rápida y con menos filas posible.

### Frustraciones
- No sabe ni qué trámites necesita, mucho menos cómo hacerlos.
- Siente que la información oficial asume que ya sabe "cómo funciona el gobierno".
- Le da pereza ir a filas y preferiría resolver todo en línea.

### Relación con TramiteFácil
El caso de uso más claro del MVP: necesita sacar su primera licencia y no sabe nada del proceso. Usaría el **Chat** intensamente para entender qué necesita, cuánto cuesta y dónde ir. Alta probabilidad de convertirse en usuario recurrente (verificación anual, renovación de licencia).

---

## Persona 4 — El Adulto Mayor Asistido

**Nombre ficticio:** Don Roberto, 68 años  
**Ocupación:** Jubilado, municipio semi-urbano de Estado de México  
**Perfil tecnológico:** Bajo — usa el celular básicamente para llamadas y WhatsApp

### Contexto
Don Roberto necesita tramitar su pensión del IMSS y renovar documentos. No usa computadora y tendría que ser su hijo quien lo ayude con cualquier plataforma digital. Es el usuario con más dolor pero también el de más baja adopción directa.

### Objetivos
- Que alguien (su hijo) pueda prepararlo para el trámite sin ir físicamente a preguntar.
- No tener que regresar al módulo porque faltó un documento.

### Frustraciones
- Nadie le explica de forma clara y humana qué necesita.
- Los módulos de atención en municipios pequeños tienen horarios limitados y poca información.

### Relación con TramiteFácil
**Usuario indirecto.** Es el beneficiario final, pero quien usa la plataforma es un familiar. Este perfil no es el usuario primario del MVP pero sí define que el contenido debe ser claro, sin jerga, y los formularios deben poder usarse sin conocimiento previo del trámite.

---

## Resumen de Personas

| | Carlos | Margarita | Sebastián | Don Roberto |
|---|---|---|---|---|
| Frecuencia de uso | Alta | Media | Puntual | Indirecto |
| Tech savviness | Alto | Medio | Alto | Bajo |
| Feature prioritario MVP | Chat | Chat | Chat | Legibilidad del contenido |
| Riesgo de abandono | Bajo | Medio (tono del chat) | Bajo | N/A (indirecto) |
| Valor para producto | Validación frecuente | Caso de uso masivo | Primera licencia | Define claridad del lenguaje |

---

## Personas Excluidas del MVP

**El usuario de trámites no vehiculares** (SAT, INE, IMSS, etc.) — existe el dolor pero el chatbot del MVP no tiene base de conocimiento para estos dominios. Se incorporan en V2+ con la expansión del catálogo.

**El funcionario público / validador institucional** — oportunidad futura para una versión B2G donde los módulos puedan recibir retroalimentación ciudadana. Descartado por complejidad y modelo de negocio diferente.

---

*Validar estas hipótesis con entrevistas antes de avanzar al BRD.*  
*Referencia cruzada: `00_Project_Charter/problem_statement.md`*
