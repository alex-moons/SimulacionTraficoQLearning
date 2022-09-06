import math
from multiprocessing.resource_sharer import stop
import random
from tempfile import tempdir
import agentpy as ap
import numpy as np
import matplotlib.pyplot as plt
import IPython
import networkx as nx
import socket
import time

MARGIN = 500.0

# Funciones vectoriales ----------------------------------------------------------------------
def normalize(v):
    """ Normaliza el vector a tamaño 1 """
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm

def distance(a, b):
    """Magnitud de distancia entre dos puntos"""
    return ((a[0] - b[0])**2 + (a[1] - b[1])**2)**0.5

def vector_distance(a, b):
    """Vector de distancia entre 2 puntos"""
    return [a[0] - b[0], a[1] - b[1]]

def get_waypoints_edge_list(receivedData: str):
    """La funcion recibe un string con todos los edges y los transforma en una lista
    para despues agregar las edges a un DiGraph. El string debe ser de formato:
    (x1,y1)&(x1,y2)&weight1;(x3,y3)&(x4,y4)&weight2;...#"""
    waypoint_edges = list()
    edgeList = receivedData.split(";")
    for edge in edgeList:
        if (edge != "" and edge != "#"):
            items = edge.split('&')
            waypoint_edge = list()
            node = items[0].split(",")
            x = node[0]
            y = node[1]
            x = x[1:]
            y = y[:-1]
            waypoint_edge.append((round(float(x),4),round(float(y),4)))

            node = items[1].split(",")
            x = node[0]
            y = node[1]
            x = x[1:]
            y = y[:-1]
            waypoint_edge.append((round(float(x),4),round(float(y),4)))

            waypoint_edge.append(int(items[2]))

            waypoint_edges.append(waypoint_edge)
        elif (edge == "#"):
            waypoint_edges.append("#")
    
    return waypoint_edges

def get_generators_endpoints(receivedData: str):
    """Recibe un string con los generadores o los endpoints y los convierte en una lista.
    El formato del string es:
    (x1,y1)&(x1,y1)&...#"""
    waypoint_edges = list()
    edgeList = receivedData.split("&")
    for edge in edgeList:
        if (edge != "" and edge != "#"):
            items = edge.split(',')
            x = items[0]
            y = items[1]
            x = x[1:]
            y = y[:-1]
            waypoint_edges.append((round(float(x),4),round(float(y),4)))
        elif (edge == "#"):
            waypoint_edges.append("#")
    return waypoint_edges

def get_stoplights(received_data: str):
    """Formato id1&cross1&(x1,y1)&(x2,y2)&...;id2&cross2&(x3,y3)&(x4,y4)&...;...#"""
    stoplights_id_list = list()
    stoplights_waypoint_list = list()
    stoplights_list = received_data.split(';')
    for stoplight in stoplights_list:
        if (stoplight != "" and stoplight != "#"):
            data = stoplight.split('&')
            stoplights_id_list.append([int(data[0]),int(data[1])])
            data.remove(data[0])
            data.remove(data[0])
            waypoints = list()
            for waypoint in data:
                items = waypoint.split(',')
                x = items[0]
                y = items[1]
                x = x[1:]
                y = y[:-1]
                waypoints.append((round(float(x),4),round(float(y),4)))
            stoplights_waypoint_list.append(waypoints)
        elif (stoplight == "#"):
            stoplights_id_list.append([-1,-1])
            stoplights_waypoint_list.append("#")

    return stoplights_id_list, stoplights_waypoint_list

