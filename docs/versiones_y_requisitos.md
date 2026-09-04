# Versiones y requisitos técnicos

## Software

| Componente | Requisito del proyecto |
|---|---|
| Python | 3.10 o superior; validado con 3.14.7 |
| Selenium | 4.25 o superior y menor que 5; validado con 4.48.0 |
| openpyxl | 3.1 o superior y menor que 4; validado con 3.1.5 |
| Navegador | Mozilla Firefox; validado con Firefox 155.0 |
| Controlador | GeckoDriver 0.37.1, gestionado automáticamente por Selenium Manager |

Para documentar las versiones exactas del equipo:

```bash
python --version
python -c "import selenium, openpyxl; print(selenium.__version__, openpyxl.__version__)"
firefox --version
```

## Requisitos de sistema

- 2 GB de RAM disponibles como mínimo;
- 300 MB de espacio para entorno, logs, descargas y resultados;
- acceso HTTPS al dominio `mantistcy.cl`;
- permisos de escritura dentro de la carpeta del proyecto;
- resolución recomendada de 1280 × 800 para ejecución visible.

## Seguridad

- no se requieren credenciales para el sitio objetivo;
- `.env` está excluido de Git;
- no se envían correos, webhooks ni avisos públicos;
- las evidencias pueden contener datos públicos visibles en el momento de la
  ejecución y deben revisarse antes de compartirlas.
