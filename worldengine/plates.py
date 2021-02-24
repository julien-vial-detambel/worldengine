# Every reference to platec has to be kept separated because it is a C
# extension which is not available when using this project from jython

import platec
import time
import numpy

from worldengine.generation import Step, add_noise_to_elevation, center_land, \
    generate_world, initialize_ocean_and_thresholds, place_oceans_at_map_borders
from worldengine.model.world import World, Size, GenerationParameters

# import global logger
import worldengine.logger as logger

def generate_plates_simulation(seed, width, height, axial_tilt, sea_level=0.65,
                               erosion_period=60, folding_ratio=0.02,
                               aggr_overlap_abs=1000000, aggr_overlap_rel=0.33,
                               cycle_count=2, num_plates=10):

    start_time = time.time()
    p = platec.create(seed, width, height, sea_level, erosion_period,
                      folding_ratio, aggr_overlap_abs, aggr_overlap_rel,
                      cycle_count, num_plates)
    # Note: To rescale the worlds heightmap to roughly Earths scale, multiply by 2000.

    while platec.is_finished(p) == 0:
        # TODO: add a if verbose: message here?
        platec.step(p)
    hm = platec.get_heightmap(p)
    pm = platec.get_platesmap(p)
    elapsed_time = time.time() - start_time
    logger.logger.debug('...plates.generate_plates_simulation() complete. ' +
              'Elapsed time ' + str(elapsed_time) + ' seconds.')
    return hm, pm


def _plates_simulation(name, width, height, axial_tilt, seed, temps=
                       [.874, .765, .594, .439, .366, .124], humids=
                       [.941, .778, .507, .236, 0.073, .014, .002], gamma_curve=1.25,
                       curve_offset=.2, num_plates=10, ocean_level=1.0,
                       step=Step.full()):
    e_as_array, p_as_array = generate_plates_simulation(seed, width, height, axial_tilt,
                                                        num_plates=num_plates)

    world = World(name, Size(width, height), seed, axial_tilt,
                  GenerationParameters(num_plates, ocean_level, step),
                  temps, humids, gamma_curve, curve_offset)
    world.elevation = (numpy.array(e_as_array).reshape(height, width), None)
    world.plates = numpy.array(p_as_array, dtype=numpy.uint16).reshape(height, width)
    return world


def world_gen(name, width, height, axial_tilt, seed, temps=[.874, .765, .594, .439, .366, .124],
              humids=[.941, .778, .507, .236, 0.073, .014, .002], num_plates=10,
              ocean_level=1.0, step=Step.full(), gamma_curve=1.25, curve_offset=.2,
              fade_borders=True):
    start_time = time.time()
    world = _plates_simulation(name, width, height, axial_tilt, seed, temps, humids, gamma_curve,
                               curve_offset, num_plates, ocean_level, step)

    center_land(world)
    elapsed_time = time.time() - start_time
    logger.logger.debug('...plates.world_gen: set_elevation, set_plates, ' +
                       'center_land complete. Elapsed time ' +
                       str(elapsed_time) + ' seconds.')

    start_time = time.time()
    add_noise_to_elevation(world, numpy.random.randint(0, 4096))  # uses the global RNG; this is the very first call to said RNG - should that change, this needs to be taken care of
    elapsed_time = time.time() - start_time
    logger.logger.debug('...plates.world_gen: elevation noise added. Elapsed ' +
                       'time ' + str(elapsed_time) + ' seconds.')

    start_time = time.time()
    if fade_borders:
        place_oceans_at_map_borders(world)
    initialize_ocean_and_thresholds(world)
    elapsed_time = time.time() - start_time
    logger.logger.debug('...plates.world_gen: oceans initialized. Elapsed ' +
                       'time ' + str(elapsed_time) + ' seconds.')

    return generate_world(world, step)