# AGENTES ------------------------------------------------------------------------------------
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
        active (bool):
            Muestra si el carro se encuentra activo dentro del espacio del modelo
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
        self.veiw_range=40

        #Variables del carro
        self.velocity = 0
        self.speed = 0.2
        self.rendimiento = 100
        self.active = False

    def setup_pos(self, model: ap.Model):
        """Se le asigna al carro su posicion actual de la lista de generadores
        y su destino de la lista de endpoints, ambos al azar.
        Su next_waypoint se asigna en update_waypoint()
        """
        
        #Se asigna la instancia del modelo, su espacio y el grafo con los waypoints
        self.model = model
        self.space = model.space
        self.waypoints = self.model.waypoints_graph
        self.pathway = list()

        #Se asignan los waypoints
        self.current_waypoint = (round(self.space.positions[self][0]-MARGIN,4), round(self.space.positions[self][1]-MARGIN,4))
        self.pos = self.current_waypoint
        self.destination = self.model.endpoints[random.randint(0,len(self.model.endpoints)-1)]
        #self.next_waypoint = list(self.waypoints[self.current_waypoint])[random.randint(0,len(self.waypoints[self.current_waypoint])-1)]

        #Activar el carro en el espacio del modelo
        self.active = True

        #Asignarle un camino inicial siendo el más corto (A*)
        pathway_possible = False
        while (not pathway_possible):
            #print(self.waypoints[self.destination])
            #print(self.waypoints[self.current_waypoint])
            
            try:
                self.pathway=nx.astar_path(self.waypoints, self.current_waypoint, self.destination)
                pathway_possible = True
            except nx.NetworkXNoPath:
                self.destination = self.model.endpoints[random.randint(0,len(self.model.endpoints)-1)]
        self.next_waypoint = self.pathway[1]
        #print(self.pathway)
        # mandar info de 'shortest_pathway' hacia el unity, para que este ultimo los mande al carro

    def update_velocity(self):
        """Se actualiza la velocidad del carro dependiendo de sus neighbors, incluyendo
        semaforos, obstaculos y otros carros"""
        self.velocity = normalize(vector_distance(self.next_waypoint,self.pos))
        self.velocity[0] *= self.speed
        self.velocity[1] *= self.speed

        for nb in self.space.neighbors(self, self.veiw_range):
            if (isinstance(nb, Stoplight)):
                if (not nb.state):
                    for waypoint in nb.assigned_waypoints:
                        #print(self.pos, self.space.positions[self], nb.pos, self.space.positions[nb], distance(self.pos, waypoint))
                        if (distance(self.pos, waypoint) <= 3):
                            self.velocity[0] *= 0
                            self.velocity[1] *= 0 
        
    def update_waypoint(self):
        """Se actualizan los waypoints cuando el carro llega a next_waypoint. Si el carro
        llega a su destino, este se remueve del espacio y se desactiva."""

        #Revisa si se llego a la distancia minima
        if (distance(self.pos, self.next_waypoint) <= 1):
            self.current_waypoint = self.next_waypoint
            if ((self.next_waypoint == self.destination) or (len(self.waypoints[self.current_waypoint]) == 0)):
                self.active = False
                self.space.remove_agents(self)
            else:
                self.pathway=nx.astar_path(self.waypoints, self.current_waypoint, self.destination)
                self.next_waypoint = self.pathway[1]
                

    def update_pos(self):
        """Se actualiza la posicion del carro en base a su velocidad"""
        self.update_waypoint()
        if (self.active):
            self.update_velocity()
            self.pos = (self.pos[0] + self.velocity[0], self.pos[1] + self.velocity[1])
            self.space.move_by(self, self.velocity)
            #print(self.pos, self.space.positions[self])
    

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
        state (bool):
            el estado del semaforo. True = rojo, False = verde
    """

    def setup(self):
        self.state = True
        self.interval_time = 10
        self.already_changed = False

    def setup_pos(self, model: ap.Model, id):
        stoplight_info = model.stoplights_list[id]
        self.id = stoplight_info[0]
        self.crossway_stoplight = stoplight_info[1]
        self.assigned_waypoints = stoplight_info[2]
        self.pos = stoplight_info[2][0]

    def setup_crossway_state(self, model: ap.Model):
        self.already_changed = True
        self.state = not self.state
        for stoplight in model.stoplight_agents:
            if stoplight.id == self.crossway_stoplight:
                stoplight.state = not self.state
                stoplight.already_changed = True

    def change_state(self, model: ap.Model):
        #print((math.floor(time.time()) - model.model_start_time)%self.interval_time)
        if ((math.floor(time.time()) - model.model_start_time)%self.interval_time == 0 
        and not self.state and not self.already_changed):
            self.setup_crossway_state(model)
            #print("state changed")
        else:
            if ((math.floor(time.time()) - model.model_start_time)%self.interval_time != 0):
                self.already_changed = False


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
                steps (int): tiempo que dura la simulacion. Los steps son infinitos
                si no se pasa este parametro
        waypoints_graph (networkx.Digraph):
            grafo direccionado con los waypoints y sus conexiones
        generators (list of tuple(float, float)):
            lista con los generadores, donde pueden generarse carros
        endpoint (list of tuple(float, float)):
            lista con los endpoints, donde pueden desactivarse carros
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
        """

        #Conexion TCP con Unity
        host, port = "127.0.0.1", 25001
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.sock.bind((host, port))
        #print("Socket bind")
        self.sock.connect((host, port))
        print("Socket connected")
        tcp_message = "Begin connection"
        self.sock.sendall(tcp_message.encode("UTF-8"))

        #Recibir los edges de waypoints hasta encontrar un #
        received_data = ""
        waypoint_edges = list()
        while (received_data != "#"):
            received_data = self.sock.recv(1048576).decode("UTF-8")
            temp_edge = get_waypoints_edge_list(received_data)
            for i in temp_edge:
                waypoint_edges.append(i)
            if (waypoint_edges[len(waypoint_edges)-1] == '#'):
                waypoint_edges.remove("#")
                received_data = "#"
        
        #Confirmacion a Unity que se recibieron los waypoints
        tcp_message = "waypoints received"
        self.sock.sendall(tcp_message.encode("UTF-8"))

        #Recibir los generators hasta encontrar un #
        received_data = ""
        self.generators = list()
        while (received_data != "#"):
            received_data = self.sock.recv(1048576).decode("UTF-8")
            temp_generators = get_generators_endpoints(received_data)
            for i in temp_generators:
                self.generators.append(i)
            if (self.generators[len(self.generators)-1] == '#'):
                self.generators.remove("#")
                received_data = "#"
        
        #Confirmacion a Unity que se recibieron los generadores
        tcp_message = "generators received"
        self.sock.sendall(tcp_message.encode("UTF-8"))

        #Recibir los endpoints hasta encontrar un #
        received_data = ""
        self.endpoints = list()
        while (received_data != "#"):
            received_data = self.sock.recv(1048576).decode("UTF-8")
            temp_endpoints = get_generators_endpoints(received_data)
            for i in temp_endpoints:
                self.endpoints.append(i)
            if (self.endpoints[len(self.endpoints)-1] == '#'):
                self.endpoints.remove("#")
                received_data = "#"

        #Confirmacion a Unity que se recibieron los endpoints
        tcp_message = "endpoints received"
        self.sock.sendall(tcp_message.encode("UTF-8"))

        #Recibir las stoplights hasta encontrar un #
        received_data = ""
        self.stoplights_list = list()
        while (received_data != "#"):
            received_data = self.sock.recv(1048576).decode("UTF-8")
            temp_ids, temp_waypoints = get_stoplights(received_data)
            for i in temp_ids:
                self.stoplights_list.append((i[0], i[1], temp_waypoints[temp_ids.index(i)]))
            if (self.stoplights_list[len(self.stoplights_list)-1][0] == -1):
                self.stoplights_list.remove(self.stoplights_list[len(self.stoplights_list)-1])
                received_data = "#"

        #Confirmacion a Unity que se recibieron las stoplights
        tcp_message = "stoplights received"
        self.sock.sendall(tcp_message.encode("UTF-8"))

        #Agregar las edges al DiGraph self.waypoints_graph
        self.waypoints_graph = nx.DiGraph()
        for edge in waypoint_edges:
            self.waypoints_graph.add_edge(edge[0], edge[1], weight=edge[2])
        
        for edge in self.waypoints_graph:
            print(edge)

        #Se inicializa el espacio (agentpy.Space) y se crean las listas de agentes
        self.space = ap.Space(self,shape=(self.p.length, self.p.height))
        self.car_agents = ap.AgentList(self, self.p.population, Car)
        self.stoplight_agents = ap.AgentList(self, len(self.stoplights_list), Stoplight)

        info_index = 0
        for stoplight in self.stoplight_agents:
            stoplight.setup_pos(self, info_index)
            stoplight_pos = self.stoplights_list[info_index][2]
            self.space.add_agents([stoplight], [[round(stoplight_pos[0][0]+MARGIN,4), round(stoplight_pos[0][1]+MARGIN,4)]])
            info_index += 1
        
        for stoplight in self.stoplight_agents:
            stoplight.setup_crossway_state(self)

        self.model_start_time = math.floor(time.time())

        print("Space setup done")

    def step(self):
        """
        - Instantiate new cars
        - Change environment
        - Change car positions
        - Send string with info of
            - Stoplights
            - Cars
        """
        
        stoplights_out_info = "stoplights:"
        for stoplight in self.stoplight_agents:
            stoplight.change_state(self)
            stoplights_out_info += str(stoplight.id) + "&" + str(stoplight.state) + ";"
        
        #print(stoplights_out_info)
        self.sock.sendall(stoplights_out_info.encode("UTF-8"))
        receivedData = ""
        while (receivedData == ""):
            receivedData = self.sock.recv(1048576).decode("UTF-8")

        #Actualizar la informacion de los carros y mandar a Unity
        car_out_info = "cars:"
        for car in self.car_agents:
            #Si el carro no se encuentra activado hay un 40% de chance
            #de activarlo
            if (not car.active):
                if (random.randint(1, 100) >= 60):
                    startPos = self.generators[random.randint(0, len(self.generators)-1)]
                    self.space.add_agents([car], [[round(startPos[0]+MARGIN,4), round(startPos[1]+MARGIN,4)]])
                    car.setup_pos(self)
            #En caso de que el carro este activado, se actualiza su posicion
            else:
                car.update_pos()
                carpos = str(car.pos)
                car_info = str(car.id) + ";" + carpos + "&"
                car_out_info += car_info
        
        #Se manda la informacion a Unity y se espera una respuesta para iniciar
        #el siguiente step
        self.sock.sendall(car_out_info.encode("UTF-8"))
        receivedData = ""
        while (receivedData == ""):
            receivedData = self.sock.recv(1048576).decode("UTF-8")

