import numpy as np
from ruamel.yaml import YAML
import warnings
from scipy.interpolate import PchipInterpolator
from PGLW.main.geom_tools import calculate_length


class WindIOReader(object):

    def __init__(self, filename):

        with open(filename, "r") as myfile:
            inputs = myfile.read()

        self.windio_dict = YAML(typ="rt").load(inputs)

        self.pf = {}

    def read_windio(self, grid=None, grid_chord=np.linspace(0, 1, 200)):
        """
        script for parsing a WindIO dictionary interpolating planform
        data, and interpolating airfoils onto a common grid.

        Airfoils are interpolated to a default uniform grid
        as function of curve fraction with 200 points.

        Parameters
        ----------
        grid: ndarray
            1-D grid to interpolate the planform onto
        grid_chord: ndarray
            1-D grid to interpolate the base airfoils onto

        Returns
        -------
        geom_data: dict
            dictionary with the following items:
            |- pf: dict
                dictionary with planform (grid, x, y, z, chord, twist, pitch_axis,
                rthick)
            |- base_airfoils: dict
                dictionary with base airfoils (labels, coords, )
        """

        geom_data = dict()

        # blade planform
        yml = self.windio_dict["components"]["blade"]["outer_shape_bem"]
        pf = {}
        # if user hasn't specified a grid
        # we use the grid from chord and interpolate all other curves onto this
        if not isinstance(grid, (np.ndarray, list)):
            grid = np.asarray(yml["chord"]["grid"])

        pf["x"] = -PchipInterpolator(
            np.asarray(yml["reference_axis"]["y"]["grid"]),
            np.asarray(yml["reference_axis"]["y"]["values"]),
        )(grid)
        pf["y"] = PchipInterpolator(
            np.asarray(yml["reference_axis"]["x"]["grid"]),
            np.asarray(yml["reference_axis"]["x"]["values"]),
        )(grid)
        pf["z"] = PchipInterpolator(
            np.asarray(yml["reference_axis"]["z"]["grid"]),
            np.asarray(yml["reference_axis"]["z"]["values"]),
        )(grid)
        pf["chord"] = PchipInterpolator(
            yml["chord"]["grid"], yml["chord"]["values"]
        )(grid)
        pf["rot_z"] = (
            -PchipInterpolator(
                np.asarray(yml["twist"]["grid"]),
                np.asarray(yml["twist"]["values"]),
            )(grid)
            * 180.0
            / np.pi
        )
        pf["p_le"] = PchipInterpolator(
            np.asarray(yml["pitch_axis"]["grid"]),
            np.asarray(yml["pitch_axis"]["values"]),
        )(grid)
        pf["dy"] = np.zeros_like(pf["p_le"])

        pf["rot_x"] = np.zeros_like(pf["rot_z"])
        pf["rot_y"] = np.zeros_like(pf["rot_z"])
        has_rthick = False
        if "rthick" in yml:
            pf["rthick"] = PchipInterpolator(
                np.asarray(yml["rthick"]["grid"]),
                np.asarray(yml["rthick"]["values"]),
            )(grid)
            has_rthick = True
        rthick_s = yml["airfoil_position"]["grid"]

        s = calculate_length(np.array([pf["x"], pf["y"], pf["z"]]).T)
        pf["smax"] = s[-1]
        blade_length = pf["z"][-1]
        pf["s"] = s / pf["smax"]
        pf["x"] /= blade_length
        pf["y"] /= blade_length
        pf["z"] /= blade_length
        pf["chord"] /= blade_length
        # relative thickness is more tricky
        base_airfoils = []
        base_airfoil_names = []
        rthick_base = []
        rthick = []
        yafs = self.windio_dict["airfoils"]
        for af in yafs:
            base_airfoil_names.append(af["name"])

        # base airfoils
        # the relative thickness for each airfoil is located in the airfoils block.
        # we can link that definition to the labels defined in the
        # outer_shape_bem section, to back out the spanwise rthick curve
        rthick_base_n = []
        blade_airfoils_ix = []
        snew = grid_chord
        for label in yml["airfoil_position"]["labels"]:
            ix = base_airfoil_names.index(label)
            blade_airfoils_ix.append(ix)
            af = yafs[ix]
            # print(label, ix, af['relative_thickness'])
            rthick.append(af["relative_thickness"])
            if label not in rthick_base_n:
                rthick_base.append(af["relative_thickness"])
                rthick_base_n.append(label)
                try:
                    x = af["coordinates"]["x"]
                    y = af["coordinates"]["y"]
                    if np.abs(y[0] - y[-1]) < 1.0e-12:
                        y[0] += 0.001
                        y[-1] -= 0.001
                        print("opening base airfoil TE", label)
                    dx = np.zeros_like(x)
                    dy = np.zeros_like(x)
                    dx[1:] = np.diff(x)
                    dy[1:] = np.diff(y)
                    ds = (dx**2 + dy**2) ** 0.5
                    if np.any(ds[1:] == 0.0):
                        raise ValueError(
                            "WARNING, non-unique points in airfoil", label
                        )
                    s = np.cumsum(ds)
                    s /= s[-1]
                    afn = np.zeros((snew.shape[0], 2))
                    afn[:, 0] = PchipInterpolator(s, x)(snew)
                    afn[:, 1] = PchipInterpolator(s, y)(snew)
                    base_airfoils.append(afn[::-1])
                except:
                    pass

        # we interpolate the relative thickness from the label defitions
        # onto the chord grid
        if not has_rthick:
            pf["rthick"] = PchipInterpolator(rthick_s, rthick)(grid)

        # set vertical offset to zero since WindIO does not define this parameter
        pf["dy"] = np.zeros(pf["x"].shape[0])

        rthick_base = np.asarray(rthick_base)
        isort = list(rthick_base.argsort())
        geom_data["pf"] = pf
        geom_data["base_airfoils"] = {}
        geom_data["base_airfoils"]["labels"] = [
            rthick_base_n[i] for i in isort
        ]
        try:
            geom_data["base_airfoils"]["coords"] = [
                base_airfoils[i] for i in isort
            ]
        except:
            warnings.warn(
                "WindIO airfoils section does not contain profile coordinates"
            )
        geom_data["base_airfoils"]["rthick"] = np.array(rthick_base[isort])

        return geom_data

    def get_scaled_hub_length(self):

        return (
            self.windio_dict["components"]["hub"]["diameter"]
            / self.get_rotor_radius()
        )

    def get_blade_length(self):

        return self.windio_dict["components"]["blade"]["outer_shape_bem"][
            "reference_axis"
        ]["z"]["values"][-1]

    def get_scaled_root_diameter(self):

        return (
            self.windio_dict["components"]["blade"]["outer_shape_bem"][
                "chord"
            ]["values"][0]
            / self.get_rotor_radius()
        )

    def get_tilt(self):

        return np.rad2deg(
            self.windio_dict["components"]["nacelle"]["drivetrain"]["uptilt"]
        )

    def get_cone(self):

        return np.rad2deg(self.windio_dict["components"]["hub"]["cone_angle"])

    def get_rotor_radius(self):

        return (
            self.windio_dict["components"]["blade"]["outer_shape_bem"][
                "reference_axis"
            ]["z"]["values"][-1]
            + self.windio_dict["components"]["hub"]["diameter"] / 2.0
        )
