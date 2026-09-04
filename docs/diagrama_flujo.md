# Diagrama de flujo de la automatización

La plataforma es pública y no solicita credenciales. Por ello, el paso de
“inicio de sesión” se reemplaza correctamente por la apertura de una sesión de
navegador y la validación de acceso al sitio.

```mermaid
flowchart TD
    A([Inicio]) --> B[Iniciar Chrome con Selenium]
    B --> C[Abrir mantistcy.cl/clima]
    C --> D{¿La matriz está disponible?}
    D -- No --> E[Capturar pantalla y registrar error]
    E --> Z[Cerrar navegador]
    D -- Sí --> F[Recorrer tarjetas de estaciones]
    F --> G[Seleccionar ciudad del pronóstico]
    G --> H{¿Se solicitó descarga Raw?}
    H -- Sí --> I[Hacer clic y verificar descarga]
    H -- No --> J[Navegar a sismos]
    I --> J
    J --> K[Extraer filas de la tabla]
    K --> L[Navegar a avisos]
    L --> M[Extraer avisos activos]
    M --> N{¿Modo formulario demo?}
    N -- Sí --> O[Rellenar campos sin publicar]
    N -- No --> P[Comparar datos con umbrales]
    O --> P
    P --> Q{¿Supera PM2.5 y/o lluvia?}
    Q -- Ambos --> R[Clasificar ROJO]
    Q -- Uno --> S[Clasificar AMARILLO]
    Q -- Ninguno --> T[Clasificar VERDE]
    R --> U[Generar Excel, JSON, capturas y log]
    S --> U
    T --> U
    U --> Z
    Z --> V([Fin])
```

## Mapa resumido

**Apertura y validación → navegación → extracción/carga → validación de
umbrales → reporte y evidencias → cierre seguro.**

