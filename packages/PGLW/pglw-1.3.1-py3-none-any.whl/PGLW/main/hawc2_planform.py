"""pure python reader for HAWC2 htc files"""

import numpy as np
from scipy.interpolate import pchip


def _convert_val(val):
    """
    convert a string value read from a file into either int, float or
    string
    """

    try:
        return int(val)
    except:
        try:
            return float(val)
        except:
            return val


class Entry(object):
    """class for "name: val" entries in input files"""

    def __init__(self, name, val, comment=""):
        self.name = name
        self.val = val
        self.comment = comment

    def _print(self, tab=0):
        """pretty print the entry"""

        if isinstance(self.val, str):
            return "%s%s" % (tab * " ", self.name + " " + self.val)
        try:
            return "%s%s" % (
                tab * " ",
                self.name + " " + " ".join(map(str, self.val)),
            )
        except:
            return "%s%s" % (tab * " ", self.name + " " + str(self.val))


class Section(object):
    """Class for list of Entry objects in a HAWC2 htc file"""

    def __init__(self, name):
        self.name = name
        self.entries = []
        self.comment = ""

    def get_entry(self, name):
        """convenience method to get a specific entry from section"""

        items = []
        for entry in self.entries:
            if entry.name == name:
                if isinstance(entry, Section):
                    return entry
                else:
                    items.append(entry.val)
        ##ACDI: debug
        # print(items)
        ###
        if len(items) == 0:
            return None
        if len(items) == 1:
            return items[0]
        else:
            return items

    def _next(self):
        try:
            entry = self.entries[self.pos]
            self.pos += 1
            return entry
        except:
            return False

    def _print(self, tab=0):
        """pretty print section recursively"""

        self.pos = 0
        string = ""

        string += "%sbegin %s" % (tab * " ", self.name + " ;\n")
        while self.pos < len(self.entries):
            entry = self._next()
            string += entry._print(tab=tab + 2)
        string += "%send %s" % (tab * " ", self.name + " ;\n")

        return string


class HAWC2InputDict(object):
    """
    Class for reading a HAWC2 htc file.

    The file is read into a nested list with Section objects with lists of
    Entry objects with name, val for each input parameter.

    All values are converted to either integer, float or string.

    pc, ae, and st files are not read.
    """

    def __init__(self):
        self.body_order = []

    def _print(self):
        string = ""
        for section in self.htc:
            string += section._print()
        return string

    def read(self, filename):
        fid = open(filename, "r", encoding="utf-8")
        self.lines = fid.readlines()
        self.nl = len(self.lines)
        self.htc = []
        self.pos = 0

        tmp = self._read_section(Section("tmp"))
        self.htc = tmp.entries
        self.inp = tmp

    def _read_section(self, section):
        while self.pos < self.nl:
            line = self._next()
            comment = line[line.find(";") + 1 :].strip()
            param = line[: line.find(";")]
            param = param.strip().split()
            if len(param) == 0:
                continue
            elif param[0] == ";":
                continue
            elif param[0] == "begin":
                newsection = Section(param[1])
                sec = self._read_section(newsection)
                section.entries.append(sec)
            elif param[0] == "end":
                return section
            elif param[0] == "exit":
                return section
            elif param[0] == "continue_in_file":
                htc = HAWC2InputDict()
                htc.read(param[1])
                self.body_order.extend(htc.body_order)
                section.entries.extend(htc.htc)
            else:
                vals = [_convert_val(val) for val in param[1:]]
                if param[0] == "name" and section.name == "main_body":
                    self.body_order.append(param[1])

                if len(vals) == 1:
                    section.entries.append(Entry(param[0], vals[0], comment))
                else:
                    section.entries.append(Entry(param[0], vals, comment))

        return section

    def _next(self):
        try:
            line = self.lines[self.pos]
            self.pos += 1
            return line
        except:
            return False


def read_hawc2_st_file(filename, var, setnum=-1):
    """
    Reader for a HAWC2 beam structure file. It creates a dictionary with keys
    the elements of the list var. The list must contain the name of the
    variables included in the st file in the correct order. It works for both
    the standard HAWC2 st input and the fully populated stiffness matrix.

    Parameters
    ----------
    filename: str
        Name of the file to read.
    var: list
        List containing the structural porperties names in the correct order.
        The list can be found in the class HAWC2BeamStructure

    Return
    ------
    st_sets: list
        List of dictionaries containning the structural properties.

    """
    right_set = False
    fid = open(filename, "r", encoding="utf-8")
    st_sets = []
    line = fid.readline()
    while line:
        if line.find("$") != -1 and right_set:
            ni = int(line.split()[1])
            st_data = np.zeros((ni, len(var)))
            for i in range(ni):
                tmp = fid.readline().split()
                st_data[i, :] = [float(tmp[j]) for j in range(len(var))]

            st = {}
            for iv, v in enumerate(var):
                st[v] = st_data[:, iv]
            st_sets.append(st)
        if line.find("#") != -1:
            if (int(line[1:2]) == setnum) or setnum == -1:
                right_set = True
            else:
                right_set = False
        line = fid.readline()

    fid.close()
    return st_sets


