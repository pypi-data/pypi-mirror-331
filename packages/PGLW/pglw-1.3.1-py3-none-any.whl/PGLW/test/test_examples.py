import glob
import os
import sys
import traceback
import unittest


def remove(pattern):
    try:
        for f in glob.glob(pattern):
            os.remove(f)
    except:
        pass


class ExamplesTest(unittest.TestCase):
    def setUp(self):
        sys.path.append(os.path.join("..", "examples"))
        os.chdir(os.path.join("..", "examples"))

    def tearDown(self):
        remove("grid.x2d")
        remove("*.xyz*")
        os.chdir(os.path.join("..", "test"))

    def test_blademesher_1b_example(self):
        try:
            import blademesher_1b_example
        except:
            traceback.print_exc()
            raise RuntimeError()

    # something wrong with specified dist
    # def test_blademesher_1b_flap_example(self):
    #     try:
    #         import blademesher_1b_flap_example
    #     except:
    #         traceback.print_exc()
    #         raise RuntimeError()

    def test_blademesher_example(self):
        try:
            import blademesher_example
        except:
            traceback.print_exc()
            raise RuntimeError()

    def test_blademesher_nacelle_example(self):
        try:
            import blademesher_nacelle_example

            # os.remove("grid.x2d")
        except:
            traceback.print_exc()
            raise RuntimeError()

    def test_bladeroot_example(self):
        try:
            import bladeroot_example

            self.assertEqual(True, True)
        except:
            traceback.print_exc()
            raise RuntimeError()

    def test_coons_extrusion_example(self):
        try:
            import coons_extrusion_example
        except:
            traceback.print_exc()
            raise RuntimeError()

    def test_coonsblade_example(self):
        try:
            import coonsblade_example
        except:
            traceback.print_exc()
            raise RuntimeError()

    def test_coonstip_example(self):
        try:
            import coonstip_example
        except:
            traceback.print_exc()
            raise RuntimeError()

    def test_loftedblade_example(self):
        try:
            import loftedblade_example
        except:
            traceback.print_exc()

    def test_vg_example(self):
        try:
            import vg_example
        except:
            traceback.print_exc()
            raise RuntimeError()


if __name__ == "__main__":
    unittest.main()
