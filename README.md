# Analizador de Disco

Herramienta local para mapear el uso de espacio en disco. Genera un reporte JSON con el árbol completo de directorios y lo visualiza en el navegador sin subir nada a internet.

Sin instalación. Sin cuenta. Sin servidor.

---

## Cómo funciona

```
analizar_disco.py  →  reporte_disco.json  →  visualizador_disco.html
```

1. El script Python recorre el árbol de directorios y genera `reporte_disco.json`
2. Abres `visualizador_disco.html` en el navegador
3. Cargas el JSON desde el mismo archivo
4. Ves el análisis completo al instante

Todo se ejecuta localmente. Ningún dato sale de tu máquina.

---

## Requisitos

- Python 3.x
- Anaconda (recomendado) o cualquier entorno Python estándar
- Navegador moderno (Chrome, Edge, Firefox)

No requiere dependencias externas. No hay `pip install`.

---

## Uso

```bash
# Abre Anaconda Prompt y navega al directorio donde están los archivos
d:
cd ruta\de\tu\carpeta

# Ejecuta el script indicando el disco o carpeta a analizar
python analizar_disco.py
```

Esto genera `reporte_disco.json` en el mismo directorio.

Luego abre `visualizador_disco.html` en el navegador, haz clic en **Seleccionar archivo JSON** y carga el reporte generado.

---

## Archivos

| Archivo | Descripción |
|---|---|
| `analizar_disco.py` | Script Python que recorre el disco y genera el reporte |
| `reporte_disco.json` | Reporte generado (no se sube al repo, ver `.gitignore`) |
| `visualizador_disco.html` | Visualizador local, funciona sin conexión |

---

## .gitignore recomendado

```
reporte_disco.json
```

El JSON puede contener rutas sensibles de tu sistema. No lo subas al repo.

---

## Por qué existe esto

Las herramientas que ya existen para analizar disco son pesadas, se conectan a la nube o piden instalar algo. Este script resuelve el problema en dos archivos planos.

Desarrollado como herramienta interna de [UXDEVOPS](https://uxdevops.com).

---

## Licencia

MIT — úsalo, modifícalo, compártelo.
