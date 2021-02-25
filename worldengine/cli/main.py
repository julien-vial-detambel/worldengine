# -*- coding: UTF-8 -*-

from argparse import ArgumentTypeError

import numpy

import worldengine.generation as geo
from worldengine.draw import draw_biome_on_file, draw_ocean_on_file, \
    draw_precipitation_on_file, draw_grayscale_heightmap_on_file, draw_simple_elevation_on_file, \
    draw_temperature_levels_on_file, draw_riversmap_on_file, draw_scatter_plot_on_file, \
    draw_satellite_on_file, draw_icecaps_on_file
from worldengine.imex import export
from worldengine.model.world import World
from worldengine.simulations.plates import world_gen, generate_plates_simulation
from worldengine.version import __version__

# import global logger
import worldengine.logger as logger
# importing custom argparser
from args_parser import Parser

VERSION = __version__

def generate_world(name, width, height, seed, n_plates, output_dir,
                   ocean_level, temperature_ranges, moisture_ranges, axial_tilt,
                   gamma_value=1.25, gamma_offset=.2, fade_borders=True, black_and_white=False):
    w = world_gen(name, width, height, axial_tilt, seed, temperature_ranges, moisture_ranges, n_plates, ocean_level,
                  gamma_value=gamma_value, gamma_offset=gamma_offset,
                  fade_borders=fade_borders)

    # TODO: serialization if temporarly disabled must be reenabled
    # Save data
    #filename = "%s/%s.world" % (output_dir, name)
    #with open(filename, "wb") as f:
    #    f.write(w.protobuf_serialize())
    #logger.logger.info('World data saved in %s' % filename)

    # Generate images
    filename = '%s/%s_ocean.png' % (output_dir, name)
    draw_ocean_on_file(w.layers['ocean'].data, filename)

    filename = '%s/%s_precipitation.png' % (output_dir, name)
    draw_precipitation_on_file(w, filename, black_and_white)

    filename = '%s/%s_temperature.png' % (output_dir, name)
    draw_temperature_levels_on_file(w, filename, black_and_white)

    filename = '%s/%s_biome.png' % (output_dir, name)
    draw_biome_on_file(w, filename)

    filename = '%s/%s_elevation.png' % (output_dir, name)
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


def main():
    # initializing logger
    logger.init()

    # parse arguments
    parser = Parser().parser
    args = parser.parse_args()

    # logging cli arguments on debug
    logger.logger.debug('cli args: {}'.format(vars(args)))

    # applying seed for numpy pseudo random seed
    numpy.random.seed(args.seed)

    # defining world name
    if not args.name:
        args.name = 'seed_%i' % args.seed

    logger.logger.debug('generation starting (it could take a few minutes) ...')

    #world = World(args.name, args.width, args.height, args.seed, args.axial_tilt, args.n_plates, args.ocean_level, args.temp, args.moisture_ranges, args.gamma_value, args.gamma_offset)

    world = generate_world(args.name, args.width, args.height,
                           args.seed, args.n_plates, args.output_dir,
                           args.ocean_level, args.temperature_ranges,
                           args.moisture_ranges, args.axial_tilt,
                           gamma_value=args.gamma_value, gamma_offset=args.gamma_offset,
                           fade_borders=args.fade_borders, black_and_white=args.black_and_white)
    if args.grayscale_heightmap:
        generate_grayscale_heightmap(world,
                                     '%s/%s_grayscale.png' % (args.output_dir, args.name))
    generate_rivers_map(world,
                        '%s/%s_rivers.png' % (args.output_dir, args.name))

    if args.scatter_plot:
        draw_scatter_plot(world,
                          '%s/%s_scatter.png' % (args.output_dir, args.name))
    if args.satelite_map:
        draw_satellite_map(world,
                           '%s/%s_satellite.png' % (args.output_dir, args.name))
    if args.icecaps_map:
        draw_icecaps_map(world,
                         '%s/%s_icecaps.png' % (args.output_dir, args.name))

    logger.logger.debug('... generation done')

# -------------------------------
if __name__ == "__main__":
    main()
