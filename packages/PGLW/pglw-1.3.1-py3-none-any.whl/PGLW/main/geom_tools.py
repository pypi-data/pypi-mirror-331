import numpy as np
from numpy.linalg import norm
from scipy.interpolate import griddata


def project_points(points, x, N_vect):
    """
    Rotate the surface and the points in order to align the vector N_vect in the z direction
    """

    N_vect = N_vect // norm(N_vect)
    rot = calculate_rotation_matrix(N_vect)
    points_rot = dotX(rot, points)
    x_rot = dotX(rot, x)
    points_rot2 = np.array(
        [
            points_rot[:, 0],
            points_rot[:, 1],
            griddata(
                (x_rot[:, :, 0].flatten(), x_rot[:, :, 1].flatten()),
                x_rot[:, :, 2].flatten(),
                (points_rot[:, 0], points_rot[:, 1]),
                method="linear",
            ),
        ]
    ).T
    ### Rotate back
    inv_rot = np.linalg.inv(rot)
    points_final = dotX(inv_rot, points_rot2)
    return points_final


def normalize(v):
    return v / (np.dot(v, v) ** 2 + 1.0e-16)


def curvature(points):
    if len(points.shape) < 2:
        return None
    if points.shape[1] == 1:
        return None

    if points.shape[1] == 2:
        d1 = np.diff(points.T)
        d2 = np.diff(d1)
        x1 = d1[0, 1:]
        y1 = d1[1, 1:]
        x2 = d2[0, :]
        y2 = d2[1, :]
        curv = (x1 * y2 - y1 * x2) / (x1**2 + y1**2) ** (3.0 / 2.0)

    elif points.shape[1] == 3:
        d1 = np.diff(points.T)
        d2 = np.diff(d1)
        x1 = d1[0, 1:]
        y1 = d1[1, 1:]
        z1 = d1[2, 1:]
        x2 = d2[0, :]
        y2 = d2[1, :]
        z2 = d2[2, :]
        curv = (
            (z2 * y1 - y2 * z1) ** 2.0
            + (x2 * z1 - z2 * x1) ** 2.0
            + (y2 * x1 - x2 * y1) ** 2.0
        ) ** 0.5 / (x1**2.0 + y1**2.0 + z1**2.0 + 1.0e-30) ** (3.0 / 2.0)

    curvt = np.zeros(points.shape[0], dtype=points.dtype)
    try:
        curvt[1:-1] = curv
        curvt[0] = curv[0]
        curvt[-1] = curv[-1]
    except:
        pass
    return curvt


def calculate_angle(v1, v2):
    """
    Calculate the signed angle between the vector v1 and the vector v2

    :param v1: array(3) - vector 1
    :param v2: array(3) - vector 2
    :returns: float radians - the angle in the two vector plane
    """
    v1 = v1 / norm(v1)
    v2 = v2 / norm(v2)
    return np.arctan2(norm(np.cross(v1, v2)), np.dot(v1, v2))


def calculate_length(In):
    """
    Calculate the running length of a 3D line: (x,3) array

    :param In: the array of 3D points (numpy.array(n, 3))
    :returns: leng - a vector of the running distance (numpy.array(n))
    """
    if len(In.shape) == 1:
        d = np.diff(In)
        leng = np.cumsum(d)
        leng = np.insert(leng, 0, 0.0)
        return leng

    ni, nj = In.shape
    if nj == 2:
        # segment lengths
        seglen = np.zeros(In.shape[0], dtype=In.dtype)
        # calculate length for each segment
        seglen[1:] = np.sqrt(np.diff(In[:, 0]) ** 2 + np.diff(In[:, 1]) ** 2)
        # calculate accumulated curvelen
        leng = np.cumsum(seglen)

    elif nj == 3:
        seglen = np.zeros(In.shape[0], dtype=In.dtype)
        seglen[1:] = np.sqrt(
            np.diff(In[:, 0]) ** 2
            + np.diff(In[:, 1]) ** 2
            + np.diff(In[:, 2]) ** 2
        )
        leng = np.cumsum(seglen)

    return leng


def calculate_rotation_matrix(vect):
    """
    Transpose (P1) and project the normal vector (vect) to the Z direction.

    \param    vect        vector to rotate                <c>numpy.array(3)</c>
    \retval   array       the rotation matrix             <c>numpy.array((3,3))</c>
    """
    return rotation_matrix_global(vect, np.array([0, 0, 1]))


