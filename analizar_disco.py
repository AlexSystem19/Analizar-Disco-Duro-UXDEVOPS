"""
Analizador de Disco - UXDEVOPS
Escanea el disco D y genera un reporte JSON con:
- Tipos de archivo y su espacio
- Antigüedad de archivos
- Archivos más pesados
- Duplicados por nombre
Uso: python analizar_disco.py
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import sys

# ==================== CONFIG ====================
RUTA_DISCO = "D:\\"          # Cambia aquí si quieres escanear otra ruta
MAX_ARCHIVOS = 100_000       # Límite de seguridad
OUTPUT_JSON = "reporte_disco.json"
# ================================================

CATEGORIAS = {
    "Documentos":    [".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt",
                      ".txt", ".csv", ".odt", ".ods", ".rtf", ".md"],
    "Imágenes":      [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp",
                      ".svg", ".ico", ".raw", ".heic", ".heif"],
    "Video":         [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm",
                      ".m4v", ".3gp", ".mpg", ".mpeg"],
    "Audio":         [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a",
                      ".opus", ".aiff"],
    "Código":        [".py", ".js", ".ts", ".html", ".css", ".cs", ".java",
                      ".cpp", ".c", ".h", ".php", ".sql", ".json", ".xml",
                      ".yaml", ".yml", ".sh", ".bat", ".ps1", ".vb", ".vbs",
                      ".pbix", ".pbip", ".m", ".dax"],
    "Comprimidos":   [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz",
                      ".cab", ".iso"],
    "Ejecutables":   [".exe", ".msi", ".apk", ".dmg", ".deb", ".rpm",
                      ".dll", ".sys"],
    "Bases de datos":[".db", ".sqlite", ".sqlite3", ".mdb", ".accdb",
                      ".bak", ".sql", ".frm", ".ibd"],
    "Diseño":        [".psd", ".ai", ".xd", ".fig", ".sketch", ".indd",
                      ".eps", ".cdr"],
    "Proyectos":     [".sln", ".csproj", ".vbproj", ".fsproj", ".pyproj",
                      ".pbixproj", ".proj"],
}

CARPETAS_EXCLUIR = {
    "windows", "system32", "syswow64", "program files", "program files (x86)",
    "$recycle.bin", "system volume information", "perflogs",
    "appdata", "temp", "tmp", ".git", "node_modules", "__pycache__",
    ".vs", "obj", "bin", ".idea"
}

def categorizar(ext):
    ext = ext.lower()
    for cat, exts in CATEGORIAS.items():
        if ext in exts:
            return cat
    return "Otros"

def tamanio_legible(bytes_):
    for u in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_ < 1024:
            return f"{bytes_:.1f} {u}"
        bytes_ /= 1024
    return f"{bytes_:.1f} PB"

def clasificar_antiguedad(dias):
    if dias <= 30:   return "Último mes"
    if dias <= 90:   return "Últimos 3 meses"
    if dias <= 180:  return "Últimos 6 meses"
    if dias <= 365:  return "Último año"
    if dias <= 730:  return "1-2 años"
    if dias <= 1095: return "2-3 años"
    if dias <= 1825: return "3-5 años"
    return "Más de 5 años"

def debe_excluir(path):
    partes = [p.lower() for p in path.parts]
    return any(excluir in partes for excluir in CARPETAS_EXCLUIR)

def hash_archivo(path, bytes_leer=8192):
    try:
        h = hashlib.md5()
        with open(path, "rb") as f:
            h.update(f.read(bytes_leer))
        return h.hexdigest()
    except:
        return None

print("=" * 60)
print("  ANALIZADOR DE DISCO - UXDEVOPS")
print("=" * 60)
print(f"  Escaneando: {RUTA_DISCO}")
print(f"  Iniciado:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("-" * 60)

ahora = datetime.now()
conteo = 0
errores = 0

# Acumuladores
por_categoria   = defaultdict(lambda: {"archivos": 0, "bytes": 0, "extensiones": defaultdict(int)})
por_antiguedad  = defaultdict(lambda: {"archivos": 0, "bytes": 0})
por_anio        = defaultdict(lambda: {"archivos": 0, "bytes": 0})
archivos_grandes = []
hashes_duplicado = defaultdict(list)
carpetas_pesadas = defaultdict(lambda: {"archivos": 0, "bytes": 0})

ruta_base = Path(RUTA_DISCO)

for archivo in ruta_base.rglob("*"):
    if conteo >= MAX_ARCHIVOS:
        print(f"\n  [AVISO] Límite de {MAX_ARCHIVOS:,} archivos alcanzado.")
        break

    try:
        if not archivo.is_file():
            continue
        if debe_excluir(archivo):
            continue

        stat = archivo.stat()
        tamanio = stat.st_size
        modificado = datetime.fromtimestamp(stat.st_mtime)
        dias = (ahora - modificado).days
        anio = modificado.year
        ext = archivo.suffix.lower() if archivo.suffix else "(sin ext)"
        cat = categorizar(ext)
        ant = clasificar_antiguedad(dias)

        por_categoria[cat]["archivos"] += 1
        por_categoria[cat]["bytes"] += tamanio
        por_categoria[cat]["extensiones"][ext] += tamanio

        por_antiguedad[ant]["archivos"] += 1
        por_antiguedad[ant]["bytes"] += tamanio

        por_anio[str(anio)]["archivos"] += 1
        por_anio[str(anio)]["bytes"] += tamanio

        # Top 200 archivos más grandes
        archivos_grandes.append({
            "ruta": str(archivo),
            "nombre": archivo.name,
            "bytes": tamanio,
            "tamanio": tamanio_legible(tamanio),
            "categoria": cat,
            "extension": ext,
            "modificado": modificado.strftime("%Y-%m-%d"),
            "antiguedad_dias": dias
        })

        # Carpeta padre
        carpeta = str(archivo.parent)
        carpetas_pesadas[carpeta]["archivos"] += 1
        carpetas_pesadas[carpeta]["bytes"] += tamanio

        # Hash para duplicados (solo archivos > 10KB y < 500MB)
        if 10_240 < tamanio < 524_288_000:
            h = hash_archivo(archivo)
            if h:
                hashes_duplicado[h].append({
                    "ruta": str(archivo),
                    "bytes": tamanio,
                    "tamanio": tamanio_legible(tamanio)
                })

        conteo += 1
        if conteo % 1000 == 0:
            print(f"  Archivos procesados: {conteo:,}", end="\r")

    except PermissionError:
        errores += 1
    except Exception as e:
        errores += 1

print(f"\n  Archivos procesados: {conteo:,}  |  Errores: {errores:,}")

# Ordenar top archivos más grandes
archivos_grandes.sort(key=lambda x: x["bytes"], reverse=True)
archivos_grandes = archivos_grandes[:200]

# Duplicados reales (mismo hash, más de 1 archivo)
duplicados = []
espacio_recuperable_dup = 0
for h, archivos in hashes_duplicado.items():
    if len(archivos) > 1:
        bytes_por_grupo = archivos[0]["bytes"]
        espacio_rec = bytes_por_grupo * (len(archivos) - 1)
        espacio_recuperable_dup += espacio_rec
        duplicados.append({
            "hash": h,
            "cantidad": len(archivos),
            "bytes_cada_uno": bytes_por_grupo,
            "tamanio": archivos[0]["tamanio"],
            "espacio_recuperable": tamanio_legible(espacio_rec),
            "archivos": archivos
        })

duplicados.sort(key=lambda x: x["bytes_cada_uno"] * x["cantidad"], reverse=True)

# Top 20 carpetas más pesadas
top_carpetas = sorted(
    [{"carpeta": k, **v, "tamanio": tamanio_legible(v["bytes"])}
     for k, v in carpetas_pesadas.items()],
    key=lambda x: x["bytes"], reverse=True
)[:20]

# Totales
total_bytes = sum(v["bytes"] for v in por_categoria.values())
total_archivos = sum(v["archivos"] for v in por_categoria.values())

# Serializar para JSON
def serializar_categoria(d):
    return {
        k: {
            "archivos": v["archivos"],
            "bytes": v["bytes"],
            "tamanio": tamanio_legible(v["bytes"]),
            "porcentaje": round(v["bytes"] / total_bytes * 100, 1) if total_bytes > 0 else 0,
            "extensiones": dict(sorted(v["extensiones"].items(), key=lambda x: x[1], reverse=True)[:10])
        }
        for k, v in d.items()
    }

reporte = {
    "meta": {
        "ruta_escaneada": RUTA_DISCO,
        "fecha_escaneo": ahora.strftime("%Y-%m-%d %H:%M:%S"),
        "total_archivos": total_archivos,
        "total_bytes": total_bytes,
        "total_tamanio": tamanio_legible(total_bytes),
        "errores_acceso": errores
    },
    "por_categoria": serializar_categoria(por_categoria),
    "por_antiguedad": {
        k: {
            "archivos": v["archivos"],
            "bytes": v["bytes"],
            "tamanio": tamanio_legible(v["bytes"]),
            "porcentaje": round(v["bytes"] / total_bytes * 100, 1) if total_bytes > 0 else 0
        }
        for k, v in por_antiguedad.items()
    },
    "por_anio": {
        k: {
            "archivos": v["archivos"],
            "bytes": v["bytes"],
            "tamanio": tamanio_legible(v["bytes"])
        }
        for k, v in sorted(por_anio.items())
    },
    "archivos_grandes": archivos_grandes,
    "carpetas_pesadas": top_carpetas,
    "duplicados": {
        "total_grupos": len(duplicados),
        "espacio_recuperable": tamanio_legible(espacio_recuperable_dup),
        "espacio_recuperable_bytes": espacio_recuperable_dup,
        "grupos": duplicados[:50]
    }
}

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(reporte, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 60)
print(f"  RESUMEN FINAL")
print("=" * 60)
print(f"  Total archivos: {total_archivos:,}")
print(f"  Espacio total:  {tamanio_legible(total_bytes)}")
print(f"  Grupos duplic.: {len(duplicados)}")
print(f"  Recuperable:    {tamanio_legible(espacio_recuperable_dup)}")
print("-" * 60)
print(f"  Reporte guardado en: {OUTPUT_JSON}")
print(f"  Abre visualizador_disco.html y carga el JSON")
print("=" * 60)
