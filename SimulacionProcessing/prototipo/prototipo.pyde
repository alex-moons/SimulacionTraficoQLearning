from graph import Graph
from vehicle import Vehicle

g = Graph()

#Av. Luis Elizondo
g.add_edge((590,222),(585,222),30)
g.add_edge((585,222),(570,222),30)
g.add_edge((570,222),(540,222),30)
g.add_edge((540,222),(470,222),30)
g.add_edge((470,222),(300,222),30)
g.add_edge((300,222),(212,222),30)
g.add_edge((212,222),(190,222),30)
g.add_edge((190,222),(85,222),30)
g.add_edge((85,222),(50,222),30)
g.add_edge((50,222),(20,222),30)
#Drop-off Luis Elizondo
g.add_edge((585,222),(570,232),30)
g.add_edge((570,232),(555,222),30)

#C. Asunción
g.add_edge((190,222),(160,280),30)
#Monteviedo
g.add_edge((245,280),(212,222),30)
#Caracas
g.add_edge((300,222),(332,280),30)
#Bogota
g.add_edge((421,280),(470,222),30)
#Av. Junco de la Vega
g.add_edge((490,222),(490,280),30)
g.add_edge((540,20),(570,222),30)

#Av. Eugenio Garza Sada Sur
g.add_edge((103,130),(115,50),30)
g.add_edge((98,158),(103,130),30)
g.add_edge((86,222),(98,158),30)
g.add_edge((75,280),(86,222),30)
#Drop-off Eugenio Garza Sada Sur
g.add_edge((103,130),(108,148),30)
g.add_edge((108,146),(98,158),30)


car = Vehicle(580,222,-3,0,(70,222))


def moveVehicle(vehicle):
    l = 10
    w = 6
    rect(vehicle.x - l/2, vehicle.y - w/2, l, w)
    vehicle.move()
    return vehicle

    """
    l = 10
    w = 6
    translate(vehicle.x, vehicle.y)
    rotate(-PI/3.0)
    rect(-l/2, -w/2, l, w)
    vehicle.move()
    return vehicle
    """


def setup():
    size(600,300)
    
def draw():
    global g
    global car
    
    mapa = loadImage("background.jpg")
    image(mapa,0,0,600,300)
    
    #Crear calles
    fill(255)
    strokeWeight(6)
    for v in g:
        for road in v.get_connections():
            line(v.id[0],v.id[1], road.id[0],road.id[1])
    
    #Crear vertices
    fill(255,100,100) 
    strokeWeight(1)
    for v in g:
        ellipse(v.id[0],v.id[1],5,5)
        
    #Mover carro
    fill(100,100,255)
    pos = (car.x, car.y)
    if (car.destination != pos):
        car = moveVehicle(car)
    else:
        car = Vehicle(580,222,-3,0,(70,222))
    
        
        
        
