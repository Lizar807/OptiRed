# Datos de prueba — resultados esperados

## grafo_simple.csv
No dirigido, no ponderado. Para BFS/DFS desde A: alcanza A,B,C,D,E,F.
No hay nodos no alcanzables (grafo conexo).

## grafo_mst.csv
No dirigido, ponderado, conexo (5 nodos, 5 aristas). MST esperado (Kruskal):
C-D:1, A-C:2, D-E:3, A-B:4. Costo total: 10.

## grafo_dijkstra.csv
Dirigido, ponderado, sin pesos negativos. Dijkstra desde A hasta D:
A->C->B->D con costo 2+1+5=8, o A->C->D con costo 2+8=10 → el más corto es 8.

## grafo_negativo.csv
Dirigido, con un peso negativo (C->B: -3) pero sin ciclo negativo.
Bellman-Ford debe converger; Dijkstra debe rechazarse por el peso negativo.

## grafo_ciclo_negativo.csv
Dirigido, contiene el ciclo B->C->D->B con peso total -1-1-1 = -3 (negativo).
Bellman-Ford debe detectar el ciclo negativo alcanzable desde A y detenerse.

## grafo_todos_pares.csv
Dirigido, ponderado, 5 nodos, sin pesos negativos. Usado para comparar
Floyd-Warshall y Johnson; ambos deben producir la misma matriz de distancias.

## grafo_flujo.csv
Red de flujo dirigida con fuente S y sumidero T, capacidades en las aristas.
Flujo máximo esperado de S a T: 23 (ejemplo clásico de Ford-Fulkerson).
