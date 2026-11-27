# Prueba de usabilidad · formato para llenar

**Qué es:** 3 personas hacen 5 tareas con el sistema mientras alguien del equipo observa y anota. **Este archivo es el formato vacío:** los
resultados se escriben durante la sesión con lo que realmente pase. No se llenan de memoria ni se completan después.

## Antes de la sesión

- [ ] Plataforma arriba (`docker compose -f docker-compose.integrado.yml up -d`) y `servicios/pruebas/preparar_entregas.py --cantidad 3` para que
      el repartidor tenga entregas en ruta. Una entrega por persona.
- [ ] App Android instalada (emulador o teléfono) apuntando al equipo; app de escritorio publicada; navegador con el portal en `http://localhost:5000`.
- [ ] Cuentas: `repartidor1@codex.mx` (tareas 1 a 3), `planeador@codex.mx` (tarea 4) y `admin@codex.mx` (tarea 5). La clave se dicta en la sesión; no se escribe aquí.
- [ ] Cronómetro, este formato impreso o abierto y la frase de inicio (abajo).
- [ ] Consentimiento: la persona sabe que se evalúa el sistema, no a ella, y que puede detenerse cuando quiera. Si se graba la pantalla, se le pide permiso.

**Frase de inicio (igual para las 3 personas):** «Vamos a pedirte cinco tareas. Hazlas como lo harías tú; si algo no queda claro, dilo en voz alta.
No te vamos a ayudar salvo que lleves más de 3 minutos atorada o atorado en una tarea.»

## Las 5 tareas

| # | Tarea (se lee tal cual) | Dónde | Se cumple cuando… | Tiempo máximo |
|---|---|---|---|---|
| T1 | «Entra con la cuenta de repartidor.» | App Android | Aparece el menú «¿Qué quieres hacer?» | 3 min |
| T2 | «Busca la entrega que te toca y dime a qué dirección vas.» | App Android | Abre la entrega y lee la dirección correcta | 3 min |
| T3 | «Registra que la entregaste completa.» (QR, foto y GPS) | App Android | Aparece «Entrega registrada» (o, sin red, «el cierre quedó guardado») | 5 min |
| T4 | «Consulta el reporte de pedidos por día del último mes y descárgalo en PDF.» | App de escritorio · Reportes | El PDF se guarda y abre | 4 min |
| T5 | «Revisa si algún servicio está caído.» | Portal web · Monitoreo (`/web/servicios/monitoreo`) | Dice cuántos servicios están arriba o nombra el caído | 3 min |

Escala de resultado por tarea: **É** = éxito sin ayuda · **D** = éxito con dificultad (dudas, retrocesos o > 2 errores) · **A** = con ayuda · **F** = no la terminó.

## Registro por persona

Copiar este bloque tres veces (P1, P2, P3).

**Persona:** P__ · Perfil (sin nombre: p. ej. «estudiante de otra carrera, usa Android a diario») ________________________ ·
Fecha y hora ____________ · Observador(a) ____________ · Dispositivo ____________

| Tarea | Inicio (hh:mm:ss) | Fin | Duración | Resultado (É/D/A/F) | Errores (número y cuáles) | Qué dijo o hizo (cita breve) |
|---|---|---|---|---|---|---|
| T1 |  |  |  |  |  |  |
| T2 |  |  |  |  |  |  |
| T3 |  |  |  |  |  |  |
| T4 |  |  |  |  |  |  |
| T5 |  |  |  |  |  |  |

Qué se cuenta como error: tocar algo que no lleva a la tarea y tener que regresar, un mensaje de validación por un dato mal escrito, buscar una
opción en el lugar equivocado más de 10 segundos.

**Al terminar (1 a 5, donde 5 es «totalmente de acuerdo»):**

| Afirmación | P__ |
|---|---|
| Fue fácil saber qué hacer en cada pantalla. |  |
| Los mensajes de error me dijeron cómo arreglar el problema. |  |
| Supe en todo momento si la app tenía conexión y si mi entrega se envió. |  |
| Encontré el reporte y la descarga sin buscar mucho. |  |
| Usaría la app en mi trabajo diario. |  |

**¿Qué fue lo más confuso?** ____________________ · **¿Qué cambiarías primero?** ____________________

## Resumen (se llena al final con los tres registros)

| Tarea | Éxitos sin ayuda (de 3) | Tiempo promedio | Errores totales | Problema observado | Mejora propuesta | Prioridad (alta/media/baja) |
|---|---|---|---|---|---|---|
| T1 |  |  |  |  |  |  |
| T2 |  |  |  |  |  |  |
| T3 |  |  |  |  |  |  |
| T4 |  |  |  |  |  |  |
| T5 |  |  |  |  |  |  |

Mejoras que se hicieron antes de la entrega a partir de la prueba (con el commit): ____________________

## Qué observar en particular

- T3: ¿entiende que hacen falta el QR, la foto y el GPS antes de registrar? ¿Ve la diferencia entre «Registrar resultado» y «Guardar resultado (sin red)»?
  Una variante útil con la tercera persona: apagar la red del teléfono antes de T3 y volverla a prender después, y ver si nota que la entrega
  se envió sola («Sin enviar» desaparece del menú).
- T4: ¿encuentra el botón «Reportes» en la barra? ¿Entiende el periodo (casillas «Desde» y «Hasta»)?
- T5: ¿interpreta los colores del panel sin explicación?

---

## Resultados de la sesión del 27 de noviembre de 2026

**Cómo se hizo (versión corta):** 3 personas y **una tarea por persona**, en la PC de Mauro con la versión de `main` que incluye el PR #23
(portal en el navegador, app Android en el emulador API 36 y app de escritorio en Windows, todo contra los servicios locales).
Condujeron y anotaron Mauro y María José (ella condujo una de las tres sesiones). La tarea 3 del formato (cerrar una entrega con QR) se cambió por una compra en el portal, porque el emulador no puede
escanear un QR real. No se aplicó el cuestionario de 1 a 5.

| Persona | Perfil | Tarea | Tiempo | Resultado | Qué dijo |
|---|---|---|---|---|---|
| P1 | Estudiante | «Compra tres productos y confirma tu pedido.» (portal web, cliente) | 3 min | **É** sola | «Todo sencillo, muy intuitivo, solo que al ser una plataforma nueva, la debes conocer un poco primero.» |
| P2 | Ama de casa | «Entra como repartidor y dime a qué dirección es tu primera entrega.» (app Android) | 30 s | **É** sola | «Muy fácil, unos pocos clicks y ya estaba donde necesitaba estar.» |
| P3 | Profesional empleado | «Descarga en PDF el reporte de pedidos por día.» (app de escritorio, planeador) | 4 min | **A** con ayuda | «Estuvo medio difícil en una parte porque había muchas opciones, me guiaron y llegué.» |

**Resumen:** 2 de 3 tareas sin ayuda. Cada tarea la hizo una sola persona, así que es una señal, no una medición.

| Tarea | Problema observado | Mejora propuesta | Prioridad |
|---|---|---|---|
| Comprar (portal) | Ninguno; P1 comenta que la primera vez hay que conocer la plataforma | — | baja |
| Entrega (Android) | Ninguno | — | — |
| Reporte PDF (escritorio) | La ventana principal muestra muchas opciones en una sola barra y cuesta encontrar el camino a «Reportes» → «Descargar PDF» | Agrupar los botones por tarea (catálogos, planeación, análisis, operación) y dejar «Reportes» a la vista; un texto de ayuda en la ventana de reportes | alta |

Mejoras hechas a partir de la prueba: ninguna todavía.

