import os
import sys
import time

# from IPython.Debugger import Tracer; debug_here = Tracer()
import numpy as np

import_database_str = """
### Import Database {database_name} from {filename} ------------------------------------- 
set DbFile [pw::Application begin DatabaseImport] 
$DbFile initialize -type PLOT3D {{{filepath}}} 
$DbFile read 
$DbFile convert 
$DbFile end 
unset DbFile
set {database_name} [pw::DatabaseEntity getByName {{surface-1}}]
${database_name} setName {{{database_name}}}
"""

create_database_str = """
### Create Database {database_name} ----------------------------------
set {database_name} [pw::DatabaseEntity getByName {{surface-1}}]
${database_name} setName {{{database_name}}}
"""

init_str = """
# Pointwise V16.03R3 Journal file - {time}
package require PWI_Glyph 2.3
pw::Application setUndoMaximumLevels 5
pw::Application reset
pw::Application clearModified
pw::Database setModelSize {ModelSize}
pw::Grid setNodeTolerance 1e-08
pw::Grid setConnectorTolerance 1e-08
pw::Grid setGridPointTolerance 1e-08
"""


class PointWiser(object):
    """Class that controls pointwise from python"""

    def __init__(self, P=[0, 0, 0], ModelSize=0.1, POINTWISE_PATH=None):
        """Create the main string"""
        self.str = init_str.format(time=time.ctime(), ModelSize=ModelSize)
        self.domains_name = []  # Tuple of domain string names
        self.domains_dic = (
            {}
        )  # Dictionary of domain string names (keys) and grid (values)
        self.extracted_domains = (
            {}
        )  # Dictionary containing a tuple of domains (keys) associated to each output files (keys)
        self.P = P
        self.POINTWISE_PATH = POINTWISE_PATH

    def set_pointwise_path(self, path):
        self.POINTWISE_PATH = path

    def import_IGS(self, filename, path=None, names=None):
        """
        Import an .igs file into pointwise.

        \param filename   the igs file name
        \param path       the path of the file
        \param names      a dictionary containing the original name of the
        """
        if path == None:
            path = os.path.realpath(".")
        filepath = path + "/" + filename

        self.add("set DBImport [pw::Application begin DatabaseImport]")
        self.add("$DBImport initialize -type Automatic {" + filepath + "}")
        self.add("$DBImport read")
        self.add("$DBImport convert")
        self.add("$DBImport end")
        self.add("unset DBImport")

        ### Add the name to the databases
        if names:
            for k, v in list(names.items()):
                self.add(
                    "set " + v + " [pw::DatabaseEntity getByName {" + k + "}]"
                )
                self.add("$" + v + " setName {" + v + "}")

    def cut_surface(
        self, domain, positions, direction="Z", dimension=100, run=False
    ):
        """
        Cut the domain "domain" at the positions "positions" in the direction "direction"

        \param domain       A string describing the domain to cut
        \param positions    A list containing all the positions in the direction to cut
        \param direction    A string describing the orientation of the cut planes
        \param dimension    Number of points to output

        returns a list of connectors
        """
        path = os.path.realpath(".")

        connector_list = ""
        for i in range(len(positions)):
            self.add(
                "### Slice "
                + domain
                + " at position "
                + str(positions[i])
                + " in direction "
                + direction
            )
            self.add("set CreatePlane [pw::Application begin Create]")
            self.add("set plane_" + str(i) + " [pw::Plane create]")
            self.add(
                "$plane_"
                + str(i)
                + " setConstant -"
                + direction
                + " "
                + str(positions[i])
            )
            self.add("$plane_" + str(i) + " setName {plane_" + str(i) + "}")
            self.add("$CreatePlane end")
            self.add("unset CreatePlane")
            self.add("set CreateSlice [pw::Application begin Create]")
            self.add(
                "set slice_"
                + str(i)
                + " [pw::Database intersect [list $Blade] [list $plane_"
                + str(i)
                + "]]"
            )
            self.add("$CreateSlice end")
            self.add("unset CreateSlice")
            # self.add('set new_slice1_' + str(i) + ' [pw::Curve join -reject new_slice2_' + str(i) + ' $slice_'+ str(i) + ']')
            self.add(
                "set Con_"
                + str(i)
                + " [pw::Connector createOnDatabase -merge 0 $slice_"
                + str(i)
                + "]"
            )
            self.add("set ColCon [pw::Collection create]")
            self.add("$ColCon set $Con_" + str(i))
            self.add("$ColCon do setDimension " + str(dimension))
            self.add(
                "set GridExportSegment [pw::Application begin GridExport $Con_"
                + str(i)
                + "]"
            )
            self.add(
                "$GridExportSegment initialize -type Segment {"
                + path
                + "/segments_"
                + str(i)
                + ".dat}"
            )
            self.add("$GridExportSegment verify")
            self.add("$GridExportSegment write")
            self.add("$GridExportSegment end")
            self.add("unset GridExportSegment")

            self.add("")
            connector_list = connector_list + "$Con_" + str(i) + " "

        # self.add('### Extract the connectors as a segment file')
        # self.add('set GridExportSegment [pw::Application begin GridExport [list ' + connector_list + ']]')
        # self.add('$GridExportSegment initialize -type Segment {' +  filepath + '}')
        # self.add('$GridExportSegment verify')
        # self.add('$GridExportSegment write')
        # self.add('$GridExportSegment end')
        # self.add('unset GridExportSegment')

        self.write("script.glf")
        if run:
            self.run("script.glf")

        cons = []
        for i in range(len(positions)):
            con = self.read_connectors("segments_" + str(i) + ".dat", pwd=path)
            if len(con) > 0:
                cons.append(con)
        # cons.append(self.read_connectors('segments_' + str(i) + '.dat',pwd=path))
        return cons

    def read_connectors(self, filename, pwd=None):
        """
        Read a file of connectors (segment format from PointWise).

        The segment file format is defined as follow:
            - The number of points in the connector
            - The x,y,z coordinates of each points

        There is no indications of how many connectors there are in the file. You have to determine it by doing a EOF test.

        \param    filename      \c string   :     the file name
        \param    pwd           \c string   :     the path of the file

        \retval   connectors    <c>list of array((n,3)) </c>    :   A list of connectors
        """
        if pwd == None:
            pwd = os.path.realpath(".")
        filepath = pwd + "/" + filename
        try:
            fid = open(filepath, "r")
            ### Read the file back into python
            ev = fid.read().split()
            fid.close()
            ### Read the number of blocks (domains)
            NbPts = int(ev[0])
            i_start = 1
            i_end = NbPts * 3
            connector = []
            while i_end <= len(ev):
                connector.append(
                    np.array(ev[i_start : i_end + 1], dtype="float64").reshape(
                        (-1, 3)
                    )
                )
                i_start = i_end + 2
                if i_end + 1 < len(ev):
                    i_end = i_start + int(ev[i_end + 1]) * 3 - 1
                else:
                    break
            return connector
        except:
            return []

    def write(self, filename):
        """Write the self.str into a .glf file for pointwise"""
        fid = open(filename, "w")
        fid.writelines(self.str)
        fid.close()

    def add(self, new_str):
        """Add a line to the self.str string, with a \\n at the end"""
        self.str = self.str + new_str + "\n"

    def write_xyz(self, X, filename, P=[0, 0, 0]):
        """
        Write a database in Plot3D format (.xyz file)

        \param X X[:,:,iX]
        """
        fid = open(filename, "w")
        if isinstance(X, dict):
            ### Number of separate databases
            fid.write("%d\n" % (len(list(X.keys()))))
            for k, v in X.items():
                ### Number of coordinates for database[n] [ni nj nk]
                fid.write("%d %d %d\n" % (v.shape[0], v.shape[1], 1))
            for k, v in X.items():
                ### Print for each database all the Xs, then Ys and Zs..
                for iC in range(3):
                    newX = v[:, :, iC] - P[iC]
                    newX.T.tofile(fid, sep="\n", format="%24.8e")
        if isinstance(X, list):
            ### Number of separate databases
            fid.write("%d\n" % (len(X)))
            for v in X:
                ### Number of coordinates for database[n] [ni nj nk]
                fid.write("%d %d %d\n" % (v.shape[0], v.shape[1], 1))
            for v in X:
                ### Print for each database all the Xs, then Ys and Zs..
                for iC in range(3):
                    newX = v[:, :, iC] - P[iC]
                    newX.T.tofile(fid, sep="\n", format="%24.8e")
        else:
            ### Number of separate databases
            fid.write("%d\n" % (1))
            ### Number of coordinates for database[n] [ni nj nk]
            fid.write("%d %d %d\n" % (X.shape[0], X.shape[1], 1))
            ### Print for each database all the Xs, then Ys and Zs..
            for iC in range(3):
                newX = X[:, :, iC] - P[iC]
                newX.T.tofile(fid, sep="\n", format="%24.8e")
        fid.close()

    def import_database(self, database, database_name, filename):
        """Import a database, give it a name and write it in a file"""
        pwd = os.path.realpath(".")
        filepath = pwd + "/" + filename

        ### Write the database in the file
        self.write_xyz(database, filepath, self.P)

        dic = {
            "database": database,
            "database_name": database_name,
            "filename": filename,
            "filepath": filepath,
        }

        ### Import and rename the database
        self.add(import_database_str.format(**dic))

    def create_database(self, database_name):
        """Associate a database to a number"""
        self.add(create_database_str.format(database_name=database_name))

    def import_connectors(self, Connectors_dic, filename="connectors.dat"):
        """Import the connectors from a segment file (filename)"""
        P = self.P
        pwd = os.path.realpath(".")
        self.add("")
        self.add(
            "### Import Connectors from "
            + pwd
            + "/"
            + filename
            + " -------------------"
        )
        self.add("set SegFile [pw::Application begin GridImport]")
        self.add(
            "$SegFile initialize -type Segment {" + pwd + "/" + filename + "}"
        )
        self.add("$SegFile read")
        self.add("$SegFile convert")
        self.add("$SegFile end")
        self.add("unset SegFile")

        fid = open(pwd + "/" + filename, "w")
        inc = 0
        for name, con in Connectors_dic.items():
            ### Write the number of point in the current connector
            fid.write("%d\n" % (con.shape[0]))
            ### Transpose the connector using the point P
            for i in range(con.shape[0]):
                fid.write(
                    "%24.8e %24.8e %24.8e\n"
                    % (con[i, 0] - P[0], con[i, 1] - P[1], con[i, 2] - P[2])
                )
            ### Rename the connectors using the dictionary name
            inc += 1
            self.add(
                "set "
                + name
                + " [pw::GridEntity getByName {con-"
                + str(inc)
                + "}]"
            )
            self.add("$" + name + " setName {" + name + "}")
        fid.close()

    def create_domain(
        self,
        domain,
        connectors,
        EdgeAttributes=None,
        database=None,
        iterations=0,
    ):
        """Create a domain using several connectors given as a tuple of strings
        f.ex:
            domain = 'TETP_Dom'
            connectors = ('HTEP','CTEP','VMTP','TET')
            EdgeAttributes = ('Orthogonal','Orthogonal','Orthogonal','Orthogonal')
            database = 'PressureDB'
            iterations = 50

        The order of the connector will have an influence on the i,j orientation, and
        therefore the normal orientation. So use the right-hand approach to decide which
        order is most appropriate.
        Note that Edge Attributes, database and iterations are optionals. If there is an
        EdgeAttributes and a database given, it will try to smooth the domain.
        """
        self.add(
            "\n### Create Domain: "
            + domain
            + " ----------------------------------"
        )
        self.add("set CreateDom [pw::Application begin Create]")
        self.add("    set " + domain + " [pw::DomainStructured create]")
        for iE in range(4):
            if connectors[iE].__class__.__name__ == "tuple":
                self.add(
                    "    ###  Create edge"
                    + str(iE + 1)
                    + " using "
                    + ", ".join(connectors[iE])
                )
                self.add("    set edge" + " [pw::Edge create]")
                ### This edge is composed of difference connectors
                for iC in range(len(connectors[iE])):
                    self.add(
                        "    $edge" + " addConnector $" + connectors[iE][iC]
                    )
            elif connectors[iE].__class__.__name__ == "str":
                self.add(
                    "    ###  Create edge"
                    + str(iE + 1)
                    + " using "
                    + connectors[iE]
                )
                self.add("    set edge" + " [pw::Edge create]")
                self.add("    $edge" + " addConnector $" + connectors[iE])
            else:
                print(
                    "ERROR: this is not a valid connector name: ",
                    connectors[iE],
                )
            self.add("    $" + domain + " addEdge $edge")
        self.add("    $" + domain + " setName {" + domain + "}")
        self.add("    unset edge")
        self.add("$CreateDom end")
        self.add("unset CreateDom")
        ### Solve it if the required parameters are given
        if EdgeAttributes != None and domain != None and database != None:
            self.solve_domain(domain, database, EdgeAttributes, iterations)
        self.domains_name.append(domain)

    def solve_domain(self, domain, database, EdgeAttributes, iterations=0):
        """Solve a domain using some specific database to project and edge attributes
        f.ex: EdgeAttributes = ('Orthogonal','Interpolate','Current','Adjacent')
        """
        self.add(
            "\n### Solve Domain "
            + domain
            + " using "
            + database
            + " -------------------"
        )
        self.add(
            "set solveDomain [pw::Application begin EllipticSolver [list $"
            + domain
            + "]]"
        )
        if database != None:
            self.add(
                "    $"
                + domain
                + " setEllipticSolverAttribute ShapeConstraint DataBase"
            )
            self.add(
                "    $"
                + domain
                + " setEllipticSolverAttribute ShapeConstraint [list $"
                + database
                + "]"
            )

        for iE in range(4):
            self.add(
                "    $"
                + domain
                + " setEllipticSolverAttribute -edge "
                + str(iE + 1)
                + " EdgeAngleCalculation "
                + EdgeAttributes[iE]
            )
        self.add("    $solveDomain run Initialize")

        if iterations > 0:
            self.add("    $solveDomain run " + str(iterations))
        self.add("$solveDomain end")
        self.add("unset solveDomain")

    def export_domains(self, filename, domains=None):
        """
        Export the domains that have been created previously using the create_domain function
        """
        if domains == None:
            domains = self.domains_name
        domains_list = ""
        for iD in range(len(domains)):
            domains_list = domains_list + "$" + domains[iD] + " "
        pwd = os.path.realpath(".")
        filepath = pwd + "/" + filename
        self.add(
            "\n### Export Domains to " + filename + " -------------------"
        )
        self.add(
            "set GridExporter [pw::Application begin GridExport [list "
            + domains_list
            + "]]"
        )
        self.add(
            "    $GridExporter initialize -type PLOT3D {" + filepath + "}"
        )
        self.add("    $GridExporter verify")
        self.add("    $GridExporter write")
        self.add("$GridExporter end")
        self.add("unset GridExporter")
        self.extracted_domains[filename] = domains

    def read_domains(self, filename):
        """
        Read the domaines that have been saved throught the export_domain function
        """
        pwd = os.path.realpath(".")
        filepath = pwd + "/" + filename
        fid = open(filepath, "r")
        ev = fid.read().split()
        ### Read the number of blocks (domains)
        nblocks = int(ev[0])
        ### Read an array containing the dimentions of the different blocks (domains)
        dims = np.array(ev[1 : nblocks * 3 + 1], dtype="int16").reshape(
            (nblocks, 3)
        )
        istart = nblocks * 3 + 1
        ### Each domain is stored as a tuple(3).array(ni,nj) in a dictionary (the keys are the domain names)
        for iN in range(nblocks):
            tmp_array = np.zeros((dims[iN, 0], dims[iN, 1], 3))
            for iX in range(3):
                iend = istart + dims[iN, 0] * dims[iN, 1]
                tmp_array[:, :, iX] = (
                    np.array(ev[istart:iend], dtype="float64")
                    .reshape((dims[iN, 1], dims[iN, 0]))
                    .swapaxes(0, 1)
                    + self.P[iX]
                )
                istart = iend
            self.domains_dic[self.extracted_domains[filename][iN]] = tmp_array
        fid.close()
        return self.domains_dic

    def run(self, scriptname):
        if not self.POINTWISE_PATH:
            print("POINTWISE_PATH not set, returning")
            return

        pwd = os.path.realpath(".")
        filepath = pwd + "/" + scriptname
        if sys.platform == "darwin":
            os.system(self.POINTWISE_PATH + " " + filepath)
        else:
            os.system(self.POINTWISE_PATH + " -b " + filepath)

        print("Pointwise executed using " + filepath)
