# OptiRed — Sistema de Análisis y Optimización de Redes

Proyecto Parcial II — Programación III
Docentes: M.Sc. Hector E. Ugarte R. y M.Sc. Boris Chullo Llave

## Descripción

OptiRed es un sistema en Python que modela, analiza y optimiza redes representadas
mediante grafos. Integra algoritmos de recorrido, árboles de expansión mínima, rutas
más cortas, caminos entre todos los pares y flujo máximo sobre una representación
común del grafo, con una **interfaz de escritorio interactiva (PyQt6)** para
construir/cargar la red, ejecutar cada módulo y visualizar los resultados
directamente resaltados sobre el grafo.

## Integrantes

| Nombre | Módulos a cargo |
|---|---|
| _Persona A_ | Gestión del grafo, BFS/DFS, estructuras dinámicas |
| _Persona B_ | Árbol de expansión mínima (Prim, Kruskal), rutas más cortas (Dijkstra, Bellman-Ford) |
| _Persona C_ | Caminos entre todos los pares (Floyd-Warshall, Johnson), flujo máximo (Ford-Fulkerson) |

## Estructura del proyecto

```
proyecto_optired/
├── main.py                     # Punto de entrada: lanza la interfaz gráfica PyQt6
├── README.md
├── requirements.txt
├── data/                       # Datasets de prueba (.csv / .json)
├── src/
│   ├── graph.py                 # Módulo 1: gestión del grafo
│   ├── bfs_dfs.py                # Módulo 2: recorridos BFS y DFS
│   ├── mst.py                    # Módulo 3: Prim y Kruskal
│   ├── shortest_paths.py         # Módulo 4: Dijkstra y Bellman-Ford
│   ├── all_pairs.py              # Módulo 5: Floyd-Warshall y Johnson
│   ├── max_flow.py               # Módulo 6: Ford-Fulkerson
│   ├── dynamic_structures.py     # Estructuras auxiliares (cola, pila, union-find, heap)
│   ├── utils.py                  # Lectura/escritura de archivos, formato de salida
│   └── gui/                      # Interfaz gráfica de escritorio (PyQt6)
│       ├── main_window.py         # Ventana principal: pestañas + lienzo del grafo
│       ├── canvas.py               # Visualización del grafo (spring layout, resaltado)
│       ├── graph_tab.py            # Pestaña Módulo 1
│       ├── traversal_tab.py        # Pestaña Módulo 2
│       ├── mst_tab.py              # Pestaña Módulo 3
│       ├── shortest_path_tab.py    # Pestaña Módulo 4
│       ├── all_pairs_tab.py        # Pestaña Módulo 5
│       ├── max_flow_tab.py         # Pestaña Módulo 6
│       ├── dialogs.py              # Diálogos auxiliares (propiedades del grafo)
│       └── common.py               # Paleta de colores y utilidades compartidas
├── tests/                       # Pruebas unitarias por módulo (sobre src/*.py)
└── docs/
    └── informe.pdf               # Informe técnico
```

## Requisitos

- Python 3.10 o superior
- PyQt6 (interfaz gráfica de escritorio, no requiere navegador ni conexión a internet)
- Ver `requirements.txt` para dependencias exactas

## Instalación

```bash
git clone <url-del-repositorio>
cd proyecto_optired
python -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecución

```bash
python main.py
```

Esto abre la ventana principal de OptiRed, dividida en dos zonas:

- **Izquierda:** pestañas para cada uno de los 6 módulos del sistema.
- **Derecha:** el lienzo con la visualización del grafo (siempre visible),
  que se actualiza para resaltar el resultado del último algoritmo ejecutado.
  Se puede hacer zoom con la rueda del mouse y desplazar la vista arrastrando.

### Flujo de uso típico

1. **Pestaña "1 · Grafo"**: crear un grafo vacío (indicando si es dirigido,
   ponderado y si tiene capacidades) o cargarlo desde un archivo `.csv`,
   `.txt` o `.json` de la carpeta `data/`. Desde aquí también se pueden
   agregar/eliminar nodos y aristas, y guardar el grafo resultante.
2. **Pestañas "2" a "6"**: cada una ejecuta los algoritmos de su módulo sobre
   el grafo actual, muestra los resultados en tablas y permite resaltarlos
   sobre el lienzo (árbol de recorrido, aristas del MST, camino más corto,
   matriz de distancias, flujo por arista, etc.).

Las validaciones del sistema (grafo no dirigido/ponderado/conexo requerido,
pesos negativos, ciclos negativos, ausencia de camino fuente→sumidero, etc.)
se muestran como cuadros de diálogo con un mensaje claro.

## Formato de los archivos de entrada

`data/` incluye dos formatos:

**CSV simple** (`origen,destino,peso`):
```
A,B,4
A,C,2
```

**JSON enriquecido** (nombres reales de nodos, descripción del dataset y,
para flujo, fuente/sumidero sugeridos — la interfaz los preselecciona
automáticamente en la pestaña de flujo máximo):
```json
{
  "dirigido": true,
  "ponderado": true,
  "con_capacidad": false,
  "descripcion": "Red de transporte urbano - ...",
  "nombres": { "N01": "Terminal Norte", "N02": "Plaza Mayor" },
  "nodos": ["N01", "N02"],
  "aristas": [{"origen": "N01", "destino": "N02", "peso": 5}],
  "meta": { "fuente": "N01", "sumidero": "N09" }
}
```

## Ejecutar pruebas

```bash
pytest tests/
```

Las pruebas cubren la lógica de los algoritmos en `src/*.py` de forma
independiente de la interfaz gráfica.

## Datos de prueba incluidos

Todos modelan la misma red de transporte urbano (25 estaciones), variando el
tipo de grafo según el algoritmo que se quiera probar:

| Archivo | Uso |
|---|---|
| `grafo_bfs_dfs.json` | BFS / DFS (no ponderado) |
| `grafo_mst.json` | Prim / Kruskal (no dirigido, ponderado) |
| `grafo_dijkstra.json` | Dijkstra (pesos no negativos) |
| `grafo_negativo.json` | Bellman-Ford (con pesos negativos, sin ciclo negativo) |
| `grafo_ciclo_negativo.json` | Detección de ciclo negativo |
| `grafo_todos_pares.json` | Floyd-Warshall / Johnson |
| `grafo_flujo.json` | Ford-Fulkerson (con capacidades y fuente/sumidero sugeridos) |
| `grafo_base.json` | Grafo base para exploración libre |

También se incluyen versiones `.csv` equivalentes y más pequeñas
(`grafo_simple.csv`, `grafo_mst.csv`, etc.) útiles para pruebas unitarias y
para verificar resultados a mano.

## Informe técnico

El informe técnico completo se encuentra en `docs/informe.pdf` e incluye el modelo
del grafo, algoritmos implementados, estructuras de datos, casos de prueba,
resultados obtenidos, análisis de complejidad y conclusiones.
