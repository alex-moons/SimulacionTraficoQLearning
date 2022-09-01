from operator import mod
import random
import agentpy as ap
import numpy as np
import matplotlib.pyplot as plt
import IPython
import networkx as nx
import socket
import time

# Funciones vectoriales ----------------------------------------------------------------------
def normalize(v):
    """ Normalize a vector to length 1. """
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm

def distance(a, b):
    return ((a[0] - b[0])**2 + (a[1] - b[1])**2)**0.5

def vector_distance(a, b):
    return [a[0] - b[0], a[1] - b[1]]

# Agentes ------------------------------------------------------------------------------------
class Car(ap.Agent):
    """Clase para todos los agentes de tipo carro. Los carros acutalizaran
    su velocidad en base a los semaforos, topes y otros carros en frente de ellos.

    Atributos:
        length, width (int):
            dimensiones del carro
        view_range (int):
            el radio de vision que tiene el carro para identificar neighbors
        velocity (numpy.ndarray):
            vector de velocidad del carro en dos dimensiones
        speed (float):
            rapidez del vector de velocidad
        rendimiento (int):
            El carro se descompone (obstaculo) si rendimiento llega a 0
        model (agentpy.Model):
            el modelo al cual el carro pertenece
        space (agentpy.Space):
            el espacio del model del carro
        pos (float tuple):
            posicion actual del carro. Su posicion puede estar entre waypoints
        waypoints (list of (float tuple)):
            lista con todos los waypoints
        current_waypoint (float tuple):
            waypoint de donde sale el carro
        next_waypoint (float tuple):
            waypoint a donde se dirige el carro
        destination (float tuple):
            destino del carro
    """

    def setup(self):
        #Dimensiones del carro
        self.length=4
        self.width=2
        self.veiw_range=5

        #Variables del carro
        self.velocity = 0
        self.rendimiento = 100 #El carro se descompone (obstaculo) si rendimiento llega a 0

    def setup_pos(self, model: ap.Model):
        """Se le asigna al carro su posicion actual y su destino, ambos al azar.
        Su next_waypoint se asigna en update_waypoint()
        """
        
        self.model = model
        self.space = model.space
        self.waypoints = self.model.waypoints_list

        self.current_waypoint = self.waypoints[random.randint(0,len(self.waypoints)-1)]
        self.pos = self.current_waypoint
        self.destination = self.waypoints[random.randint(0,len(self.waypoints)-1)]
        self.next_waypoint = self.waypoints[random.randint(0,len(self.waypoints)-1)]

        self.space.move_to(self, np.asarray(self.pos))

    def update_velocity(self):
        """Se actualiza la velocidad del carro dependiendo de sus neighbors, incluyendo
        semaforos, obstaculos y otros carros"""

        #nbs = self.space.neighbors(self, self.veiw_range)
        self.velocity = normalize(vector_distance(self.next_waypoint,self.pos))
        self.velocity[0] *= 1
        self.velocity[1] *= 1
        
    def update_waypoint(self):
        """Se actualizan los waypoints cuando el carro llega a next_waypoint"""

        if (distance(self.pos, self.next_waypoint) <= 0.2):
            self.current_waypoint = self.next_waypoint
            if (self.next_waypoint == self.destination):
                #if (space.position_states[self.pos] == "generator"):
                #self.space.remove_agents(self)
                while (self.destination == self.current_waypoint):
                    self.destination = self.waypoints[random.randint(0,len(self.waypoints)-1)]

            while (self.next_waypoint == self.current_waypoint): 
                self.next_waypoint = self.waypoints[random.randint(0,len(self.waypoints)-1)]


    def update_pos(self):
        """Se actualiza la posicion del carro en base a su velocidad"""
        self.update_waypoint()
        self.update_velocity()

        self.pos = (self.pos[0] + self.velocity[0], self.pos[1] + self.velocity[1])
        self.space.move_by(self, self.velocity)
    

class Stoplight(ap.Agent):
    """Los semaforos pertenecen a un cruce con ID y se les asigna un waypoint del cual los carros
    no se pueden pasar si el semaforo se encuentra en rojo.

    Atributos:
        pos (float tuple):
            posicion real del semaforo. No forma parte de los waypoints
        assigned_waypoint (float tuple):
            el waypoint perteneciente al semaforo. Los carros se deben detener ahi si el
            semaforo esta en rojo
        cross_section (int):
            ID del cruce al cual pertenece el semaforo
        state (int):
            el estado del semaforo. 0 = verde, 1 = amarillo, 2 = rojo
    """

    def setup(self):
        self.state = 1
        self.cross_section = 1

    def setup_pos(self, model: ap.Model):
        self.pos = model.space.positions[self]
        self.assigned_waypoint = model.p.assigned_waypoint[model.p.pos_stoplight.index(self.pos)]

    def changeState(self):
        pass


class SpeedBump(ap.Agent):
    def setup(self):
        self.pos


class DropOff(ap.Agent):
    """Los drop-offs son lugares donde los carros se pueden estacionar. Cada uno tiene su 
    ubicacion y su estado de si esta ocupado o no

    Atributos:
        pos (float tuple):
            posicion real del drop-off
        occupied (bool):
            indica si el drop-off esta ocupado
    """

    def setup(self):
        self.pos
        self.occupied = False
    
    def setup_pos(self, model: ap.Model):
        self.pos = model.space.positions[self]

    def change_state(self):
        self.occupied = not self.occupied

