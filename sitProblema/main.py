from random import Random
import agentpy as ap
import numpy as np

# Agentes ------------------------------------------------------------------------------------
class Car(ap.Agent):
    """Clase para todos los agentes de tipo carro. Los carros acutalizaran
    su velocidad en base a los semaforos, topes y otros carros en frente de ellos.
    La posición real del carro se conseguira con self.space.positions[self] (float tuple)
    """

    def setup(self):

        #Waypoints
        self.current_waypoint #De donde sale actualmente
        self.next_waypoint #Al que se dirije
        self.destination #Destino del carro

        #Dimensiones del carro
        self.length=4
        self.width=2
        self.veiw_range=5

        #Variables del carro
        self.velocity = 0
        self.rendimiento = 100 #El carro se descompone (obstaculo) si rendimiento llega a 0

    def setup_pos(self, space):
        """Se le asigna al carro su posicion actual y su destino, ambos al azar.
        Su next_waypoint se asigna en update_waypoint()
        Tambien se guarda el espacio (space) localmente para no tener que llamarlo en otras funciones."""
        
        self.space = space

        self.current_waypoint = space.waypoints_graph[space.positions[self]]
        self.destination = space.generators[random]
        pass

    def update_velocity(self):
        """Se actualiza la velocidad del carro dependiendo de sus neighbors, incluyendo
        semaforos, obstaculos y otros carros"""
        nbs = self.space.neighbors(self, self.veiw_range)

    def speedup(self):
        speed = speed + 1

    def slowdown(self):
        if (speed > 0):
            speed = speed -1
    

class Stoplight(ap.Agent):
    def setup(self):
        self.pos
        self.state
        self.cross_section

    def changeState(self):
        pass

class SpeedBump(ap.Agent):
    def setup(self):
        self.pos

class DropOff(ap.Agent):
    def setup(self):
        self.pos
        self.occupied = False

# Modelo -------------------------------------------------------------------------------------
class ModelMap(ap.Model):

    self.waypoints_graph
    self.generators


    def setup(self):
        """Estados que pueden tener las posiciones:
        - occupied: el espacio esta ocupado por un vehiculo
        - blocked: el espacio esta bloqueado por un obstaculo
        - free: el espacio esta libre para que un carro pase
        """

        self.space = ap.Space(self,shape=(p.length, p.height))
        self.position_states
        self.carAgents = ap.AgentList(self, self.p.population, Car)
        self.stoplightAgents = ap.AgentList(self, self.p.population, Stoplight)
        self.speedBumpAgents = ap.AgentList(self, self.p.population, SpeedBump)
        self.dropOffAgents = ap.AgentList(self, self.p.population, DropOff)
        self.space.add_agents(self.carAgents, random=True)
        self.space.add_agents(self.stoplightAgents, p.stoplightPos)
        self.space.add_agents(self.speedBumpAgents, p.speedBumpPos)
        self.space.add_agents(self.dropOffAgents, p.dropOffPos)

    def step(self):
        self.stoplightAgents.changeState()