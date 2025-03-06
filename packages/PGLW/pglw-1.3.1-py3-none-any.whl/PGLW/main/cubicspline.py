import platform

from numpy import array, asarray, float32, float64, zeros

from PGLW.PGLlib import spline, splint

# hack to avoid inconsistencies in results on Windows due to 32/64 bit conversion errors
if "Windows" in platform.platform():
    _float = float32
else:
    _float = float64


class CubicSpline(object):
    """
    Interpolates a 1-D function using the Numerical Recipes Natural cubic spline.

    x and y are arrays that describe some curve. This class returns a function,
    which when called with an array returns the spline approximation of the
    original curve.

    Parameters
    ----------
    x : array_like
        A 1-D array of monotonically increasing real values.
    y : array_like
        array of real values. The dimension of y must be the equal
        to the length of x.
    copy : bool, optional
        If True, the class makes internal copies of x and y.
        If False, references to `x` and `y` are used. The default is to copy.

    Examples
    --------
    >>> from cubicspline import CubicSpline
    >>> x = np.arange(0, 10)
    >>> y = np.exp(-x/3.0)
    >>> f = CubicSpline(x, y)

    >>> xnew = np.arange(0,9, 0.1)
    >>> ynew = f(xnew)   # use interpolation function returned by `CubicSpline`

    """

    def __init__(self, x, y, yp1=1.0e32, ypn=1.0e32, copy=True):
        self.x = array(x, copy=copy)
        self.y = array(y, copy=copy)
        self.ys = asarray(spline(x, y, yp1, ypn), dtype=_float)

    def __call__(self, x_new):
        """
        Find interpolated y_new = f(x_new).

        Parameters
        ----------
        x_new : number or array
            New independent variable(s).

        Returns
        -------
        y_new : ndarray
            Interpolated value(s) corresponding to x_new.
        """

        if isinstance(x_new, float):
            y_new = asarray(
                splint(self.x, self.y, self.ys, array(x_new)), dtype=_float
            )
        else:
            x_new = asarray(x_new)
            y_new = zeros(x_new.shape[0])
            y_new = asarray(
                splint(self.x, self.y, self.ys, x_new), dtype=_float
            )

        return y_new
