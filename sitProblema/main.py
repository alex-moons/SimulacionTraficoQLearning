import math
from multiprocessing.resource_sharer import stop
from pydoc import ispackage
import random
from tempfile import tempdir
import agentpy as ap
import numpy as np
import matplotlib.pyplot as plt
import IPython
import networkx as nx
import socket
import time

""" El modelo de agentpy no tiene coordenadas negativas, mientras que Unity si tiene. Para resolver
este problema se decidio que el modelo de agentpy esta desfazado por MARGIN para que no ocupe coordenadas
negativas. Las posiciones y velocidades son calculadas y reflejadas adecuadamente en Unity """
MARGIN = 500.0

# Funciones vectoriales ----------------------------------------------------------------------
def normalize(v):
    """ Normaliza el vector a tamaño 1 """
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm

def mag(x):
    """ Magnitud de un vector """
    return math.sqrt(sum(i**2 for i in x))

def distance(a, b):
    """ Magnitud de distancia entre dos puntos """
    return ((a[0] - b[0])**2 + (a[1] - b[1])**2)**0.5

def vector_distance(a, b):
    """ Vector de distancia entre 2 puntos """
    return [a[0] - b[0], a[1] - b[1]]

def get_waypoints_edge_list(receivedData: str):
    """ La funcion recibe un string con todos los edges y los transforma en una lista
    para despues agregar las edges a un DiGraph. El string debe ser de formato:
    (x1,y1)&(x1,y2)&weight1;(x3,y3)&(x4,y4)&weight2;...# """
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
    su velocidad en base a los semaforos y otros carros en frente de ellos.

    Atributos:
        length, width (int):
            dimensiones del carro
        view_range (int):
            el radio de vision que tiene el carro para identificar neighbors
        velocity (numpy.ndarray):
            vector de velocidad del carro en dos dimensiones
        speed (float):
            rapidez del vector de velocidad
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
        pathway (list of (float tuple)):
            camino generado por A* desde current_waypoint a destination
    """

    def setup(self):
        #Dimensiones del carro
        self.length=4
        self.width=2
        self.veiw_range=40

        #Variables del carro
        self.velocity = [0, 0]
        self.speed = 0.2
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

        #Activar el carro en el espacio del modelo
        self.active = True

        #Asignarle un camino con (A*)
        pathway_possible = False
        while (not pathway_possible):
            try:
                self.pathway=nx.astar_path(self.waypoints, self.current_waypoint, self.destination)
                pathway_possible = True
            except nx.NetworkXNoPath:
                #Si no existe un camino posible, se cambia el destination
                self.destination = self.model.endpoints[random.randint(0,len(self.model.endpoints)-1)]
        self.next_waypoint = self.pathway[1]

    def update_velocity(self):
        """Se actualiza la velocidad del carro dependiendo de sus neighbors, incluyendo
        semaforos y otros carros"""
        
        #Se crea una lista con los waypoints adyacentes del current_waypoint
        #El carro se detiene si todos los caminos estan ocupados
        is_path_free = [True for i in range(len(self.waypoints[self.current_waypoint]))]
        self.velocity = normalize(vector_distance(self.next_waypoint,self.pos))
        self.velocity[0] *= self.speed
        self.velocity[1] *= self.speed

        #Busca todos los vecinos a su alrededor (Stoplights, Cars)
        for nb in self.space.neighbors(self, self.veiw_range):
            #El carro se detiene por completo si está en frente de un semaforo rojo
            if (isinstance(nb, Stoplight)):
                if (not nb.state):
                    for waypoint in nb.assigned_waypoints:
                        if (distance(self.pos, waypoint) <= 3):
                            self.velocity[0] *= 0
                            self.velocity[1] *= 0 
            
            #El carro busca otros caminos si un carro detenido esta en frente suyo
            elif (isinstance(nb, Car)):
                if (self.next_waypoint == nb.current_waypoint):
                    #Si solo hay un camino posible, el carro se detiene atras del otro
                    if (len(self.waypoints[self.current_waypoint]) != 1):
                        i = 0
                        for other_path in self.waypoints[self.current_waypoint]:
                            for other_nb in self.space.neighbors(self, self.veiw_range):
                                if (isinstance(other_nb, Car)):
                                    if (other_path == other_nb.next_waypoint or self.next_waypoint == other_nb.next_waypoint):
                                        is_path_free[i] = False
                                        break
                            try:
                                self.pathway=nx.astar_path(self.waypoints, other_path, self.destination)
                                self.next_waypoint = other_path
                            except nx.NetworkXNoPath:
                                is_path_free[i] = False
                            i += 1
                    else:
                        is_path_free[0] = False

                    try:
                        new_path = list(self.waypoints[self.current_waypoint])[is_path_free.index(True)]
                        self.pathway=nx.astar_path(self.waypoints, new_path, self.destination)
                        self.next_waypoint = new_path
                    except ValueError:
                        self.velocity[0] *= 0
                        self.velocity[1] *= 0

                dist = (self.pos[0] + (self.velocity[0] * self.length*5), self.pos[1] + (self.velocity[1] * self.length*5))
                #print(self.pos, dist)
                if (distance(nb.pos, dist) <= 4):
                    self.velocity[0] *= 0
                    self.velocity[1] *= 0

        
    def update_waypoint(self):
        """Se actualizan los waypoints cuando el carro llega a next_waypoint. Si el carro
        llega a su destino, este se remueve del espacio y se desactiva."""

        #Revisa si se llego a la distancia minima
        if (distance(self.pos, self.next_waypoint) <= 1):
            self.current_waypoint = self.next_waypoint
            #Si llego a su destino, se remueve y desactiva el carro
            if ((self.next_waypoint == self.destination) or (len(self.waypoints[self.current_waypoint]) == 0)):
                self.active = False
                self.space.remove_agents(self)
            else:
                #Si todavia no llega a su destino, se agarra el camino más corto de
                #los nodos adyacentes, siempre y cuando tenga camino posible a destination
                dist = distance(self.pos, self.destination)
                for paths in self.waypoints[self.current_waypoint]:
                    if (distance(self.pos, paths) < dist):
                        try:
                                self.pathway=nx.astar_path(self.waypoints, paths, self.destination)
                                self.next_waypoint = paths
                                dist = distance(self.pos, paths)
                        except nx.NetworkXNoPath:
                            pass
                if (dist == distance(self.pos, self.destination)):
                    self.next_waypoint = self.destination
                else:
                    self.next_waypoint = self.pathway[0]
                
    def update_pos(self):
        """Se actualiza la posicion del carro en base a su velocidad"""
        self.update_waypoint()
        if (self.active):
            self.update_velocity()
            self.pos = (self.pos[0] + self.velocity[0], self.pos[1] + self.velocity[1])
            self.space.move_by(self, self.velocity)    

class Stoplight(ap.Agent):
    """Los semaforos pertenecen a un cruce con ID y se les asigna un waypoint del cual los carros
    no se pueden pasar si el semaforo se encuentra en rojo.

    Atributos:
        id (int):
            identificador del semaforo necesario para comunicarse con el otro semaforo
            de su cruce
        pos (float tuple):
            posicion del primer assigned_waypoint, el cual es detectado por los carros
        assigned_waypoints (list of (float tuple)):
            lista de waypoints pertenecientes al semaforo. Los carros se deben detener ahi si el
            semaforo esta en rojo
        crossway_stoplight (int):
            identificador del otro semaforo en el mismo cruce de este semaforo
        state (bool):
            el estado del semaforo. True = rojo, False = verde
        interval_time (int):
            tiempo que tarda el semaforo en cambiar su state
        already_changed (bool):
            indica si el semaforo ya cambio su state dentro de un mismo step
    """

    def setup(self):
        self.state = True
        self.interval_time = 5
        self.already_changed = False

    def setup_pos(self, model: ap.Model, id):
        """ Se establecen los datos iniciales del semaforo"""
        stoplight_info = model.stoplights_list[id]
        self.id = stoplight_info[0]
        self.crossway_stoplight = stoplight_info[1]
        self.assigned_waypoints = stoplight_info[2]
        self.pos = stoplight_info[2][0]

    def setup_crossway_state(self, model: ap.Model):
        """ Cambia los estados de los semaforos de un mismo cruce """
        self.already_changed = True
        self.state = not self.state
        for stoplight in model.stoplight_agents:
            if stoplight.id == self.crossway_stoplight:
                stoplight.state = not self.state
                stoplight.already_changed = True

    def change_state(self, model: ap.Model):
        """ Detecta si ya paso el intervalo de cambio de estado """
        if ((math.floor(time.time()) - model.model_start_time)%self.interval_time == 0 
        and not self.state and not self.already_changed):
            self.setup_crossway_state(model)
        else:
            if ((math.floor(time.time()) - model.model_start_time)%self.interval_time != 0):
                self.already_changed = False

# MODELO -------------------------------------------------------------------------------------
class ModelMap(ap.Model):
    """La clase del modelo multi-agentes. Debe recibir un dict con parametros. 
    En setup se crean todos los agentes y se crea el grafo de waypoints en base a
    la informacion recibida de Unity
    
    Atributos:
        p (dict):
            Lista de parametros necesarios:
                length, height (int): el tamaño del modelo, debe ser igual o mas grande
                    que el mapa de Unity
                population (int): numero maximo de agentes
                steps (int): tiempo que dura la simulacion. Los steps son infinitos
                    si no se pasa este parametro
                seed (int): semilla que determina la randomness del modelo
        sock (socket.socket):
            el socket de transmision de datos con Unity. Tiene IP y puerto
        waypoints_graph (networkx.Digraph de tuple(float, float)):
            grafo direccionado con los waypoints y sus conexiones
        generators (list of tuple(float, float)):
            lista con los generadores, donde pueden generarse carros
        endpoints (list of tuple(float, float)):
            lista con los endpoints, donde pueden desactivarse carros
        space (agentpy.Space):
            Espacio donde interactuan los agentes del modelo
        car_agents (agentpy.AgenList):
            Lista con todos los agentes de tipo Car
        stoplight_agents (agentpy.AgenList):
            Lista con todos los agentes de tipo Stoplight
        model_start_time (float):
            tiempo, en segundos, de cuando se empezo a correr el programa. Es necesario para
            contar el intervalo de cambio de estado en los semaforos
        average_velocity (list of tuple (int, float)):
            lista de las velocidades promedio de cada step del programa
    """

    def setup(self):
        """ Primero se inicaliza la conexion TCP con Unity, luego se reciben todos los datos
        de posiciones de waypoints y semaforos. """

        #Conexion TCP con Unity
        host, port = "127.0.0.1", 25001
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #La siguiente linea comentada de codigo sirve para abrir el puerto, porque existe la
        #posibilidad de que el codigo mande error de conexion rechazada.
        #self.sock.bind((host, port))
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

        #Se inicializa el espacio (agentpy.Space) y se crean las listas de agentes
        self.space = ap.Space(self,shape=(self.p.length, self.p.height))
        self.car_agents = ap.AgentList(self, self.p.population, Car)
        self.stoplight_agents = ap.AgentList(self, len(self.stoplights_list), Stoplight)

        #Se inicializa la informacion de los semaforos
        info_index = 0
        for stoplight in self.stoplight_agents:
            stoplight.setup_pos(self, info_index)
            stoplight_pos = self.stoplights_list[info_index][2]
            self.space.add_agents([stoplight], [[round(stoplight_pos[0][0]+MARGIN,4), round(stoplight_pos[0][1]+MARGIN,4)]])
            info_index += 1
        
        for stoplight in self.stoplight_agents:
            stoplight.setup_crossway_state(self)

        #Se inicializa el tiempo del programa para los intervalos de los semaforos
        #Tambien se inicializa la lista que contiene las velocidades promedio
        self.model_start_time = math.floor(time.time())
        self.average_velocity = list()
        print("Space setup done")

    def step(self):
        
        #Crea la lista de stoplights con sus estados
        stoplights_out_info = "stoplights:"
        for stoplight in self.stoplight_agents:
            stoplight.change_state(self)
            stoplights_out_info += str(stoplight.id) + "&" + str(stoplight.state) + ";"
        
        #Se manda la lista a Unity y se espera una respuesta
        self.sock.sendall(stoplights_out_info.encode("UTF-8"))
        receivedData = ""
        while (receivedData == ""):
            receivedData = self.sock.recv(1048576).decode("UTF-8")

        #Se actualiza la informacion de los carros y se guarda en una lista
        total_velocity = 0
        active_cars = 0
        car_out_info = "cars:"
        for car in self.car_agents:
            #Si el carro no se encuentra activado hay un 40% de chance de activarlo
            if (not car.active):
                if (random.randint(1, 100) >= 60):
                    startPos = self.generators[random.randint(0, len(self.generators)-1)]
                    self.space.add_agents([car], [[round(startPos[0]+MARGIN,4), round(startPos[1]+MARGIN,4)]])
                    if (len(self.space.neighbors(car, 10)) != 0):
                        self.space.remove_agents(car)
                        car.active = False
                    else:
                        car.setup_pos(self)
            #En caso de que el carro este activado, se actualiza su posicion
            else:
                car.update_pos()
                carpos = str(car.pos)
                car_info = str(car.id) + ";" + carpos + "&"
                car_out_info += car_info
                total_velocity += mag(car.velocity)
                active_cars += 1

        #Se registan las velocidades para conseguir la average_velocity del step
        if (active_cars != 0):
            self.average_velocity.append((self.t,total_velocity/active_cars))
        else:
            self.average_velocity.append((self.t,0))
        
        #Se manda la informacion a Unity y se espera una respuesta para iniciar
        #el siguiente step
        self.sock.sendall(car_out_info.encode("UTF-8"))
        receivedData = ""
        while (receivedData == ""):
            receivedData = self.sock.recv(1048576).decode("UTF-8")

    def end(self):
        """ Al final de la ejecucion del modelo, se recopila la velocidad promedio
        de los steps y se manda un plot """
        xs = [x[0] for x in self.average_velocity]
        ys = [x[1] for x in self.average_velocity]
        plt.plot(xs, ys)
        plt.show()

# ---------------------------------------------------------------------------------
parameters = {
    'length': 1000,
    'height': 1000,
    'population': 50,
    'steps': 1500,
    'seed': 123,
}
# MAIN-----------------------------------------------------------------------------

#Se crea la instancia del modelo y se inicia la simulacion
model_map = ModelMap(parameters)
res = model_map.run()