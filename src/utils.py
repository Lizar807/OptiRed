"""
utils.py
Funciones auxiliares utilizadas por los distintos módulos del sistema:
lectura y escritura de archivos, formato de impresión y manejo de infinito.
"""

import csv
import json
import os

INF = float("inf")  # abreviatura matemática estándar para "infinito"


def es_numero(valor):
    """Indica si un valor puede interpretarse como número (int o float)."""
    try:
        float(valor)
        return True
    except (TypeError, ValueError):
        return False


def formatear_numero(valor):
    """Formatea INF como 'INF' y el resto de valores numéricos de forma legible."""
    if valor == INF:
        return "INF"
    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))
    return str(valor)


def imprimir_tabla(encabezados, filas):
    """Imprime una tabla simple alineada en consola a partir de encabezados y filas."""
    anchos_columna = [len(str(h)) for h in encabezados]
    filas_texto = []
    for fila in filas:
        fila_texto = [formatear_numero(c) if es_numero(c) or c == INF else str(c) for c in fila]
        filas_texto.append(fila_texto)
        for i, celda in enumerate(fila_texto):
            anchos_columna[i] = max(anchos_columna[i], len(celda))

    linea_encabezado = "  ".join(str(h).ljust(anchos_columna[i]) for i, h in enumerate(encabezados))
    print(linea_encabezado)
    print("-" * len(linea_encabezado))
    for fila_texto in filas_texto:
        print("  ".join(celda.ljust(anchos_columna[i]) for i, celda in enumerate(fila_texto)))


def leer_aristas_csv(ruta):
    """
    Lee un archivo .csv con líneas 'origen,destino,peso' y devuelve una lista
    de tuplas (origen, destino, peso). Si la tercera columna no existe, se
    asume peso 1 (grafo no ponderado).
    """
    aristas = []
    with open(ruta, newline="", encoding="utf-8") as f:
        lector = csv.reader(f)
        for num_linea, fila in enumerate(lector, start=1):
            fila = [c.strip() for c in fila if c.strip() != ""]
            if not fila:
                continue
            if len(fila) < 2:
                raise ValueError(
                    f"Formato incorrecto en línea {num_linea} de {ruta}: se esperaban "
                    f"al menos 2 columnas (origen,destino[,peso])."
                )
            u, v = fila[0], fila[1]
            if len(fila) >= 3:
                if not es_numero(fila[2]):
                    raise ValueError(
                        f"Peso no numérico en línea {num_linea} de {ruta}: '{fila[2]}'"
                    )
                peso = float(fila[2])
            else:
                peso = 1.0
            aristas.append((u, v, peso))
    return aristas


def leer_grafo_json(ruta):
    """
    Lee un archivo .json de grafo. Admite dos esquemas:

    1) Esquema simple:
       {"directed": true, "weighted": true, "edges": [["A","B",4], ...]}

    2) Esquema enriquecido (nombres reales, capacidades, metadatos):
       {
         "dirigido": true, "ponderado": true, "con_capacidad": false,
         "descripcion": "...", "nombres": {"N01": "Terminal Norte", ...},
         "nodos": ["N01", "N02", ...],
         "aristas": [{"origen": "N01", "destino": "N02", "peso": 5}, ...],
         "meta": {"fuente": "N01", "sumidero": "N09"}
       }

    Devuelve un diccionario con: dirigido, ponderado, con_capacidad, nodos,
    aristas (lista de tuplas u,v,peso), etiquetas (id -> nombre legible),
    descripcion, metadatos.
    """
    with open(ruta, encoding="utf-8") as f:
        datos = json.load(f)

    es_esquema_enriquecido = "aristas" in datos or "nodos" in datos

    if es_esquema_enriquecido:
        dirigido = datos.get("dirigido", True)
        ponderado = datos.get("ponderado", True)
        con_capacidad = datos.get("con_capacidad", False)
        descripcion = datos.get("descripcion", "")
        etiquetas = datos.get("nombres", {})
        metadatos = datos.get("meta", {})
        nodos = datos.get("nodos", [])

        aristas = []
        for item in datos.get("aristas", []):
            if "origen" not in item or "destino" not in item:
                raise ValueError(f"Arista mal formada en {ruta}: {item}")
            u, v = item["origen"], item["destino"]
            peso = float(item.get("peso", 1))
            aristas.append((u, v, peso))
    else:
        dirigido = datos.get("directed", True)
        ponderado = datos.get("weighted", True)
        con_capacidad = datos.get("has_capacity", False)
        descripcion = datos.get("description", "")
        etiquetas = {}
        metadatos = {}
        nodos = []

        aristas = []
        for item in datos.get("edges", []):
            if len(item) < 2:
                raise ValueError(f"Arista mal formada en {ruta}: {item}")
            u, v = item[0], item[1]
            peso = float(item[2]) if len(item) >= 3 else 1.0
            aristas.append((u, v, peso))

    return {
        "dirigido": dirigido,
        "ponderado": ponderado,
        "con_capacidad": con_capacidad,
        "nodos": nodos,
        "aristas": aristas,
        "etiquetas": etiquetas,
        "descripcion": descripcion,
        "metadatos": metadatos,
    }


def leer_aristas_txt(ruta):
    """Lee un archivo .txt separado por espacios: 'origen destino [peso]' por línea."""
    aristas = []
    with open(ruta, encoding="utf-8") as f:
        for num_linea, linea in enumerate(f, start=1):
            partes = linea.strip().split()
            if not partes:
                continue
            if len(partes) < 2:
                raise ValueError(
                    f"Formato incorrecto en línea {num_linea} de {ruta}: "
                    f"se esperaban al menos 2 columnas."
                )
            u, v = partes[0], partes[1]
            peso = float(partes[2]) if len(partes) >= 3 else 1.0
            aristas.append((u, v, peso))
    return aristas


def escribir_aristas_csv(ruta, aristas):
    """Guarda una lista de aristas (u, v, peso) en formato CSV."""
    os.makedirs(os.path.dirname(ruta), exist_ok=True) if os.path.dirname(ruta) else None
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        for u, v, peso in aristas:
            escritor.writerow([u, v, formatear_numero(peso)])


def escribir_grafo_json(ruta, aristas, dirigido, ponderado):
    """Guarda una lista de aristas junto con los metadatos del grafo en formato JSON."""
    datos = {
        "directed": dirigido,
        "weighted": ponderado,
        "edges": [[u, v, peso] for u, v, peso in aristas],
    }
    os.makedirs(os.path.dirname(ruta), exist_ok=True) if os.path.dirname(ruta) else None
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)
