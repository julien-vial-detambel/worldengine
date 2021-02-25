from worldengine.simulations.basic import find_threshold_f
import numpy


class HumiditySimulation(object):
    @staticmethod
    def is_applicable(world):
        return world.has_precipitations() and world.has_irrigation() and (
            not world.has_humidity())

    def execute(self, world, seed):
        assert seed is not None
        data, quantiles = self._calculate(world)
        world.humidity = (data, quantiles)

    @staticmethod
    def _calculate(world):
        moisture_ranges = world.moisture_ranges
        precipitationWeight = 1.0
        irrigationWeight = 3
        data = numpy.zeros((world.size.height, world.size.width), dtype=float)

        data = (world.layers['precipitation'].data * precipitationWeight - world.layers['irrigation'].data * irrigationWeight)/(precipitationWeight + irrigationWeight)

        # These were originally evenly spaced at 12.5% each but changing them
        # to a bell curve produced better results
        ocean = world.layers['ocean'].data
        quantiles = {}
        quantiles['12'] = find_threshold_f(data, moisture_ranges[6], ocean)
        quantiles['25'] = find_threshold_f(data, moisture_ranges[5], ocean)
        quantiles['37'] = find_threshold_f(data, moisture_ranges[4], ocean)
        quantiles['50'] = find_threshold_f(data, moisture_ranges[3], ocean)
        quantiles['62'] = find_threshold_f(data, moisture_ranges[2], ocean)
        quantiles['75'] = find_threshold_f(data, moisture_ranges[1], ocean)
        quantiles['87'] = find_threshold_f(data, moisture_ranges[0], ocean)
        return data, quantiles
