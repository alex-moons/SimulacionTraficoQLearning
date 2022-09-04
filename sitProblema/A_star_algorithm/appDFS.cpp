// Implementa funciones para manejo de grafos como matrices y listas de adyacencias
#include <iostream>
#include <vector>
#include <stack>

using namespace std;

// lee los arcos de un grafo y los almamacena en una matriz de adyacencias y en una lista de adyacencias y la
void loadGraph(int n, int m, vector<vector<int>> &adjList) {
    // crear la matriz de adyacencias con n elementos, donde la matriz de cada elemento sea un vector de booleanos falsos
    // y crear la lista de adyacencias con n elementos de vectores enteros vacíos
    vector<int> arcs;
    for (int i = 0; i < n; i++) {
        adjList.push_back(arcs);
    }
    // leer los arcos y almacenarlos en la matriz y lista
    int origin, target;
    for (int arc = 0; arc < m; arc++) {
        //cout << "Arco " << arc << ": ";
        cin >> origin >> target;
        adjList[origin].push_back(target);
    }
}

// despliega una lista de adyacencias
void displayAdjList(const vector<vector<int>> &adjList) {
    cout << endl << "Lista de Adyacencias" << endl;
    for (int node = 0; node < adjList.size(); node++)
    {
        cout << "Nodo " << node << ": ";
        for (int arc = 0; arc < adjList[node].size(); arc++)
        {
            cout << adjList[node][arc] << " ";
        }
        cout << endl;
    }
}

// implementa un recorrido primero en profundidad en un grafo
// Complejidad: O()
void DFS(vector<vector<int>> &adjList, int inicio) {
    int nnodes = adjList.size();
    int cost=1;
    vector<bool> status(nnodes, false);
    stack<int> tovisit;
    tovisit.push(0);
    cout << "DFS: \n";
    while (!tovisit.empty())
    {
        int node = tovisit.top();
        tovisit.pop();
        // if (!status[node])
        // {
            // status[node] = true;
            cout << node << " ";
            // if(adjList[node].size() == 0){
            //     cout << endl << "Coste: " << cost << endl;
            //     cost=1;
            // }else{
            //     cost++;
            // }
            for (int a = adjList[node].size() - 1; a >= 0; a--)
            {
                // if (!status[adjList[node][a]])
                // {
                    tovisit.push(adjList[node][a]);
                // }
            }
        // }
    }
    cout << endl;
}

int main() {
    int n; // cantidad de nodos
    int m; // cantidad de arcos
    vector<vector<int>> adjList; // lista de adyacencias

    //cout << "Dame # nodos y # arcos: ";
    cin >> n >> m;

    // crea el grafo como matriz y lista de adyacencias
    loadGraph(n, m, adjList);

    // despliega la lista de adyacencias
    displayAdjList(adjList);

    cout << endl;

    // recorre un grafo primero en profundidad
    DFS(adjList, 0);

    return 0;
}