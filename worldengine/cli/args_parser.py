# -*- coding: UTF-8 -*-

from argparse import ArgumentParser

OPERATIONS = 'world|plates|info|export'
STEPS = 'plates|precipitations|full'

class Parser(ArgumentParser):
    def __init__(self):
        self.parser = ArgumentParser(
            usage="usage: %(prog)s [options] [" + OPERATIONS + "]")
        self.parser.add_argument('OPERATOR', nargs='?')
        self.parser.add_argument('FILE', nargs='?')

        # exposing output directory
        self.parser.add_argument('-o', '--output-dir', dest = 'output_dir',
            help = 'Generate files in DIR [default = %(default)s]',
            metavar = 'DIR', default = '.')

        self.parser.add_argument(
            '-n', '--worldname', dest='world_name',
            help="set world name to STR. output is stored in a " +
                 "world file with the name format 'STR.world'. If " +
                 "a name is not provided, then seed_N.world, " +
                 "where N=SEED",
            metavar="STR")
        self.parser.add_argument('--hdf5', dest='hdf5',
                            action="store_true",
                            help="Save world file using HDF5 format. " +
                                 "Default = store using protobuf format",
                            default=False)
        self.parser.add_argument('-s', '--seed', dest='seed', type=int,
                            help="Use seed=N to initialize the pseudo-random " +
                                 "generation. If not provided, one will be " +
                                 "selected for you.",
                            metavar="N")
        self.parser.add_argument('-t', '--step', dest='step',
                            help="Use step=[" + STEPS + "] to specify how far " +
                                 "to proceed in the world generation process. " +
                                 "[default='%(default)s']",
                            metavar="STR", default="full")
        # TODO --step appears to be duplicate of OPERATIONS. Especially if
        # ancient_map is added to --step
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
                                 choices = range(1, 101),
                                 metavar = '[1-100]',
                                 help = 'Number of plates ' +
                                 '[default = %(default)s]',
                                 default = '10', type = int)

        self.parser.add_argument('--recursion_limit', dest='recursion_limit', type=int,
                            help="Set the recursion limit [default = %(default)s]",
                            metavar="N", default='2000')
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
        generation_args.add_argument('--temps', dest='temps',
                                help="Provide alternate ranges for temperatures. " +
                                     "If not provided, the default values will be used. \n" +
                                     "[default = .126/.235/.406/.561/.634/.876]",
                                metavar="#/#/#/#/#/#")
        generation_args.add_argument('--humidity', dest='humids',
                                help="Provide alternate ranges for humidities. " +
                                     "If not provided, the default values will be used. \n" +
                                     "[default = .059/.222/.493/.764/.927/.986/.998]",
                                metavar="#/#/#/#/#/#/#")
        generation_args.add_argument('-gv', '--gamma-value', dest='gv', type=float,
                                help="N = Gamma value for temperature/precipitation " +
                                     "gamma correction curve. [default = %(default)s]",
                                metavar="N", default='1.25')
        generation_args.add_argument('-go', '--gamma-offset', dest='go', type=float,
                                help="N = Adjustment value for temperature/precipitation " +
                                     "gamma correction curve. [default = %(default)s]",
                                metavar="N", default='.2')
        generation_args.add_argument('--not-fade-borders', dest='fade_borders', action="store_false",
                                help="Not fade borders",
                                default=True)
        generation_args.add_argument('--scatter', dest='scatter_plot',
                                action="store_true", help="generate scatter plot")
        generation_args.add_argument('--sat', dest='satelite_map',
                                action="store_true", help="generate satellite map")
        generation_args.add_argument('--ice', dest='icecaps_map',
                                action="store_true", help="generate ice caps map")

        # exposing axial_tilt
        generation_args.add_argument('-ax', '--axial_tilt', dest = 'axial_tilt',
                                     choices = range(-90, 91),
                                     metavar = '[-90-90]',
                                     help = 'Axial tilt (-180-180) denoting ' +
                                     'the world obliquity. Default is 25.',
                                     default = 25, type = int)

        # -----------------------------------------------------
        export_args = self.parser.add_argument_group(
            "Export Options", "You can specify the formats you wish the generated output to be in. ")
        export_args.add_argument("--export-format", dest="export_format", type=str,
                                    help="Export to a specific format such as BMP or PNG. " +
                                         "All possible formats: http://www.gdal.org/formats_list.html",
                                    default="PNG", metavar="STR")
        export_args.add_argument("--export-datatype", dest="export_datatype", type=str,
                                    help="Type of stored data (e.g. uint16, int32, float32 and etc.)",
                                    default="uint16", metavar="STR")
        export_args.add_argument("--export-dimensions", dest="export_dimensions", type=int,
                                    help="Export to desired dimensions. (e.g. 4096 4096)", default=None,
                                    nargs=2)
        export_args.add_argument("--export-normalize", dest="export_normalize", type=int,
                                    help="Normalize the data set to between min and max. (e.g 0 255)",
                                    nargs=2, default=None)
        export_args.add_argument("--export-subset", dest="export_subset", type=int,
                                    help="Normalize the data set to between min and max?",
                                    nargs=4, default=None)