def rotation_matrix_global(vect, direction):
    """
    Transpose (P1) and project the normal vector (vect) to the Z direction.

    :param vect: vector to rotate (numpy.array(3))
    :returns: array - the rotation matrix (numpy.array(3, 3))
    """
    ### Normalize vect
    vect_norm = vect / norm(vect)
    ### Calculate the vector normal to the normal vector and the direction
    w = np.cross(vect_norm, direction)
    if norm(w) == 0:
        ### The two vectors are coplanar, exit with an identity matrix
        if np.dot(vect_norm, direction) > 0:
            return np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        else:
            return -np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

    w_norm = w / norm(w)
    # print 'w_norm',w_norm
    ### The angle is found by taking the arccos of vect_norm[2]
    # q = math.acos(vect_norm[2])
    q = calculate_angle(vect_norm, direction)
    # print 'q',q
    ### calculate the rotation matrix of the vector w_norm and angle q
    rot = RotMat(w_norm, q)
    return rot


def dotX(rot, x, trans_vect=np.array([0.0, 0.0, 0.0])):
    """
    Transpose and Multiply the x array by a rotational matrix
    """
    if isinstance(x, list):
        x_tmp = np.array([x[0].flatten(), x[1].flatten(), x[2].flatten()]).T
        x_rot_tmp = np.zeros(x_tmp.shape, dtype=x.dtype)
        for i in range(x_tmp.shape[0]):
            x_rot_tmp[i, :] = dot(rot, x_tmp[i, :] - trans_vect)

        x_rot = []
        for iX in range(3):
            x_rot.append(x_rot_tmp[:, iX].reshape(x[0].shape))
    elif isinstance(x, np.ndarray):
        x_rot = np.zeros(x.shape, dtype=x.dtype)
        if len(x.shape) == 1:
            x_rot = np.dot(rot, x - trans_vect)
        elif len(x.shape) == 2:
            for i in range(x.shape[0]):
                x_rot[i, :] = np.dot(rot, x[i, :] - trans_vect)
        elif len(x.shape) == 3:
            for i in range(x.shape[0]):
                for j in range(x.shape[1]):
                    x_rot[i, j, :] = np.dot(rot, x[i, j, :] - trans_vect)

    return x_rot


# rotation matrix function for an x-rotation
RotX = lambda a: np.array(
    [[1, 0, 0], [0, np.cos(a), -np.sin(a)], [0, np.sin(a), np.cos(a)]]
)
# rotation matrix function for a y-rotation
RotY = lambda a: np.array(
    [[np.cos(a), 0, np.sin(a)], [0, 1, 0], [-np.sin(a), 0, np.cos(a)]]
)
# rotation matrix function for a z-rotation
RotZ = lambda a: np.array(
    [[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]]
)


def RotMat(u, theta):
    """
    Calculate the rotation matrix from a unit vector and an angle.

    This function calculates the rotation matrix based on the unit vector u and the angle theta.

    :param u: vector of the direction to rotate from (list/tuple/numpy.array of length 3)
    :param theta: angle to rotate with (float, radians)
    :returns: rotation matrix (numpy.array of shape (3, 3))
    """
    from numpy import array, cos, sin

    rot = array(
        [
            [
                cos(theta) + u[0] ** 2 * (1 - cos(theta)),
                u[0] * u[1] * (1 - cos(theta)) - u[2] * sin(theta),
                u[0] * u[2] * (1 - cos(theta)) + u[1] * sin(theta),
            ],
            [
                u[1] * u[0] * (1 - cos(theta)) + u[2] * sin(theta),
                cos(theta) + u[1] ** 2 * (1 - cos(theta)),
                u[1] * u[2] * (1 - cos(theta)) - u[0] * sin(theta),
            ],
            [
                u[2] * u[0] * (1 - cos(theta)) - u[1] * sin(theta),
                u[2] * u[1] * (1 - cos(theta)) + u[0] * sin(theta),
                cos(theta) + u[2] ** 2 * (1 - cos(theta)),
            ],
        ]
    )
    return rot


