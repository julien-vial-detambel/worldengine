# -*- coding: UTF-8 -*-

import sys
import os

import numpy

import worldengine.generation as geo
from worldengine.common import set_verbose, print_verbose, get_verbose
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
                   step, ocean_level, temps, humids, axial_tilt,
                   gamma_curve=1.25, curve_offset=.2, fade_borders=True,
                   verbose=True, black_and_white=False):
    w = world_gen(world_name, width, height, axial_tilt, seed, temps, humids, num_plates, ocean_level,
                  step, gamma_curve=gamma_curve, curve_offset=curve_offset,
                  fade_borders=fade_borders, verbose=verbose)

    print('')  # empty line
    print('Producing ouput:')
    sys.stdout.flush()

    # Save data
    filename = "%s/%s.world" % (output_dir, world_name)
    with open(filename, "wb") as f:
        f.write(w.protobuf_serialize())
    print("* world data saved in '%s'" % filename)
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
        print("ERROR: unknown step name, using default 'full'")
        return Step.get_by_name("full")
    else:
        return step


def main():
    # initializing logger
    logger.init()

    # parse arguments
    parser = Parser().parser
    args = parser.parse_args()

    operation = "world"

    # there is a hard limit somewhere so seeds outside the uint16 range are considered unsafe
    maxseed = numpy.iinfo(
        numpy.uint16).max
    if args.seed is not None:
        seed = int(args.seed)
        assert 0 <= seed <= maxseed, \
            "Seed has to be in the range between 0 and %s, borders included." % maxseed
    else:
        seed = numpy.random.randint(0,
                                    maxseed)  # first-time RNG initialization is done automatically
    numpy.random.seed(seed)

    if args.world_name:
        world_name = args.world_name
    else:
        world_name = "seed_%i" % seed

    step = check_step(args.step)

    if args.temps and len(args.temps.split('/')) is not 6:
        usage(error="temps must have exactly 6 values")

    temps = [.874, .765, .594, .439, .366, .124]
    if args.temps:
        temps = args.temps.split('/')
        for x in range(0, len(temps)):
            temps[x] = 1 - float(temps[x])

    if args.humids and len(args.humids.split('/')) is not 7:
        usage(error="humidity must have exactly 7 values")

    humids = [.941, .778, .507, .236, 0.073, .014, .002]
    if args.humids:
        humids = args.humids.split('/')
        for x in range(0, len(humids)):
            humids[x] = 1 - float(humids[x])

    print('Worldengine - a world generator (v. %s)' % VERSION)
    print('-----------------------')
    print(' seed                 : %i' % seed)
    print(' name                 : %s' % world_name)
    print(' width                : %i' % args.width)
    print(' height               : %i' % args.height)
    print(' number of plates     : %i' % args.number_of_plates)
    print(' black and white maps : %s' % args.black_and_white)
    print(' step                 : %s' % step.name)
    print(' greyscale heightmap  : %s' % args.grayscale_heightmap)
    print(' icecaps heightmap    : %s' % args.icecaps_map)
    print(' rivers map           : %s' % args.rivers_map)
    print(' scatter plot         : %s' % args.scatter_plot)
    print(' satellite map        : %s' % args.satelite_map)
    print(' fade borders         : %s' % args.fade_borders)
    if args.temps:
        print(' temperature ranges   : %s' % args.temps)
    if args.humids:
        print(' humidity ranges      : %s' % args.humids)
    print(' gamma value          : %s' % args.gv)
    print(' gamma offset         : %s' % args.go)
    print(' axial tile           : %s' % args.axial_tilt)
    # Warning messages
    warnings = []
    if temps != sorted(temps, reverse=True):
        warnings.append("WARNING: Temperature array not in ascending order")
    if numpy.amin(temps) < 0:
        warnings.append("WARNING: Maximum value in temperature array greater than 1")
    if numpy.amax(temps) > 1:
        warnings.append("WARNING: Minimum value in temperature array less than 0")
    if humids != sorted(humids, reverse=True):
        warnings.append("WARNING: Humidity array not in ascending order")
    if numpy.amin(humids) < 0:
        warnings.append("WARNING: Maximum value in humidity array greater than 1")
    if numpy.amax(humids) > 1:
        warnings.append("WARNING: Minimum value in temperature array less than 0")

    if warnings:
        print("\n")
        for x in range(len(warnings)):
            print(warnings[x])

    set_verbose(args.verbose)

    print('starting (it could take a few minutes) ...')

    world = generate_world(world_name, args.width, args.height,
                           seed, args.number_of_plates, args.output_dir,
                           step, args.ocean_level, temps, humids, args.axial_tilt,
                           gamma_curve=args.gv, curve_offset=args.go,
                           fade_borders=args.fade_borders,
                           verbose=args.verbose, black_and_white=args.black_and_white)
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

    print('...done')


def usage(error=None):
    print(
        ' -------------------------------------------------------------------')
    print(' Federico Tomassetti and Bret Curtis, 2011-2017')
    print(' Worldengine - a world generator (v. %s)' % VERSION)
    print(' ')
    print(' worldengine <world_name> [operation] [options]')
    print(' possible operations: %s' % OPERATIONS)
    print(' use -h to see options')
    print(
        ' -------------------------------------------------------------------')
    if error:
        print("ERROR: %s" % error)
    sys.exit(' ')


# -------------------------------
if __name__ == "__main__":
    main()
