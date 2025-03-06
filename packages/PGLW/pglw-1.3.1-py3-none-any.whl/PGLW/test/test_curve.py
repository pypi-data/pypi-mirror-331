import unittest

import numpy as np

from PGLW.main.curve import Curve


class CurveTest(unittest.TestCase):
    def test_splines(self):
        # available spline types
        spline_types = ["linear", "cubic", "ncubic", "akima", "pchip"]
        # observed
        xo = np.linspace(0.0, 10.0, 51)
        yo = np.sin(xo)
        out = np.zeros(len(spline_types))
        for i, spline in enumerate(spline_types):
            c = Curve(points=np.c_[xo, yo], spline=spline)
            c.redistribute()
            out[i] = np.sum(np.abs(c.points))
        ref = np.array(
            [
                561.044745191,
                561.185380485,
                561.185587413,
                561.183234852,
                561.186991999,
            ]
        )
        np.testing.assert_array_almost_equal(ref, out, 9)

    def test_points_shape(self):
        # If only one point
        points = np.array([[0.0], [0.0], [0.0]])
        self.assertRaises(ValueError, Curve, points)

        # If wrong transpose
        self.points = np.array(
            [
                [0.0, 0.5, 1 / 3, -0.3],
                [0.0, 0.3, 0.8, 0.1],
                [0.0, 0.2, 0.4, 0.6],
            ]
        )
        self.assertRaises(ValueError, Curve, points)

    def test_line_rotation(self):
        # Rotating in a non-comuting way
        points = np.array(
            [
                [0.0, 0.5, 1 / 3, -0.3],
                [0.0, 0.3, 0.8, 0.1],
                [0.0, 0.2, 0.4, 0.6],
            ]
        ).T
        curve = Curve(points)
        curve.rotate_y(90)
        curve.rotate_x(90)
        curve.rotate_z(-90)
        curve.rotate_x(-90)
        np.testing.assert_array_almost_equal(points, curve.points, 9)

    def test_unique_points(self):
        # Testing that having two equal points will fail as expected
        points = np.array(
            [[0.0, 0.0, 1.0], [0.0, 0.0, 2.0], [0.0, 0.0, 3.0]]
        ).T
        self.assertRaises(ValueError, Curve, points)


if __name__ == "__main__":
    unittest.main()
