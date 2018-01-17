import battlecode as bc
import random
import sys
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

while True:
    # We only support Python 3, which means brackets around print()
    print('pyround:', gc.round(), 'time left:', gc.get_time_left_ms(), 'ms')

    units = gc.my_units()
    for unit in units:
        type = unit.unit_type
        d = random.choice(directions)
        if type == bc.UnitType.Worker:
            if gc.karbonite() > bc.UnitType.Rocket.blueprint_cost() and gc.can_blueprint(unit.id, bc.UnitType.Rocket, d):
                gc.blueprint(unit.id, bc.UnitType.Rocket, d)
            d2 = random.choice(directions)
            if gc.can_replicate(unit.id, d2):
                gc.replicate(unit.id, d2)
            d3 = random.choice(directions)
            if gc.can_harvest(unit.id, d3):
                gc.harvest(unit.id, d3)
            location = unit.location
            if location.is_on_map():
                nearby = gc.sense_nearby_units(location.map_location(), 2)
                for other in nearby:
                    if gc.can_build(unit.id, other.id):
                        gc.build(unit.id, other.id)


    # send the actions we've performed, and wait for our next turn.
    gc.next_turn()

    # these lines are not strictly necessary, but it helps make the logs make more sense.
    # it forces everything we've written this turn to be written to the manager.
    sys.stdout.flush()
    sys.stderr.flush()
