def loadGraphMat(n, m, file):
    adjMat=[]
    temp=[]
    # Llenar la lista de falsos
    for i in range(0, n):
        temp.append(False)
    for i in range(0, n):
        adjMat.append(temp)

    # Poner en verdadero aquellas casillas que si son útiles
    for i in range(0, m*2, 2):
        origin=int(file[i+2])
        target=int(file[i+3])
        adjMat[origin][target]=True
    return adjMat

def loadGraphList(n, m, adjList):
    adjList=[]
    for i in range(0, n):
        temp=[]
        adjList.append(temp)
    for i in range(0, m*2, 2):
        origin=int(file[i+2])
        target=int(file[i+3])
        adjList[origin].append(target)
    return adjList

def printMat(adjMat):
    print("Matriz de adyacencias")
    for i in range(0, len(adjMat)):
        for j in range(0, len(adjMat[i])):
            if(adjMat[i][j]):
                print("T", end=' ')
            else:
                print("F", end=' ')
        print("\n")

def printList(adjList):
    print("Lista de adyacencias")
    for i in range(0, len(adjList)):
        print("Nodo "+str(i)+": ", end=' ')
        for j in range(0, len(adjList[i])):
            print(adjList[i][j], end=' ')
        print("\n")

# Read file and leave just the numbers
f=open("input1.txt","r")
file=f.read()
file=file.replace("\n","")
file=file.replace(" ","")

n=int(file[0])
m=int(file[1])

# adjMat=loadGraphMat(n, m, file)
# printMat(adjMat)

adjList=loadGraphList(n, m, file)
printList(adjList)