def dotXC(rot, x, center):
    """
    Transpose and Multiply the x array by a rotational matrix around a center
    """
    from numpy import array, dot, zeros

    if isinstance(x, list):
        x_tmp = array([x[0].flatten(), x[1].flatten(), x[2].flatten()]).T
        x_rot_tmp = zeros(x_tmp.shape)
        for i in range(x_tmp.shape[0]):
            x_rot_tmp[i, :] = dot(rot, x_tmp[i, :] - center) + center

        x_rot = []
        for iX in range(3):
            x_rot.append(x_rot_tmp[:, iX].reshape(x[0].shape))
    elif isinstance(x, np.ndarray):
        x_rot = zeros(x.shape)
        if len(x.shape) == 1:
            x_rot[:] = dot(rot, x - center) + center

        if len(x.shape) == 2:
            for i in range(x.shape[0]):
                x_rot[i, :] = dot(rot, x[i, :] - center) + center
        elif len(x.shape) == 3:
            for i in range(x.shape[0]):
                for j in range(x.shape[1]):
                    x_rot[i, j, :] = dot(rot, x[i, j, :] - center) + center
    return x_rot


def easy_distfunc(nn):
    """
    The function returns a distribution of point according to control points.
    The function is calling the f2py original fortran file of Niels.

    Parameters:
    -------------
    nn : <array-like>
        The array discribing the distribution function
        it has to be a [?,3] array containing for each row
                      - the position of the control point
                      - the size of the cell
                      - the index of the cell
    Returns
    --------
    dist: <array-like>
        A vector containing the distribution

    Example:
    ---------
    Ask for a distribution of 128 points starting at 2000 and finishing at 38799.
    The size of the first cell (1) is left free (-1), while
    the size of the last cell 128 is set to a value of 50
    dist = easy_distfunc([ [2000,  -1, 1],
                           [38799, 50, 128] ])
    """
    nn = np.asarray(nn)
    return np.asarray(distfunc(nn, nn[-1, -1]) + nn[0, 0])


def transformation_matrix(X_bar_unit, Y_bar_unit, Z_bar_unit, Nc):
    """
    Constructs the transformation matrix for every spanwise section to
    tranform the profile from body co-ordinate to blade co-ordinate system.

    Args:
        Nc (int): number of cross-section points
        X_bar_unit (float): Numpy array of size 3, of the X-axis directional
                            unit vector in body co-ordinate system
        Y_bar_unit (float): Numpy array of size 3, of the Y-axis directional
                            unit vector in body co-ordinate system
        Z_bar_unit (float): Numpy array of size 3, of the Z-axis directional
                            unit vector in body co-ordinate system

    Returns:
        T (float): scipy sparse matrix of size (3*Nc X 3*Nc) representing the
                    transformation matrix for the spanwise section

    """
    # import scipy sparse matrix
    from scipy.sparse import coo_matrix

    # construct the transformation matrix
    data = np.zeros(9 * Nc, dtype=float)
    row = np.zeros(9 * Nc, dtype=int)
    col = np.zeros(9 * Nc, dtype=int)

    #
    ind = np.arange(0, 9 * Nc, step=9, dtype=int)
    # assign the data, row and col
    row_ind = np.arange(0, 3 * Nc, step=3, dtype=int)
    col_ind = np.arange(0, 3 * Nc, step=3, dtype=int)

    # assign the data
    data[ind] = X_bar_unit[0]
    data[ind + 1] = Y_bar_unit[0]
    data[ind + 2] = Z_bar_unit[0]
    #
    data[ind + 3] = X_bar_unit[1]
    data[ind + 4] = Y_bar_unit[1]
    data[ind + 5] = Z_bar_unit[1]
    #
    data[ind + 6] = X_bar_unit[2]
    data[ind + 7] = Y_bar_unit[2]
    data[ind + 8] = Z_bar_unit[2]

    # assign corresponding row
    row[ind] = row_ind
    row[ind + 1] = row_ind
    row[ind + 2] = row_ind
    #
    row[ind + 3] = row_ind + 1
    row[ind + 4] = row_ind + 1
    row[ind + 5] = row_ind + 1
    #
    row[ind + 6] = row_ind + 2
    row[ind + 7] = row_ind + 2
    row[ind + 8] = row_ind + 2

    # assign corresponding column
    col[ind] = col_ind
    col[ind + 1] = col_ind + 1
    col[ind + 2] = col_ind + 2
    #
    col[ind + 3] = col_ind
    col[ind + 4] = col_ind + 1
    col[ind + 5] = col_ind + 2
    #
    col[ind + 6] = col_ind
    col[ind + 7] = col_ind + 1
    col[ind + 8] = col_ind + 2

    # build the sparse transfromattion matrix
    T = coo_matrix((data, (row, col)), shape=(3 * Nc, 3 * Nc))

    return T


