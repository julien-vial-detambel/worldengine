# -*- coding: UTF-8 -*-

import os
import argparse

import numpy

import worldengine.logger as logger

STEPS = 'plates|precipitations|full'

class Parser():

    # used for validation of directory given to parser
    def directory(self, path):
        if not os.path.exists(path) or (os.path.exists(path)
            and not os.path.isdir(path)):
            raise argparse.ArgumentTypeError('Not a valid directory')
        return path

    # used for validation of axial tilt
    def axial_tilt(self, ax):
        ax = float(ax)
        if ax < -90.0 or ax > 90.0:
            raise argparse.ArgumentTypeError('Axial tilt should be a float in ' +
                                             'interval [-90, 90]')
        return ax

    # used for validation of plates number
    def plates_number(self, q):
        q = int(q)
        if q < 1 or q > 100:
            raise argparse.ArgumentTypeError('Number of plates should be an int ' +
                                             'interval [0, 100]')
        return q

    # used for validation of gamma offset
    def gamma_offset(self, go):
        go = float(go)
        if go >= 1 or go < 0:
            raise argparse.ArgumentTypeError('Gamma offset should be a float in ' +
                                             'interval [0, 1]')
        return go

    # used for validation of gamma value
    def gamma_value(self, gv):
        gv = float(gv)
        if gv <= 0:
            raise argparse.ArgumentTypeError('Gamma value should be a positive ' +
                                             'float')
        return gv

    # used for validation of temperature ranges
    def temperature_ranges(self, temp_ranges):
        temp_ranges = str(temp_ranges)
        if len(temp_ranges.split('/')) is not 6:
            raise argparse.ArgumentTypeError('Temperature ranges must have ' +
                                             'exactly 6 floating point values')
        temp_ranges = temp_ranges.split('/')
        for x in range(0, len(temp_ranges)):
            temp_ranges[x] = 1 - float(temp_ranges[x])

        if temp_ranges != sorted(temp_ranges, reverse = True):
            logger.logger.warning('Temperature array not in ascending order')
        if numpy.amin(temp_ranges) < 0:
            logger.logger.warning('Maximum value in temperature array greater than 1')
        if numpy.amax(temp_ranges) > 1:
            logger.logger.warning('Minimum value in temperature array less than 0')

        return temp_ranges

    # used for validation of moisture ranges
    def moisture_ranges(self, moist_ranges):
        moist_ranges = str(moist_ranges)
        if len(moist_ranges.split('/')) is not 7:
            raise argparse.ArgumentTypeError('Moisture ranges must have ' +
                                             'exactly 7 floating point values')
        moist_ranges = moist_ranges.split('/')
        for x in range(0, len(moist_ranges)):
            moist_ranges[x] = 1 - float(moist_ranges[x])

        if moist_ranges != sorted(moist_ranges, reverse = True):
            logger.logger.warning('Humidity array not in ascending order')
        if numpy.amin(moist_ranges) < 0:
            logger.logger.warning('Maximum value in humidity array greater than 1')
        if numpy.amax(moist_ranges) > 1:
            logger.logger.warning('Minimum value in temperature array less than 0')

        return moist_ranges

    # used for seed validation
    def seed(self, seed):
        seed = int(seed)
        if seed < 0 or seed > 65535:
            raise argparse.ArgumentTypeError('Seed should be in interval ' +
                                             '[0, 65535]')
        return seed

    def __init__(self):

        self.parser = argparse.ArgumentParser(
            usage="%(prog)s [options]")

        self.parser.add_argument('FILE', nargs='?')

        # exposing output directory
        self.parser.add_argument('-o', '--output-dir', dest = 'output_dir',
                                 metavar = 'DIR',
                                 help = 'Generate files in DIR ' +
                                 '[default = %(default)s]',
                                 default = '.', type = self.directory)

        # exposing seed
        self.parser.add_argument('-s', '--seed', dest = 'seed',
                                 metavar = '[0, 65535]',
                                 help = 'Specify seed for pseudo-random ' +
                                 'generation.',
                                 default = numpy.random.randint(0, 65535),
                                 type = self.seed)

        # exposing worldname
        # TODO: dangerous uses of seed defined above.
        self.parser.add_argument('-n', '--worldname', dest = 'world_name',
                                 metavar = 'STR',
                                 help = 'Specify world name used for outputs')
                                 #//default = 'seed_%i' % args.seed)

        self.parser.add_argument('-t', '--step', dest='step',
                            help="Use step=[" + STEPS + "] to specify how far " +
                                 "to proceed in the world generation process. " +
                                 "[default='%(default)s']",
                            metavar="STR", default="full")

        self.parser.add_argument('-x', '--width', dest='width', type=int,
                            help="N = width of the world to be generated " +
                                 "[default=%(default)s]",
                            metavar="N",
                            default='512')

        self.parser.add_argument('-y', '--height', dest='height', type=int,
                            help="N = height of the world to be generated " +
                                 "[default=%(default)s]",
                            metavar="N",
                            default='512')

        # exposing the number of plates to generate
        self.parser.add_argument('-q', '--number-of-plates',
                                 dest = 'number_of_plates',
                                 metavar = '[1-100]',
                                 help = 'Number of plates ' +
                                 '[default = %(default)s]',
                                 default = '10', type = self.plates_number)

        self.parser.add_argument('-v', '--verbose', dest='verbose', action="store_true",
                            help="Enable verbose messages", default=False)

        self.parser.add_argument('--version', dest='version', action="store_true",
                            help="Display version information", default=False)

        self.parser.add_argument('--bw', '--black-and-white', dest='black_and_white',
                            action="store_true",
                            help="generate maps in black and white",
                            default=False)

        # -----------------------------------------------------
        generation_args = self.parser.add_argument_group(
            "Generate Options", "These options are only useful in plate and " +
                                "world modes")

        generation_args.add_argument('-r', '--rivers', dest='rivers_map',
                                action="store_true", help="generate rivers map")

        generation_args.add_argument('-gs', '--grayscale-heightmap',
                                dest='grayscale_heightmap', action="store_true",
                                help='produce a grayscale heightmap')

        generation_args.add_argument('--ocean_level', dest='ocean_level', type=float,
                                help='elevation cut off for sea level " +'
                                     '[default = %(default)s]',
                                metavar="N", default=1.0)

        # exposing temperature ranges
        generation_args.add_argument('--temp_ranges', dest = 'temp_ranges',
                                     metavar = '%f/%f/%f/%f/%f/%f',
                                     help = 'Provide alternate ranges for ' +
                                     'temperatures. [default = %(default)s]',
                                     default = '.126/.235/.406/.561/.634/.876',
                                     type = self.temperature_ranges)

        # exposing moisture ranges
        generation_args.add_argument('--moist_ranges', dest = 'moist_ranges',
                                     metavar = '%f/%f/%f/%f/%f/%f/%f',
                                     help = 'Provide alternate ranges for ' +
                                     'moisture. [default = %(default)s]',
                                     default = '.059/.222/.493/.764/.927/.986/.998',
                                     type = self.moisture_ranges)

        # exposing gamma value
        generation_args.add_argument('-gv', '--gamma-value', dest='gv',
                                     metavar = '> 0',
                                     help = 'Gamma value for ' +
                                     'temperature/precipitation gamma ' +
                                     'correction curve. [default = %(default)s]',
                                     default = '1.25',  type = self.gamma_value)

        # exposing gamma offset
        generation_args.add_argument('-go', '--gamma-offset', dest = 'go',
                                     metavar = '[0, 1]',
                                     help = 'Adjustment value [0, 1] for ' +
                                    'temperature/precipitation gamma ' +
                                    'correction curve. [default = %(default)s]',
                                    default = '.2', type = self.gamma_offset)

        generation_args.add_argument('--not-fade-borders', dest='fade_borders', action="store_false",
                                help="Not fade borders",
                                default=True)

        generation_args.add_argument('--scatter', dest='scatter_plot',
                                action="store_true", help="generate scatter plot")

        generation_args.add_argument('--sat', dest='satelite_map',
                                action="store_true", help="generate satellite map")

        generation_args.add_argument('--ice', dest='icecaps_map',
                                action="store_true", help="generate ice caps map")

        # exposing axial tilt
        generation_args.add_argument('-ax', '--axial_tilt', dest = 'axial_tilt',
                                     metavar = '[-90-90]',
                                     help = 'Axial tilt [-90.0, 90] denoting ' +
                                     'the world obliquity. Default is 25.0',
                                     default = 25.0, type = self.axial_tilt)
