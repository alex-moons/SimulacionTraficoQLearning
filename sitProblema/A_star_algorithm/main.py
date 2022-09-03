import networkx as nx
import matplotlib.pyplot as plt # Librería para visualizar grafos en pruebas

def printMat(carretera):
    for i in range(carretera):
        for node in carretera[i]:
            print(str(node)+" ", end='')
        print("\n")
    print("\n")

def a_Star_Search(carPos, carDest, waypoints_graph):
    
    initial_nodes=waypoints_graph[carPos]
    carretera=list(waypoints_graph)
    # printMat(carretera)
    # Crear la lista de lineas de tiempo del arbol
    pila=list()
    pila.append(carPos)
    while len(pila)!=0:
        nodo=pila.pop(-1)
        for n in range(len(waypoints_graph[nodo])-1, -1, n>=0):
            pila.append(waypoints_graph[nodo][n])

    return 0