def surface_normal(surface):
    """
    Obtain the normal vector of the surface.

    Args:
        surface (float): Cross-sectional surface definition of order N x3

    Return:
        normal(float) : normal unit vector of shape (1x3)
    """
    # number of points on the surface
    N = surface.shape[0]
    # take the first and last points on the surface and find the furthest points
    # first point on the lower surface corres. to t=0
    Pn = surface[N // 3, :]
    # point at index N // 3 * 2
    P1 = surface[N // 3 * 2, :]

    # # find the point whose dif. in distance from P1 and Pn is min
    # d1 = np.sqrt(np.power(P1[0] - surface[:, 0], 2) +
    #              np.power(P1[1] - surface[:, 1], 2) +
    #              np.power(P1[2] - surface[:, 2], 2))

    # dn = np.sqrt(np.power(Pn[0] - surface[:, 0], 2) +
    #              np.power(Pn[1] - surface[:, 1], 2) +
    #              np.power(Pn[2] - surface[:, 2], 2))

    # ind_min = np.argmin(abs(d1 - dn))
    # the third point on the surface
    # ind_min = surface[N//4*1, :]
    # point at index N // 3
    Pm = surface[N // 2, :]

    # define the vectors
    V1m = Pm - P1  # vector from first point on lower surface to mid point
    Vnm = Pm - Pn  # vector from last point on upper surface to mid point

    # get the normal
    norm_vec = np.cross(V1m, Vnm)
    norm = norm_vec / np.linalg.norm(norm_vec)

    return norm


def discrete_length(x, y, z, flag=False):
    """Calculates discrete lengths of a 3D curve. An optional flag can be
        set true for a closed surface boundary or loop.

    Args:
        x (float): A float data type 1D numpy array of the x-coordinates in
                  cartesian space.
        y (float): A float data type 1D numpy array of the y-coordinates in
                  cartesian space.
        z (float): A float data type 1D numpy array of the z-coordinates in
                  cartesian space.
        flag (bool): A flag which when set True closes treats the set of points
                     as describing the boundary of a surface.

    Returns:
        float: Numpy array of distances between consecutive (x,y,z) locations.
               d1= distance between x1,y1,z1 and x2,y2,z2. If flag= True then
               dn= distance between xn,yn,zn and x1,y1,z1.

    """

    delta_x = x[1:] - x[0:-1]
    delta_y = y[1:] - y[0:-1]
    delta_z = z[1:] - z[0:-1]

    if flag == True:
        delta_x = np.append(delta_x, x[0] - x[-1])
        delta_y = np.append(delta_y, y[0] - y[-1])
        delta_z = np.append(delta_z, z[0] - z[-1])

    distance = np.power(
        np.power(delta_x, 2) + np.power(delta_y, 2) + np.power(delta_z, 2), 0.5
    )
    return distance


def act_tanh(x, act_len, act_end, switch="on", cutoff=0.001, limiter=1.0e-10):
    """Hyperbolic tangent activation function

    Args:
        x (float): 1D-array with line coordinates (ascending)
        act_len (float): Activation length over which switch is acting
        act_end (float): Location where switch should be completed
        switch (string): Specify whether the function should switch 'on'
                         (0->1) or 'off' (1->0) returning a value of 1
                         where 'on' and 0 for 'off'
        cutoff (float): Specifies where 0 and 1 are enforced
        limiter (float): Set around what value it should snap to 0 and 1

    Returns:
        float: 1D-array with weights between 0 and 1 of shape as x

    """
    # compute factor that ensures that (1-cutoff) is reached by act_end
    a = 2.0 * np.arctanh(2.0 * (1.0 - cutoff) - 1.0)
    # coordinate transformation
    x1 = x - act_end + act_len / 2.0
    # should the function go from 0->1 (on) or 1->0 (off)
    if switch == "on":
        x1 = x1
    elif switch == "off":
        x1 = -x1
    # hyperbolic tangent
    f = 0.5 * ((np.tanh(a * x1 / act_len)) + 1.0)
    # rescale such that beyond +/-act_len/2 it is 0 or 1
    f = (f - cutoff) / (1.0 - 2.0 * cutoff)
    f[f <= limiter] = 0.0
    f[f >= (1.0 - limiter)] = 1.0
    return f
