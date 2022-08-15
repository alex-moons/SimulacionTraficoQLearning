from trafficSimulator import *

#https://towardsdatascience.com/simulating-traffic-flow-in-python-ee1eab4dd20f

# Create simulation
sim = Simulation()

# Add multiple roads
sim.create_roads([
    ((30, 100), (120, 10)),
    ((25, 100), (122, 3)),
    ((120, 10), (280, 160)),
    ((285, 160), (120, 5)),
    ((280, 160), (120, 300)),
    ((285, 160), (120, 305)),
    ((120, 300), (30, 100)),
    ((118, 305), (26, 100))
])

"""
    ((300, 98), (0, 98)),
    ((0, 102), (300, 102)),
    ((180, 60), (0, 60)),
    ((220, 55), (180, 60)),
    ((300, 30), (220, 55)),
    ((180, 60), (160, 98)),
    ((158, 130), (300, 130)),
    ((0, 178), (300, 178)),
    ((300, 182), (0, 182)),
    ((160, 102), (155, 180))"""  

sim.create_gen({
    'vehicle_rate': 60,
    'vehicles': [
        [1, {"path": [0,2,4,6]}],
        [1, {"path": [5]}],
        [1, {"path": [1]}],
        [1, {"path": [3,7,1]}]
    ]
})

# Start simulation
win = Window(sim)
win.offset = (-150, -110)
win.run(steps_per_update=5)