def read_hawc2_pc_file(filename):
    """Read a pc airfoil data file into a dictionary"""

    fid = open(filename, "r", encoding="utf-8")
    ltmp = fid.readline().strip("\r\n").split()
    nset = int(ltmp[0])
    desc = " ".join(ltmp[1:])
    sets = []
    for i in range(nset):
        pcset = {}
        pcset["polars"] = []
        npo = int(fid.readline().split()[0])
        rthick = []
        ii = 0
        for n in range(npo):
            polar = {}
            line = fid.readline().split()
            ni = int(float(line[1]))
            polar["np"] = ni
            polar["rthick"] = float(line[2])
            polar["desc"] = " ".join(line[3:])
            data = np.zeros((ni, 4))
            ii += 1
            for i in range(ni):
                dline = fid.readline().split("\t")[0]
                data[i, :] = [float(var) for var in dline.split()]
                ii += 1
            polar["aoa"] = data[:, 0]
            polar["cl"] = data[:, 1]
            polar["cd"] = data[:, 2]
            polar["cm"] = data[:, 3]
            rthick.append(polar["rthick"])
            pcset["polars"].append(polar)
        pcset["rthick"] = rthick
        sets.append(pcset)

    fid.close()
    return [desc, sets]


def read_hawc2_ae_file(filename):
    """read blade chord and relative thickness from an ae file
    only first set is read - comments are allowed after set"""

    fid = open(filename, "r", encoding="utf-8")
    blade_ae = {}

    # read header
    line = fid.readline()

    # read data for set 1
    line = fid.readline().strip("\r\n").split()
    ni = int(line[1])
    data = np.zeros((ni, 4))
    for i in range(ni):
        line = fid.readline().strip("\r\n").split()
        data[i, 0] = float(line[0])
        data[i, 1] = float(line[1])
        data[i, 2] = float(line[2])
        data[i, 3] = int(line[3])
    blade_ae["s"] = data[:, 0]
    blade_ae["chord"] = data[:, 1]
    blade_ae["rthick"] = data[:, 2]
    blade_ae["aeset"] = data[:, 3]

    fid.close()

    return blade_ae


class HAWC2InputReader(object):
    """
    Class to read HAWC2 files and store the data in variables trees.

    Parameters
    ----------
    htc_master_file: str
        Name of the htc file to read.

    Creates
    -------
    vartrees: HAWC2VarTrees
        Attribute corresponding to the variable tree with all the information
        of the model.

    Example
    -------
    >>> from PGLW.main.hawc2_geometry import HAWC2InputReader
    >>> reader = HAWC2InputReader('hawc2_master.htc')
    >>> reader.blade_ae
    >>> reader.c12axis

    """

    def __init__(self, htc_master_file, blade_body_name="blade1"):
        self.htc_master_file = htc_master_file
        self.blade_body_name = blade_body_name

        self.dict = HAWC2InputDict()
        self.dict.read(self.htc_master_file)
        self.htc = self.dict.htc
        self.ae = {}

        for section in self.htc:
            if section.name.lower() == "new_htc_structure":
                for sec in section.entries:
                    if sec.name == "main_body":
                        self._add_main_body(sec)
            elif section.name.lower() == "aero":
                self._add_aero(section)

    def _add_aero(self, section):
        self.ae_filename = section.get_entry("ae_filename")

        self.blade_ae = read_hawc2_ae_file(self.ae_filename)

    def _add_main_body(self, section):
        name = section.get_entry("name")
        if not name == self.blade_body_name:
            return
        c2sec = section.get_entry("c2_def")
        self.c12axis = np.array(c2sec.get_entry("sec"))[:, 1:5]

    def toPGL(self, x_offset="c12"):
        """
        Extract the blade geometry from a HAWC2 config.

        parameters
        ----------
        htcmaster: str
            filename of htc file
        x_offset: str
            options:
                | pale: assume pitch axis to be placed in x=0
                | c12: use the c12 axis as pitch axis and set p_le=0.

        returns
        -------
        pfd: array
            array with FUSED-Wind blade planform at HAWC2 ae file blade stations.
        """

        c12axis = self.c12axis
        blade_ae = self.blade_ae

        # interpolate c12axis onto blade_ae
        ni = blade_ae["chord"].shape[0]
        s_c12 = np.zeros(c12axis.shape[0])
        l = (
            (c12axis[1:, 0] - c12axis[:-1, 0]) ** 2
            + (c12axis[1:, 1] - c12axis[:-1, 1]) ** 2
            + (c12axis[1:, 2] - c12axis[:-1, 2]) ** 2
        ) ** 0.5
        s_c12[1:] = np.cumsum(l)
        s_c12 /= s_c12[-1]
        c12new = np.zeros((ni, 4))
        for i in range(4):
            tck = pchip(s_c12, c12axis[:, i])
            c12new[:, i] = tck(blade_ae["s"] / blade_ae["s"][-1])

        # Performing the conversion
        pfd = {}
        pfd["s"] = blade_ae["s"] / blade_ae["s"][-1]
        pfd["dy"] = np.zeros(pfd["s"].shape[0])
        pfd["smax"] = blade_ae["s"][-1]
        theta = c12new[:, 3] * np.pi / 180
        if x_offset == "pale":
            p_le = c12new[:, 0] / (blade_ae["chord"] * np.cos(theta)) + 0.5
            pfd["x"] = np.zeros(c12new.shape[0])
            pfd["y"] = c12new[:, 1] - c12new[:, 0] * np.tan(theta)
        elif x_offset == "c12":
            p_le = np.ones(ni) * 0.5
            pfd["x"] = c12new[:, 0] / c12new[-1, 2]
            pfd["y"] = c12new[:, 1] / c12new[-1, 2]
        pfd["z"] = c12new[:, 2] / c12new[-1, 2]
        pfd["rot_x"] = np.zeros(c12new.shape[0])
        pfd["rot_y"] = np.zeros(c12new.shape[0])
        pfd["rot_z"] = c12new[:, 3]
        pfd["chord"] = blade_ae["chord"] / c12new[-1, 2]
        pfd["rthick"] = blade_ae["rthick"] / 100.0
        pfd["p_le"] = p_le

        return pfd
