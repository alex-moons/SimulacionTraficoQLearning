import numpy as np
import os

#num de col
MAP_X = 15
#num de rows
MAP_Y = 17

#Creación de Mapa
q_values = np.zeros((MAP_Y, MAP_X,2))

#Acciones de Agentes (Semáforos)
    #El naranja viene en el rojo
signalActions =  ['green', 'red']
carActions = ['forward','stop']

def printRewards(mat):
    for i in range(0,MAP_Y):
        for j in range(0,MAP_X):
            print(mat[i,j],end=" ")
    print('\n')

#Definir Reward Matrix
rewards = np.full((MAP_Y,MAP_X),-100)

#Llenar los 100
rewards[6,7]=rewards[7,0]=rewards[8,0]=rewards[9,0]=rewards[10,1]=100

#Llenar los -1
caminos = {}
for i in range(0,7):
    caminos[i] = [1]
caminos[7] = [i for i in range(1,15)]
caminos[8] = [i for i in range(1,15)]
caminos[9] = [i for i in range(1,15)]
for i in range(10,17):
    caminos[i] = [7]

for row_index in range(0,17):
    for column_index in caminos[row_index]:
        rewards[row_index, column_index] = -1

#Checar si la posición es terminal

def carTrajectory():
    loc = np.random.randint(1,4)
    if loc ==1:
        return [0,1],[10,1]
    elif loc ==2:
        return [16,7],[6,7]
    else:
        return [8,14],[8,0]

def carAdvance(currenty,currentx, targetpos):
    if targetpos == [10,1] and rewards[currenty +1,currentx] >= rewards[currenty,currentx]:
        return [currenty + 1,currentx]
    elif targetpos == [6,7] and rewards[currenty -1,currentx] >= rewards[currenty,currentx]:
        return [currenty - 1, currentx]
    elif targetpos == [8,0] and rewards[currenty,currentx-1] >= rewards[currenty,currentx]:
        return [currenty, currentx - 1]
    elif rewards[currenty, currentx]==100:
        return [currenty,currentx]

def carMove(positions):
    positions[0][0] = carAdvance(positions[0][0], positions[0][1], positions[1])[0]
    positions[0][1] = carAdvance(positions[0][0], positions[0][1], positions[1])[1]
    print(positions[0])
    return positions
    
stoplight = {}
stoplight[0] = [8,[2,3,4,5,6],True]
stoplight[1] = [[1,2,3,4,5,6],1,False]
stoplight[2] = [[10,11,12,13,14,15,16],7,False]
stoplight[3] = [8,[8,9,10,11,12,13,14],True]

def switchStoplight():
    #True = Verde :. False = Rojo
    if stoplight[0][2]:
        stoplight[0][2] = False
        stoplight[1][2] = True
        stoplight[2][2] = True
        stoplight[3][2] = False

        #Preferencia EGS
        rewards[8,1]=rewards[8,7] = -100
        rewards[7,1]=rewards[9,7] = -1

    else:
        stoplight[0][2] = True
        stoplight[1][2] = False
        stoplight[2][2] = False
        stoplight[3][2] = True

        #Preferencia Luis Elizondo
        rewards[8,1]=rewards[8,7] = -1
        rewards[7,1]=rewards[9,7] = -100


#Get Spawn and Despawn positions
positions = carTrajectory()

for row in rewards:
    print(row)

while(positions[0]!= positions[1]):
    switchStoplight()
    positions = carMove(positions)

for row in rewards:
    print(row)



""" 
for i in range(0,len(stoplight)):
    for j in range(0,len(stoplight[i])):
        print(stoplight[i][j])
 """
