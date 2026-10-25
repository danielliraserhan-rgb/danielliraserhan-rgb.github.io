# Fuente editable de /predicaciones/

- `_cms/predicaciones/*.md`: un archivo por artículo (front matter YAML + texto en Markdown). Se editan desde Pages CMS (`.pages.yml`).
- `_cms/build.py`: genera `predicaciones/<slug>/index.html`, `index.md`, `og.jpg` (solo si cambió el título), `predicaciones/index.html`, la sección de la portada, `sitemap.xml`, `llms.txt` y `llms-full.txt`.
- `.github/workflows/construir-predicaciones.yml`: ejecuta el build en cada cambio en `main` bajo `_cms/` y publica.
- `published: false` oculta un artículo de listados en el siguiente build (su página ya generada no se borra sola).
- Local: `pip install pyyaml pillow && python3 _cms/build.py`
