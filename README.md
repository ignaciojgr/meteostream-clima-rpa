# Robot MeteoStream

Crear el entorno e instalar dependencias:

```bash
python -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python ej.py
```

Se requiere Firefox instalado (o Chrome/Edge al cambiar `NAVEGADOR`).
El robot extrae estaciones, descarga la telemetria TXT mediante un clic,
consulta sismos mediante un enlace y abre el formulario de avisos.
`PUBLICAR_AVISO = True` envia el aviso; usar `False` para solo rellenar el formulario.

Todas las funciones del robot estan en `ej.py`, incluida la integracion Excel.
Para entregar el codigo basta ese archivo Python; el maestro
`maestro_umbrales_clima.xlsx` sigue siendo un archivo de entrada necesario.
Se requieren Selenium y openpyxl: `python -m pip install selenium openpyxl`.
El archivo de pruebas es solo para desarrollo y no se necesita para ejecutar el robot.

## Excel y umbrales

El robot carga `maestro_umbrales_clima.xlsx`, situado junto a `ej.py`, antes
de abrir el navegador. La hoja `Umbrales` debe tener estas columnas:

| parametro | umbral | unidad |
| --- | ---: | --- |
| mp25 | 50 | µg/m³ |
| lluvia_mm | 20 | mm |

Los valores iniciales corresponden al ejemplo solicitado. Editar la columna
`umbral` en Excel para cambiar la comparacion; los valores deben ser numericos.
No se reemplaza un maestro existente ni se aplican valores predeterminados si
falta o tiene errores.

Se extrae `Lluvia` del pie de cada tarjeta. Cada ejecucion guarda
`evidencias/clima_consolidado_[FECHA].xlsx`, con fecha y hora para evitar
sobrescribir ejecuciones anteriores. Incluye los datos de las estaciones,
los umbrales utilizados, fecha de extraccion, fuente y una formula Excel:

- `ALERTA` si MP 2.5 supera su umbral **o** lluvia supera el suyo.
- `SIN ALERTA` si ambos datos existen y ninguno supera su umbral.
- `SIN DATO` si falta un dato y el disponible no dispara una alerta.

Igualar el umbral no dispara una alerta. Las celdas vacias no equivalen a cero.
La formula se calcula al abrir el archivo en Excel; el CSV incluye el estado
calculado por Python. Los umbrales del consolidado son una copia de los usados
en esa ejecucion, sin vinculos externos al maestro.

`estado_alerta` es la comparacion solicitada para Excel/CSV. `calidad_aire` y la
seleccion del aviso web mantienen la logica original de MP 2.5; no se generan
avisos adicionales por lluvia.

Pruebas: `.venv/bin/python -m unittest -v test_excel_clima.py`.

## Version anterior del repositorio

`meteostream_rpa/`, `data/`, `docs/` y `tests/` corresponden a la version modular
anterior. El robot actual se ejecuta con `python ej.py`; su prueba es
`python -m unittest -v test_excel_clima.py`.

Los archivos generados en `evidencias/` se conservan localmente y se excluyen de Git.
