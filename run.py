import battlecode as bc
import random
import sys
import traceback
import time

import os
print(os.getcwd())

print("pystarting")

# A GameController is the main type that you talk to the game with.
# Its constructor will connect to a running game.
gc = bc.GameController()
directions = list(bc.Direction)

print("pystarted")

# It's a good idea to try to keep your bots deterministic, to make debugging easier.
# determinism isn't required, but it means that the same things will happen in every thing you run,
# aside from turns taking slightly different amounts of time due to noise.
random.seed(6137)
y = 50

# let's start off with some research!
# we can queue as much as we want.
gc.queue_research(bc.UnitType.Rocket)
gc.queue_research(bc.UnitType.Rocket)
gc.queue_research(bc.UnitType.Worker)
gc.queue_research(bc.UnitType.Knight)

my_team = gc.team()
replicate_prob = 1/3
mars_map = gc.starting_map(bc.Planet.Mars)
mars_height = mars_map.height
mars_width = mars_map.width


def get_random_mars_position():
    row = random.randint(0, mars_height)
    column = random.randint(0, mars_width)
    return bc.MapLocation(bc.Planet.Mars, row, column)


def count_workers(planet):
    total = 0
    for unit in gc.units():
        if unit.unit_type == bc.UnitType.Worker and unit.location.is_on_planet(planet):
            total += 1
    return total


while True:
    # We only support Python 3, which means brackets around print()
    print('pyround:', gc.round(), 'time left:', gc.get_time_left_ms(), 'ms')

    # frequent try/catches are a good idea
    try:
        # walk through our units:
        worker_count = count_workers(gc.planet())
        for unit in gc.my_units():
            d = random.choice(directions)
            if unit.unit_type == bc.UnitType.Worker:
                if gc.karbonite() > bc.UnitType.Rocket.blueprint_cost() and gc.can_blueprint(unit.id,bc.UnitType.Rocket, d):
                    print("there is a thing!")
                    gc.blueprint(unit.id, bc.UnitType.Rocket, d)
            elif unit.unit_type == bc.UnitType.Factory:
                if gc.can_produce_robot(unit.id, bc.UnitType.Knight) or gc.can_produce_robot(unit.id,
                                                                                             bc.UnitType.Ranger):
                    x = random.uniform(0, 10)
                    if x >= 7:
                        gc.produce_robot(unit.id, bc.UnitType.Ranger)
                        print('produced a Ranger!')
                    else:
                        gc.produce_robot(unit.id, bc.UnitType.Knight)
                        print('produced a Knight!')
            else:
                # or, try to build a factory:
                if gc.karbonite() > bc.UnitType.Factory.blueprint_cost() and gc.can_blueprint(unit.id, bc.UnitType.Factory, d):
                    gc.blueprint(unit.id, bc.UnitType.Factory, d)
                # and if that fails, try to move
                elif gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
                    gc.move_robot(unit.id, d)
            location = unit.location
            if not location.is_on_map():
                continue
            type = unit.unit_type

            if unit.unit_type == bc.UnitType.Worker:
                d2 = random.choice(directions)
                if gc.can_replicate(unit.id, d2) and worker_count < 20:
                    gc.replicate(unit.id, d2)
                d3 = random.choice(directions)
                if gc.can_harvest(unit.id, d3):
                    gc.harvest(unit.id, d3)
                nearby = gc.sense_nearby_units(location.map_location(), 2)
                for other in nearby:
                    if gc.can_build(unit.id, other.id):
                        gc.build(unit.id, other.id)
                # d4 = random.choice(directions)
                # gc.move_robot(unit.id, d4)
            elif type == bc.UnitType.Rocket:
                if not unit.rocket_is_used() and unit.structure_is_built():
                    nearby_units = gc.sense_nearby_units(location.map_location(), 1)
                    if len(nearby_units) > 0:
                        gc.load(unit.id, nearby_units[0].id)
                    destination = get_random_mars_position()
                    gc.launch_rocket(unit.id, destination)

            # if y >= 0 and unit.unit_type == bc.UnitType.Worker:
            #     d = random.choice(directions)
            #     if gc.can_replicate(unit.id, d):
            #         gc.replicate(unit.id, d)
            #         y = y - 1
            #         continue

            # first, factory logic
            elif unit.unit_type == bc.UnitType.Factory:
                garrison = unit.structure_garrison()
                if len(garrison) > 0:
                    d = random.choice(directions)
                    if gc.can_unload(unit.id, d):
                        print('unloaded a Knight!')
                        gc.unload(unit.id, d)
            else:
                # first, let's look for nearby blueprints to work on
                location = unit.location
                if location.is_on_map():
                    nearby = gc.sense_nearby_units(location.map_location(), 2)
                    for other in nearby:
                        if unit.unit_type == bc.UnitType.Worker and gc.can_build(unit.id, other.id):
                            gc.build(unit.id, other.id)
                            print('built a factory!')
                            # move onto the next unit
                        # if gc.is_move_ready(unit.id) and gc.can_move(unit.id, directions.South) and unit.unit_type == bc.UnitType.Ranger:
                        #     gc.move_robot(unit.id, directions.South)
                        #     continue
                        elif other.team != my_team and gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
                            print('attacked a thing!')
                            gc.attack(unit.id, other.id)
    except Exception as e:
        print('Error:', e)
        # use this to show where the error was
        traceback.print_exc()

    # send the actions we've performed, and wait for our next turn.
    gc.next_turn()

    # these lines are not strictly necessary, but it helps make the logs make more sense.
    # it forces everything we've written this turn to be written to the manager.
    sys.stdout.flush()
    sys.stderr.flush()
