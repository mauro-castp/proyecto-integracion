# Actualización documental del Segundo Parcial

Base analizada: `proyecto-integracion-main (3).zip`, recibido en esta conversación. Versión documental 4.2, 13 de octubre de 2026. No se consultó una versión posterior de GitHub.

## Cambios de arquitectura

| Antes | Ahora | Impacto |
|---|---|---|
| Catálogos :5103 | Productos :5103, Zonas :5108, Microhubs :5109 | Cada recurso tiene un servicio de solo lectura |
| GPS dentro de Entregas | Seguimiento :5110 | Ubicaciones y recorrido usan `/api/v1/seguimiento/{id}` |
| Notificaciones :5108 | Triggers PostgreSQL y bandeja web | Se retira la API independiente, se conserva la función |
| 8 microservicios | 10 microservicios | 15 contenedores definidos, 14 continuos y migraciones |
| Reporte con 48 endpoints | 45 pares método-ruta en el código | Inventario explícito, excluye salud y documentación |

## Documentos incluidos

- Reporte técnico integral DOCX versión 4.2: diez fichas, requisitos, historias, contratos, despliegue, pruebas y trazabilidad.
- Documento de arquitectura DOCX actualizado.
- Fuentes y exportaciones de diagramas.
- Presentación de 31 slides, guion PDF y contenido en texto.
- README general, de servicios, diagramas, presentación y capturas.
- Inventario completo de endpoints.
- Evidencias adjuntas de los diez servicios, conservadas sin alterar sus resultados.

## Verificación realizada

Se compararon Docker Compose, las rutas declaradas en `servicios/*/app.py`, `sistema_web/integracion.py` y las evidencias del ZIP. Se revisó la presentación y se renderizaron los documentos para revisar su formato. No se levantaron PostgreSQL, Redis ni MongoDB, ni se ejecutaron nuevas pruebas funcionales.

La ejecución adjunta registra 93/93 casos aprobados a las 21:27 UTC del 13 de octubre. El ejemplo de cierre vigente es ENT-05: entrega 129, pedido 153, monto 146.80, HTTP 201. ENT-06 repite el UUID y devuelve 200. El GPS usa SEG-01 y SEG-02.

Las capturas manuales antiguas se identifican como históricas. Renueva las figuras 18, 23, 19 y 25 para demostrar el despliegue actual; consulta `capturas/LEEME.md`. Las aportaciones y commits históricos no se reasignaron ni se inventaron nuevas autorías. Los documentos especializados del Primer Parcial permanecen como antecedentes.

## Cómo aplicar el paquete en GitHub

1. Extrae este ZIP.
2. Copia el contenido de `Documentos_Segundo_Parcial/` sobre la raíz de tu copia del repositorio, conservando las carpetas y aceptando reemplazar los archivos con el mismo nombre. No borres ni reemplaces carpetas completas: combina su contenido.
3. Revisa los archivos en `git status`. Este paquete contiene documentación y evidencias, no modifica código, Dockerfiles ni bases de datos.
4. Agrega los cambios, crea un commit y haz push a tu rama de trabajo:

```bash
git add README.md CAMBIOS_DOCUMENTACION_SEGUNDO_PARCIAL.md "Arquitectura_Plataforma_Microhubs (1).docx" reporte_tecnico bloque_d capturas servicios/README.md servicios/INVENTARIO_ENDPOINTS.md presentacion evidencias
git diff --cached --stat
git commit -m "Actualiza documentacion del segundo parcial a diez microservicios"
git push
```

Si los microservicios cambiaron después del ZIP analizado, compara esa versión nueva antes de aplicar este paquete.