# Modelo -------------------------------------------------------------------------------------
class ModelMap(ap.Model):
    """La clase del modelo multi-agentes. Debe recibir un dict con parametros. 
    En setup se crean todos los agentes y se crea el grafo de waypoints en base a
    la informacion recibida de Unity
    
    Atributos:
        p (dict):
            Lista de parametros necesarios:
                population (int): numero maximo de agentes
                steps (int): tiempo que dura la simulacion
                waypoints (list of (int tuple)): lista de nodos donde hay waypoints
                waypoint_edges (list of [(int tuple), (int tuple), int]): lista con los
                edges y sus pesos
        waypoints_list (list of (int tuple)):
            lista donde se guarda p.waypoints
        waypoints_graph (networkx.Digraph):
            grafo direccionado con los waypoints y sus conexiones
        space (agentpy.Space):
            Espacio donde interactuan los agentes del modelo
        carAgents (agentpy.AgenList):
            Lista con todos los agentes de tipo Car
    """

    def setup(self):
        """Estados que pueden tener las posiciones:
        - occupied: el espacio esta ocupado por un vehiculo
        - blocked: el espacio esta bloqueado por un obstaculo
        - free: el espacio esta libre para que un carro pase
        - generator: carros son creados y destruidos en estos puntos
        """
        self.waypoints_list = self.p.waypoints
        self.waypoints_graph = nx.DiGraph()
        self.waypoints_graph.add_nodes_from(self.p.waypoints)
        for edge in self.p.waypoint_edges:
            self.waypoints_graph.add_edge(edge[0], edge[1], weight=edge[2])
        #self.generators

        self.space = ap.Space(self,shape=(self.p.length, self.p.height))
        #self.position_states
        self.carAgents = ap.AgentList(self, self.p.population, Car)
        #self.stoplightAgents = ap.AgentList(self, self.p.population, Stoplight)
        #self.speedBumpAgents = ap.AgentList(self, self.p.population, SpeedBump)
        #self.dropOffAgents = ap.AgentList(self, self.p.population, DropOff)
        self.space.add_agents(self.carAgents, random=True)
        self.carAgents.setup_pos(self)
        print("Setup done")
        #self.space.add_agents(self.stoplightAgents, p.stoplightPos)
        #self.space.add_agents(self.speedBumpAgents, p.speedBumpPos)
        #self.space.add_agents(self.dropOffAgents, p.dropOffPos)

    def step(self):
        #self.stoplightAgents.changeState()
        #print("Initiate step")
        self.carAgents.update_pos()
        #print("Step done")

def animation_plot_single(m, ax):
    ax.set_title(f"AgentPy {2}D t={m.t}")
    pos = m.space.positions.values()
    pos = np.array(list(pos)).T  # Transform
    ax.scatter(*pos,marker=[(-2,-1),(2,-1),(2,1),(-2,1)],c='black')
    #ax.scatter(0,0,c='red')
    ax.scatter(20,30,c='red')
    ax.scatter(30,30,c='red')
    ax.scatter(30,20,c='red')
    ax.scatter(20,20,c='red')
    ax.set_xlim(0, m.p.size)
    ax.set_ylim(0, m.p.size)
    ax.set_axis_off()

def animation_plot(m, p):
    projection = None
    fig = plt.figure(figsize=(7,7))
    ax = fig.add_subplot(111, projection=projection)
    animation = ap.animate(m(p), fig, ax, animation_plot_single)
    plt.show()
    print("Show plt")
    return IPython.display.HTML(animation.to_jshtml(fps=20))

parameters = {
    'length': 50,
    'height': 50,
    'population': 1,
    'size': 50,
    #'steps': 100,
    'seed': 123,
    'waypoints': [(20,30),(30,30),(20,20),(30,20)],
    'waypoint_edges': [[(20,30), (30,30), 5],
                        [(30,30), (30,20), 5],
                        [(30,20), (20,20), 5],
                        [(20,20), (20,30), 5],],
    'pos_stoplight': [(25, 25)],
    'assigned_waypoint': [(20, 20)]
}

# ---------------------------------------------------------------------------------

host, port = "127.0.0.1", 36258
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))

startPos = [0, 0, 0] #Vector3   x = 0, y = 0, z = 0

receivedData = sock.recv(1024).decode("UTF-8")

while receivedData is None:
    print(".", end="")
    receivedData = sock.recv(1024).decode("UTF-8")
    """time.sleep(0.5) #sleep 0.5 sec
    startPos[0] +=1 #increase x by one
    posString = ','.join(map(str, startPos)) #Converting Vector3 to a string, example "0,0,0"
    print(posString)

    sock.sendall(posString.encode("UTF-8")) #Converting string to Byte, and sending it to C#
    receivedData = sock.recv(1024).decode("UTF-8") #receiveing data in Byte fron C#, and converting it to String
    print(receivedData)"""
print("")
print(receivedData)

animation_plot(ModelMap, parameters)
#mod = ModelMap(parameters=parameters)
#print(mod.run()['info'])

#https://www.redblobgames.com/pathfinding/a-star/implementation.html