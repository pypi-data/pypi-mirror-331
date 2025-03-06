import numpy as np

from PGLW.main.curve import Curve
from PGLW.main.domain import Domain


class PGLComponent(object):
    def __init__(self, inputs=None):
        self.connectors = {}
        self.domain = Domain()
        if inputs is not None:
            self.read_inputs(inputs)

    #
    # def read_inputs(self, filename):
    #
    #     io = yaml.load(filename)
    #
    #         try:
    #             if isi

    def add_connector(self, name, con):
        name = self._check_name(name)

        setattr(self, name, con)
        self.connectors[name] = getattr(self, name)
        con.name = name
        return getattr(self, name)

    def delete_connectors(self):
        for name, b in self.connectors.items():
            del self.connectors[name]

    def connectors_from_domain(self):
        for name, b in self.domain.blocks.items():
            u0 = Curve(
                points=np.array([b.x[:, 0, 0], b.y[:, 0, 0], b.z[:, 0, 0]]).T
            )
            u1 = Curve(
                points=np.array(
                    [b.x[:, -1, 0], b.y[:, -1, 0], b.z[:, -1, 0]]
                ).T
            )
            v0 = Curve(
                points=np.array([b.x[0, :, 0], b.y[0, :, 0], b.z[0, :, 0]]).T
            )
            v1 = Curve(
                points=np.array(
                    [b.x[-1, :, 0], b.y[-1, :, 0], b.z[-1, :, 0]]
                ).T
            )
            self.add_connector(name + "_u0", u0)
            self.add_connector(name + "_u1", u1)
            self.add_connector(name + "_v0", v0)
            self.add_connector(name + "_v1", v1)

    def _check_name(self, name, c=0):
        if name in list(self.connectors.keys()):
            c += 1
            newname = name.split("-")
            try:
                # it = int(newname[-1])
                newname = newname[:-1]
            except RuntimeError:
                pass

            newname = "-".join(newname) + "-" + str(c)
            name = self._check_name(newname, c=c)
            return name
        else:
            return name

    def mirror_z(self, copy=False):
        newcons = {}
        for name, con in self.connectors.items():
            if copy:
                newname = name + "-mirror"
                newcon = con.copy()
                newcons[newname] = newcon
                newcon.mirror(2)
            else:
                con.mirror(2)

        for name, con in newcons.items():
            self.add_connector(name, con)

    def rotate_x(self, rot, center=np.zeros(3)):
        for name, con in self.connectors.items():
            con.rotate_x(rot, center)

    def rotate_y(self, rot, center=np.zeros(3)):
        for name, con in self.connectors.items():
            con.rotate_y(rot, center)

    def rotate_z(self, rot, center=np.zeros(3)):
        for name, con in self.connectors.items():
            con.rotate_z(rot, center)

    def scale(self, x):
        for name, con in self.connectors.items():
            con.scale(x)
