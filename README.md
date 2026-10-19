# AUDIKA CUSCO EXPERIENCES

Sitio web de Tours, Estadías y Movilidad Privada en Cusco.

## Estado
Repositorio creado. Pendiente: subir `web_publica/index.html`, guardar el secreto `AUDIKA_ICAL_FEEDS_JSON` en **Settings → Secrets and variables → Actions**, y activar **Settings → Pages → GitHub Actions**.

## Seguridad
- Las 17 URL iCal de Airbnb contienen claves privadas; **nunca** incluirlas en el repositorio, archivos HTML o capturas.
- El proceso `SOLO_ADMIN/actualizar_calendarios.py` descarga esos feeds desde el secreto de GitHub Actions y publica **solo** los periodos bloqueados, sin identificadores de huéspedes.
- Si un calendario falla o está desactualizado, la página no debe declarar disponibilidad de ese anuncio.
- Las fechas que aparecen sin bloqueos siempre requieren confirmación final dentro de Airbnb.

## Estructura
- `web_publica/index.html` — web completa (se sube desde el archivo descargable preparado en ChatGPT).
- `web_publica/disponibilidad.json` — archivo público generado por el sincronizador; inicialmente no verificado.
- `SOLO_ADMIN/actualizar_calendarios.py` — sincronizador de 17 calendarios.
- `.github/workflows/publicar-y-actualizar.yml` — despliegue a GitHub Pages y sincronización aproximada cada hora.

## No subir
Enlaces iCal con token, JSON privados, archivos .ics ni contraseñas.
