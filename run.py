import battlecode as bc
import random
import sys
import math
import traceback
import time


gc = bc.GameController()
directions = list(bc.Direction)

# It's a good idea to try to keep your bots deterministic, to make debugging easier.
# determinism isn't required, but it means that the same things will happen in every thing you run,
# aside from turns taking slightly different amounts of time due to noise.
# random.seed(6137)

gc.queue_research(bc.UnitType.Rocket)
gc.queue_research(bc.UnitType.Rocket)

my_team = gc.team()
replicate_prob = 1/3
mars_map = gc.starting_map(bc.Planet.Mars)
mars_height = mars_map.height
mars_width = mars_map.width


def get_random_mars_position():
    row = random.randint(0, mars_height)
    column = random.randint(0, mars_width)
    return bc.MapLocation(bc.Planet.Mars, row, column)


while True:
    # We only support Python 3, which means brackets around print()
    print('pyround:', gc.round(), 'time left:', gc.get_time_left_ms(), 'ms')

    units = gc.my_units()
    try:
        for unit in units:
            location = unit.location
            if not location.is_on_map():
                continue
            type = unit.unit_type
            d = random.choice(directions)
            if type == bc.UnitType.Worker:
                if gc.karbonite() > bc.UnitType.Rocket.blueprint_cost() and gc.can_blueprint(unit.id, bc.UnitType.Rocket, d):
                    gc.blueprint(unit.id, bc.UnitType.Rocket, d)
                d2 = random.choice(directions)
                if gc.can_replicate(unit.id, d2) and random.random() < replicate_prob:
                    gc.replicate(unit.id, d2)
                d3 = random.choice(directions)
                if gc.can_harvest(unit.id, d3):
                    gc.harvest(unit.id, d3)
                nearby = gc.sense_nearby_units(location.map_location(), 2)
                for other in nearby:
                    if gc.can_build(unit.id, other.id):
                        gc.build(unit.id, other.id)
                #d4 = random.choice(directions)
                #gc.move_robot(unit.id, d4)
            elif type == bc.UnitType.Rocket:
                if not unit.rocket_is_used() and unit.structure_is_built():
                    nearby_units = gc.sense_nearby_units(location.map_location(), 1)
                    if len(nearby_units) > 0:
                        gc.load(unit.id, nearby_units[0].id)
                    destination = get_random_mars_position()
                    gc.launch_rocket(unit.id, destination)
    except Exception as e:
        print(e)

    # send the actions we've performed, and wait for our next turn.
    gc.next_turn()

    # these lines are not strictly necessary, but it helps make the logs make more sense.
    # it forces everything we've written this turn to be written to the manager.
    sys.stdout.flush()
    sys.stderr.flush()