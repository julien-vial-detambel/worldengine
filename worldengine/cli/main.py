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

OPERATIONS = 'world|plates|info|export'
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


def generate_plates(seed, world_name, output_dir, width, height, axial_tilt, num_plates=10):
    """
    Eventually this method should be invoked when generation is called at
    asked to stop at step "plates", it should not be a different operation
    :param seed:
    :param world_name:
    :param output_dir:
    :param width:
    :param height:
    :param axial_tilt:
    :param num_plates:
    :return:
    """
    elevation, plates = generate_plates_simulation(seed, width, height, axial_tilt, num_plates=num_plates)

    world = World(world_name, Size(width, height), seed, axial_tilt,
                  GenerationParameters(num_plates, -1.0, "plates"))
    world.elevation = (numpy.array(elevation).reshape(height, width), None)
    world.plates = numpy.array(plates, dtype=numpy.uint16).reshape(height, width)

    # Generate images
    filename = '%s/plates_%s.png' % (output_dir, world_name)
    draw_simple_elevation_on_file(world, filename, None)
    print("+ plates image generated in '%s'" % filename)
    geo.center_land(world)
    filename = '%s/centered_plates_%s.png' % (output_dir, world_name)
    draw_simple_elevation_on_file(world, filename, None)
    print("+ centered plates image generated in '%s'" % filename)


def check_step(step_name):
    step = Step.get_by_name(step_name)
    if step is None:
        print("ERROR: unknown step name, using default 'full'")
        return Step.get_by_name("full")
    else:
        return step


def __get_last_byte__(filename):
    with open(filename, 'rb') as input_file:
        data = tmp_data = input_file.read(1024 * 1024)
        while tmp_data:
            tmp_data = input_file.read(1024 * 1024)
            if tmp_data:
                data = tmp_datar
    return data[len(data) - 1]


def __varint_to_value__(varint):
    # See https://developers.google.com/protocol-buffers/docs/encoding for details

    # to convert it to value we must start from the first byte
    # and add to it the second last multiplied by 128, the one after
    # multiplied by 128 ** 2 and so on
    if len(varint) == 1:
        return varint[0]
    else:
        return varint[0] + 128 * __varint_to_value__(varint[1:])


def __get_tag__(filename):
    with open(filename, 'rb') as ifile:
        # drop first byte, it should tell us the protobuf version and it
        # should be normally equal to 8
        data = ifile.read(1)
        if not data:
            return None
        done = False
        tag_bytes = []
        # We read bytes until we find a bit with the MSB not set
        while data and not done:
            data = ifile.read(1)
            if not data:
                return None
            value = ord(data)
            tag_bytes.append(value % 128)
            if value < 128:
                done = True
        # to convert it to value we must start from the last byte
        # and add to it the second last multiplied by 128, the one before
        # multiplied by 128 ** 2 and so on
        return __varint_to_value__(tag_bytes)


def __seems_protobuf_worldfile__(world_filename):
    worldengine_tag = __get_tag__(world_filename)
    return worldengine_tag == World.worldengine_tag()


def load_world(world_filename):
    pb = __seems_protobuf_worldfile__(world_filename)
    if pb:
        try:
            return World.open_protobuf(world_filename)
        except Exception:
            raise Exception("Unable to load the worldfile as protobuf file")
    else:
        raise Exception("The given worldfile does not seem to be a protobuf file")


def print_world_info(world):
    print(" name               : %s" % world.name)
    print(" width              : %i" % world.width)
    print(" height             : %i" % world.height)
    print(" seed               : %i" % world.seed)
    print(" no plates          : %i" % world.n_plates)
    print(" ocean level        : %f" % world.ocean_level)
    print(" step               : %s" % world.step.name)

    print(" has biome          : %s" % world.has_biome())
    print(" has humidity       : %s" % world.has_humidity())
    print(" has irrigation     : %s" % world.has_irrigation())
    print(" has permeability   : %s" % world.has_permeability())
    print(" has watermap       : %s" % world.has_watermap())
    print(" has precipitations : %s" % world.has_precipitations())
    print(" has temperature    : %s" % world.has_temperature())


def main():
    # initializing logger
    logger.init()

    # parse arguments
    parser = Parser().parser
    args = parser.parse_args()

    if os.path.exists(args.output_dir):
        if not os.path.isdir(args.output_dir):
            raise Exception("Output dir exists but it is not a dir")
    else:
        print('Directory does not exist, we are creating it')
        os.makedirs(args.output_dir)

    # it needs to be increased to be able to generate very large maps
    # the limit is hit when drawing ancient maps
    sys.setrecursionlimit(args.recursion_limit)

    operation = "world"
    if args.OPERATOR is None:
        pass
    elif args.OPERATOR is not None and args.OPERATOR.lower() not in OPERATIONS:
        parser.print_help()
        usage("Only 1 operation allowed [" + OPERATIONS + "]")
    else:
        operation = args.OPERATOR.lower()

    if args.OPERATOR == 'info' or args.OPERATOR == 'export':
        if args.FILE is None:
            parser.print_help()
            usage("For operation info only the filename should be specified")
        if not os.path.exists(args.FILE):
            usage("The specified world file does not exist")

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

    generation_operation = (operation == 'world') or (operation == 'plates')

    if args.grayscale_heightmap and not generation_operation:
        usage(
            error="Grayscale heightmap can be produced only during world " +
                  "generation")

    if args.rivers_map and not generation_operation:
        usage(error="Rivers map can be produced only during world generation")

    if args.temps and not generation_operation:
        usage(error="temps can be assigned only during world generation")

    if args.temps and len(args.temps.split('/')) is not 6:
        usage(error="temps must have exactly 6 values")

    if args.go >= 1 or args.go < 0:
        usage(error="Gamma offset must be greater than or equal to 0 and less than 1")

    if args.gv <= 0:
        usage(error="Gamma value must be greater than 0")

    temps = [.874, .765, .594, .439, .366, .124]
    if args.temps:
        temps = args.temps.split('/')
        for x in range(0, len(temps)):
            temps[x] = 1 - float(temps[x])

    if args.humids and not generation_operation:
        usage(error="humidity can be assigned only during world generation")

    if args.humids and len(args.humids.split('/')) is not 7:
        usage(error="humidity must have exactly 7 values")

    humids = [.941, .778, .507, .236, 0.073, .014, .002]
    if args.humids:
        humids = args.humids.split('/')
        for x in range(0, len(humids)):
            humids[x] = 1 - float(humids[x])
    if args.scatter_plot and not generation_operation:
        usage(error="Scatter plot can be produced only during world generation")

    print('Worldengine - a world generator (v. %s)' % VERSION)
    print('-----------------------')
    if generation_operation:
        print(' operation            : %s generation' % operation)
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

    if operation == 'world':
        print('')  # empty line
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

    elif operation == 'plates':
        print('')  # empty line
        print('starting (it could take a few minutes) ...')

        generate_plates(seed, world_name, args.output_dir, args.width,
                        args.height, args.axial_tilt, num_plates=args.number_of_plates)

    elif operation == 'info':
        world = load_world(args.FILE)
        print_world_info(world)
    elif operation == 'export':
        world = load_world(args.FILE)
        print_world_info(world)
        export(world, args.export_format, args.export_datatype, args.export_dimensions,
               args.export_normalize, args.export_subset,
               path='%s/%s_elevation' % (args.output_dir, world.name))
    else:
        raise Exception(
            'Unknown operation: valid operations are %s' % OPERATIONS)

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
