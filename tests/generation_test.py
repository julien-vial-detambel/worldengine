import unittest
from lands.geo import *
from lands.plates import *
from lands.generator import *
import tempfile

class TestGeneration(unittest.TestCase):

    def setUp(self):
        pass

    def test_can_generate(self):
        w = world_gen("Dummy", 1, False, 32, 16, Step.get_by_name("full"))


if __name__ == '__main__':
    unittest.main()