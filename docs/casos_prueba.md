# Casos de prueba

| ID | Caso | Tipo | Resultado esperado | Resultado validado |
|---|---|---|---|---|
| CP-01 | Convertir unidades con punto y coma decimal | Unitario | Números correctos | APROBADO |
| CP-02 | Rechazar texto sin valor numérico | Unitario | `ValueError` controlado | APROBADO |
| CP-03 | Clasificar estación verde | Unitario | Nivel VERDE | APROBADO |
| CP-04 | Clasificar una superación | Unitario | Nivel AMARILLO | APROBADO |
| CP-05 | Clasificar dos superaciones | Unitario | Nivel ROJO | APROBADO |
| CP-06 | Exportar Excel y JSON | Unitario | Archivos válidos y legibles | APROBADO |
| CP-07 | Abrir sitio y extraer estaciones | En vivo | Diez o más estaciones | APROBADO: 15 |
| CP-08 | Navegar y extraer sismos | En vivo | Una o más filas | APROBADO: 20 |
| CP-09 | Seleccionar una ciudad | Funcional | Pronóstico de la ciudad | APROBADO: Santiago |
| CP-10 | Rellenar formulario sin publicar | Funcional | Captura con campos completos | APROBADO: sin envío |

La prueba en vivo exige `RUN_LIVE_TESTS=1`; de otro modo se omite de manera
intencional para evitar tráfico involuntario. Validación realizada el 3 de
septiembre de 2026: **10 de 10 casos aprobados (100 %)**, por encima del mínimo
de 80 % exigido.
