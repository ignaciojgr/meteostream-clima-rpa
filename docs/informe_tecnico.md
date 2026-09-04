# Informe técnico — Automatización de monitoreo METEOSTREAM

## 1. Descripción del problema

El proceso manual obliga al operador a abrir METEOSTREAM Clima Chile, revisar
una a una las estaciones distribuidas de norte a sur, copiar temperatura,
humedad, PM2.5 y lluvia, consultar en otra pantalla la actividad sísmica,
revisar los avisos regionales y consolidar los resultados. La repetición y el
volumen aumentan el tiempo de respuesta y el riesgo de omitir una condición
crítica.

El robot propuesto automatiza el levantamiento de estos datos públicos en
`https://mantistcy.cl/clima/` mediante Python y Selenium. El resultado es un
libro Excel con semáforo de alertas, un resumen JSON, capturas y un log.

## 2. Justificación de la automatización

El proceso es susceptible de automatización porque sigue reglas estables:

- las estaciones comparten una estructura HTML repetida;
- las métricas aparecen con etiquetas reconocibles;
- sismos se presenta en una tabla con columnas fijas;
- los umbrales pueden expresarse como comparaciones numéricas;
- los resultados pueden consolidarse en formatos estructurados;
- la actividad se repite con frecuencia y no requiere juicio humano durante la
  extracción.

La decisión operativa final sigue siendo humana. El robot detecta y destaca
señales; no reemplaza fuentes oficiales ni emite por sí mismo una alerta pública.

## 3. Pasos manuales actuales

1. Abrir el sitio de clima.
2. Confirmar que la información se encuentre actualizada.
3. Revisar cada tarjeta meteorológica.
4. Copiar los valores a una planilla.
5. Abrir la sección de sismos y copiar los registros relevantes.
6. Abrir la sección de avisos y revisar novedades.
7. Comparar manualmente PM2.5, lluvia y magnitud con valores críticos.
8. Preparar un reporte y conservar evidencia.

## 4. Tareas repetitivas que se optimizan

- navegación entre tres páginas del mismo sistema;
- espera de elementos dinámicos;
- lectura de tarjetas y filas de tabla;
- conversión de unidades mostradas como texto a números;
- comparación contra la planilla maestra;
- clasificación verde, amarilla o roja;
- creación del reporte, resumen, evidencias y trazabilidad.

## 5. Objetivo y tareas del robot

**Objetivo general:** reducir el trabajo manual de consolidación y detectar de
manera consistente superaciones de umbral.

**Tareas específicas:**

- abrir y validar el sitio público;
- extraer todas las estaciones con un ciclo `for`;
- seleccionar una ciudad en el pronóstico;
- descargar la telemetría Raw cuando se solicite;
- extraer sismos y avisos;
- demostrar llenado de formulario sin efectuar una publicación;
- aplicar condicionales `if/elif/else` para el semáforo;
- controlar errores, tomar una captura y cerrar Firefox aun si ocurre una falla;
- producir Excel, JSON y logs reproducibles.

## 6. Alcance y limitaciones

### Incluido

- navegación automática, clics, selección de opciones e ingreso de texto;
- scraping visual mediante Selenium, sin llamadas HTTP paralelas;
- descarga activada por el enlace del sitio;
- extracción de estaciones, sismos y avisos visibles;
- reporte Excel con formato condicional;
- evidencias y pruebas automatizadas.

### Fuera de alcance

- publicar avisos reales o modificar datos de la plataforma;
- envío de correo o webhooks con credenciales reales;
- ejecución cada 30 minutos en infraestructura productiva;
- garantía de continuidad si el propietario cambia el HTML;
- uso de la información como reemplazo de SENAPRED, DMC, CSN u otra fuente
  oficial.

## 7. Automatizaciones básicas implementadas

| Requisito | Evidencia en el proyecto |
|---|---|
| Navegación | Apertura del inicio y clics a sismos/avisos |
| Carga de información | Selección de ciudad y formulario demo sin envío |
| Extracción | Tarjetas meteorológicas, tabla sísmica y avisos activos |
| Manejo web | Clics, listas desplegables, texto, esperas y descarga |

## 8. Estructuras de programación

- **Condicional 1:** semáforo ROJO/AMARILLO/VERDE según PM2.5 y lluvia.
- **Condicional 2:** validación de ciudad disponible y uso de Santiago como
  alternativa controlada.
- **Ciclo `for`:** recorrido de estaciones, filas sísmicas, avisos y umbrales.
- **Ciclo `while`:** espera acotada de la descarga Raw.
- **Excepciones:** captura de `TimeoutException`, `NoSuchElementException`,
  errores de conversión y fallas del navegador.
- **Validación:** se rechaza una tarjeta sin números o una ejecución sin
  estaciones.
- **Cierre seguro:** el contexto `with` finaliza el controlador incluso ante
  errores.

## 9. Beneficios esperados

- disminución del tiempo de consolidación;
- criterios uniformes para todas las estaciones;
- mayor trazabilidad mediante fecha, log y archivos estructurados;
- reducción de errores de transcripción;
- evidencia visual reproducible;
- base ampliable para una programación desatendida responsable.

## 10. Riesgos y controles

| Riesgo | Control aplicado |
|---|---|
| Cambio de HTML | Selectores por etiquetas y texto; prueba en vivo opcional |
| Lentitud o caída | Esperas explícitas, plazo máximo y captura de error |
| Sobrecarga del sitio | Una secuencia acotada; prueba en vivo desactivada por defecto |
| Publicación accidental | El botón “Publicar Aviso” nunca se pulsa |
| Datos inexactos | Reporte de apoyo; contraste humano con fuentes oficiales |
| Exposición de secretos | `.env` ignorado, ausencia de credenciales y anonimización de la IP reflejada por el sitio |

## 11. Procedimiento de despliegue y uso

1. Instalar Python y Firefox.
2. Crear un entorno virtual e instalar `requirements.txt`.
3. Copiar `.env.example` a `.env` si se requieren valores personalizados.
4. Editar `data/maestro_umbrales_clima.csv`.
5. Ejecutar primero las pruebas unitarias.
6. Ejecutar el robot en modo `--headless`.
7. Revisar `salidas/`, `evidencias/` y `logs/`.
8. Antes de programar ejecuciones periódicas, acordar una frecuencia respetuosa
   con el responsable del sitio.

## 12. Problemas encontrados y soluciones

1. **El documento sugería `.card`, pero el sitio real usa `.bd-card.h-100`.**
   Se verificó el DOM actual y se adoptó el selector real.
2. **La sección de avisos no es una tabla.** Contiene un formulario y tarjetas
   de avisos activos; el robot trata ambas estructuras correctamente.
3. **El sitio no tiene inicio de sesión.** El flujo inicia con sesión de
   navegador y validación de acceso, sin credenciales ficticias.
4. **Publicar una prueba alteraría un sistema público.** El modo demostración
   rellena los campos, toma evidencia y se detiene antes del envío.

## 13. Criterio de éxito

La solución se considera exitosa cuando procesa las estaciones, navega a las
dos secciones complementarias, genera ambos reportes y supera al menos el 80 %
de los casos definidos en [casos_prueba.md](casos_prueba.md). La validación del
3 de septiembre de 2026 obtuvo 10 de 10 casos aprobados (100 %): 15 estaciones,
20 sismos y cuatro evidencias visuales con Firefox 155.0 y GeckoDriver 0.37.1,
sin publicar datos en el sitio.