# ---------------------------------------------------------------------------------
parameters = {
    'length': 1000,
    'height': 1000,
    'population': 1,
    'steps': 10000,
    'seed': 124,
}
# MAIN-----------------------------------------------------------------------------

#Se crea la instancia del modelo y se inicia la simulacion
model_map = ModelMap(parameters)
res = model_map.run()

"""
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

host, port = "127.0.0.1", 25001
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.bind((host, port))
print("Socket bind")
sock.connect((host, port))
print("Socket connect")

#conn,addr=sock.accept()
#startPos = [0, 0, 0] #Vector3   x = 0, y = 0, z = 0
posString = "Begin connection" #Converting Vector3 to a string, example "0,0,0"

sock.sendall(posString.encode("UTF-8"))

receivedData = sock.recv(1024).decode("UTF-8")
print("Data received")

while receivedData == "":
    print(".", end="")
    receivedData = sock.recv(1024).decode("UTF-8")
    time.sleep(0.5) #sleep 0.5 sec
    startPos[0] +=1 #increase x by one
    posString = ','.join(map(str, startPos)) #Converting Vector3 to a string, example "0,0,0"
    print(posString)

    sock.sendall(posString.encode("UTF-8")) #Converting string to Byte, and sending it to C#
    receivedData = sock.recv(1024).decode("UTF-8") #receiveing data in Byte fron C#, and converting it to String
    print(receivedData)
print("")
print(receivedData)

animation_plot(ModelMap, parameters)
mod = ModelMap(parameters=parameters)
print(mod.run()['info'])
"""


