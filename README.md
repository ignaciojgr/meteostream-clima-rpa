# METEOSTREAM Clima Chile — Robot RPA con Python y Selenium

Proyecto académico de automatización para la plataforma pública
[METEOSTREAM Clima Chile](https://mantistcy.cl/clima/). Todas las acciones web
se realizan exclusivamente con **Python + Selenium**; no se usan `requests`,
BeautifulSoup, Playwright, Puppeteer ni herramientas RPA de terceros.

## Qué automatiza

1. Abre el sitio y valida que la matriz meteorológica esté disponible.
2. Recorre las tarjetas de estaciones y extrae zona, temperatura, humedad,
   PM2.5, condición, máximas, mínimas y lluvia.
3. Selecciona una ciudad en el pronóstico extendido para demostrar carga de
   información en un control web.
4. Descarga opcionalmente la telemetría Raw mediante un clic de Selenium.
5. Navega mediante los enlaces del sitio hacia sismos y avisos.
6. Extrae la tabla de sismos y los avisos activos.
7. Puede rellenar el formulario de avisos en modo demostración, **sin pulsar
   “Publicar Aviso”** y sin modificar el sitio.
8. Compara los datos con umbrales configurables, genera un Excel con formato
   de alertas, un resumen JSON, evidencias PNG y un log cronológico.

## Requisitos

- Python 3.10 o superior.
- Mozilla Firefox instalado.
- Acceso a `https://mantistcy.cl/clima/`.
- Las dependencias de [requirements.txt](requirements.txt).

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

Selenium Manager obtiene automáticamente **GeckoDriver**, el controlador de
Firefox, cuando es necesario. No se guardan credenciales en el repositorio.

## Ejecución

Ejecución segura recomendada:

```bash
python -m meteostream_rpa --headless --ciudad Santiago
```

Demostración completa, incluyendo descarga Raw y llenado del formulario sin
envío:

```bash
python -m meteostream_rpa --headless --ciudad Santiago \
  --descargar-raw --llenar-formulario-demo
```

Para observar el navegador:

```bash
python -m meteostream_rpa --visible --ciudad Valparaíso
```

Los resultados se guardan en `salidas/`, las descargas en `descargas/`, las
capturas en `evidencias/` y el historial en `logs/meteostream_rpa.log`.

## Pruebas

```bash
python -m unittest discover -s tests -v
```

La prueba en vivo se omite por defecto para no efectuar tráfico involuntario:

```bash
RUN_LIVE_TESTS=1 python -m unittest tests.test_live_smoke -v
```

## Estructura

```text
meteostream_rpa/       Código del robot y punto de entrada
data/                  Umbrales editables por ciudad
docs/                  Informe técnico, flujo y casos de prueba
evidencias/            Capturas obtenidas por Selenium
tests/                 Pruebas unitarias y prueba en vivo opcional
salidas/ descargas/    Artefactos generados durante la ejecución
```

## Documentación de la evaluación

- [Informe técnico](docs/informe_tecnico.md)
- [Diagrama de flujo](docs/diagrama_flujo.md)
- [Casos de prueba](docs/casos_prueba.md)
- [Versiones y requisitos técnicos](docs/versiones_y_requisitos.md)

## Uso responsable

El robot limita su actividad a datos públicos, usa esperas explícitas y no
publica avisos por defecto. Ajusta la frecuencia de ejecución de forma
responsable para no sobrecargar la plataforma. Los valores obtenidos son una
fuente de apoyo y no sustituyen canales meteorológicos o sísmicos oficiales.
