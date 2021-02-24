# -*- coding: UTF-8 -*-

import sys
from argparse import ArgumentTypeError

import numpy

import worldengine.generation as geo
from worldengine.draw import draw_biome_on_file, draw_ocean_on_file, \
    draw_precipitation_on_file, draw_grayscale_heightmap_on_file, draw_simple_elevation_on_file, \
    draw_temperature_levels_on_file, draw_riversmap_on_file, draw_scatter_plot_on_file, \
    draw_satellite_on_file, draw_icecaps_on_file
from worldengine.imex import export
from worldengine.model.world import World, Size, GenerationParameters
from worldengine.plates import world_gen, generate_plates_simulation
from worldengine.step import Step
from worldengine.version import __version__

# import global logger
import worldengine.logger as logger
# importing custom argparser
from args_parser import Parser

VERSION = __version__

STEPS = 'plates|precipitations|full'


def generate_world(world_name, width, height, seed, num_plates, output_dir,
                   step, ocean_level, temp_ranges, moist_ranges, axial_tilt,
                   gamma_curve=1.25, curve_offset=.2, fade_borders=True, black_and_white=False):
    w = world_gen(world_name, width, height, axial_tilt, seed, temp_ranges, moist_ranges, num_plates, ocean_level,
                  step, gamma_curve=gamma_curve, curve_offset=curve_offset,
                  fade_borders=fade_borders)

    # Save data
    filename = "%s/%s.world" % (output_dir, world_name)
    with open(filename, "wb") as f:
        f.write(w.protobuf_serialize())
    logger.logger.info('World data saved in %s' % filename)
    sys.stdout.flush()

    # Generate images
    filename = '%s/%s_ocean.png' % (output_dir, world_name)
    draw_ocean_on_file(w.layers['ocean'].data, filename)

    if step.include_precipitations:
        filename = '%s/%s_precipitation.png' % (output_dir, world_name)
        draw_precipitation_on_file(w, filename, black_and_white)

        filename = '%s/%s_temperature.png' % (output_dir, world_name)
        draw_temperature_levels_on_file(w, filename, black_and_white)

    if step.include_biome:
        filename = '%s/%s_biome.png' % (output_dir, world_name)
        draw_biome_on_file(w, filename)

    filename = '%s/%s_elevation.png' % (output_dir, world_name)
    sea_level = w.sea_level()
    draw_simple_elevation_on_file(w, filename, sea_level=sea_level)
    return w


def generate_grayscale_heightmap(world, filename):
    draw_grayscale_heightmap_on_file(world, filename)


def generate_rivers_map(world, filename):
    draw_riversmap_on_file(world, filename)


def draw_scatter_plot(world, filename):
    draw_scatter_plot_on_file(world, filename)


def draw_satellite_map(world, filename):
    draw_satellite_on_file(world, filename)


def draw_icecaps_map(world, filename):
    draw_icecaps_on_file(world, filename)


def check_step(step_name):
    step = Step.get_by_name(step_name)
    if step is None:
        logger.logger.error('Unknown step name, using default \'full\'')
        return Step.get_by_name('full')
    else:
        return step


def main():
    # initializing logger
    logger.init()

    # parse arguments
    parser = Parser().parser
    args = parser.parse_args()

    # logging cli arguments on debug
    logger.logger.debug('cli args: ' + str(vars(args)))

    # applying seed for numpy pseudo random seed
    numpy.random.seed(args.seed)

    # defining world name
    if not args.world_name:
        args.world_name = 'seed_%i' % args.seed

    step = check_step(args.step)

    logger.logger.debug('generation starting (it could take a few minutes) ...')

    world = generate_world(args.world_name, args.width, args.height,
                           args.seed, args.number_of_plates, args.output_dir,
                           step, args.ocean_level, args.temp_ranges,
                           args.moist_ranges, args.axial_tilt,
                           gamma_curve=args.gv, curve_offset=args.go,
                           fade_borders=args.fade_borders, black_and_white=args.black_and_white)
    if args.grayscale_heightmap:
        generate_grayscale_heightmap(world,
                                     '%s/%s_grayscale.png' % (args.output_dir, world_name))
    if args.rivers_map:
        generate_rivers_map(world,
                            '%s/%s_rivers.png' % (args.output_dir, world_name))
    if args.scatter_plot:
        draw_scatter_plot(world,
                          '%s/%s_scatter.png' % (args.output_dir, world_name))
    if args.satelite_map:
        draw_satellite_map(world,
                           '%s/%s_satellite.png' % (args.output_dir, world_name))
    if args.icecaps_map:
        draw_icecaps_map(world,
                         '%s/%s_icecaps.png' % (args.output_dir, world_name))

    logger.logger.debug('... generation done')

# -------------------------------
if __name__ == "__main__":
    main()
