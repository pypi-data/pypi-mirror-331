from spb import plot3d_parametric_line, plot3d_parametric_surface
from spb.graphics import arrow_2d, arrow_3d, graphics
from spb.plot_functions.functions_2d import _create_generic_data_series, _set_labels
from spb.utils import _check_arguments, _plot_sympify
from sympy import Matrix, N


def _check_dims(v, s=None):
    if hasattr(v[0], "__iter__") or isinstance(v[0], Matrix):
        d = len(v[0])
        if d not in (2, 3):
            err = "First vector was neither 2D or 3D"
            raise TypeError(err)
        for vv in v:
            if len(vv) != d:
                err = "A vector didn't match the dimensions of the first vector"
                raise TypeError(err)
            if s is not None:
                for ss in s:
                    if len(ss) != d:
                        err = "A starting point didn't match the dimensions of the vectors."
                        raise TypeError(err)
        return d, True

    d = len(v)
    if d not in (2, 3):
        err = "The vector must be either 2D or 3D."
        raise TypeError(err)
    if s is not None and len(s) != d:
        err = "Starting point and vector must both be either 2D or 3D."
        raise TypeError(err)
    return d, False


def _calc_limits(v, s):
    kw = ["xlim", "ylim", "zlim"]
    result = {}

    if not hasattr(v[0], "__iter__"):
        v = [v]
        s = [s]

    for d in range(len(v[0])):
        d_min = v[0][d] + s[0][d] if v[0][d] + s[0][d] < s[0][d] else s[0][d]
        d_max = v[0][d] + s[0][d] if v[0][d] + s[0][d] > s[0][d] else s[0][d]
        for i in range(len(v)):
            if v[i][d] + s[i][d] > s[i][d]:
                nextmax = v[i][d] + s[i][d]
                nextmin = s[i][d]
            else:
                nextmin = v[i][d] + s[i][d]
                nextmax = s[i][d]
            d_min = min(nextmin, d_min)
            d_max = max(nextmax, d_max)
        extra = (d_max - d_min) / 10
        result[kw[d]] = (d_min - extra, d_max + extra)
    return result


def plot_vector(*args, **kwargs):
    """Afbild en eller flere vektorer (2D eller 3D).

    - Afbild en vektor der starter i (0,0)

    `plot_vector(v, **kwargs)`

    - Afbild flere vektorer med forskellige startpunkter

    `plot_vector([s1,s2], [v1,v2], **kwargs)`

    Parametre
    ---------
    s : iterable, optional
        Startpunkterne for vektorerne. Skal indeholde 2-3 elementer.

    v : iterable
        Vektorernes retninger. Skal indeholde 2-3 elementer.

    kwargs : se `arrow_2d`, `arrow_3d`

    Returnerer
    ---------
    plt : Plot
        Plotobjektet.

    Se også
    ---------
    - [SPB: arrow_2d](https://sympy-plot-backends.readthedocs.io/en/latest/modules/graphics/vectors.html#spb.graphics.vectors.arrow_2d)
    - [SPB: arrow_3d](https://sympy-plot-backends.readthedocs.io/en/latest/modules/graphics/vectors.html#spb.graphics.vectors.arrow_3d)
    """
    if len(args) == 1:
        v = args[0]
        dim, lst = _check_dims(v)

        if lst:
            for i in range(len(v)):
                if isinstance(v[i], Matrix):
                    v[i] = [float(N(x)) for x in v[i]]
            s = [[0] * dim] * len(v)
        else:
            if isinstance(v, Matrix):
                v = [float(N(x)) for x in v]
            s = [0] * dim

    elif len(args) == 2:  # noqa: PLR2004
        s = args[0]
        v = args[1]
        dim, lst = _check_dims(v, s)
        if lst:
            for i in range(len(v)):
                if isinstance(v[i], Matrix):
                    v[i] = [float(N(x)) for x in v[i]]
            for i in range(len(s)):
                if isinstance(s[i], Matrix):
                    s[i] = [float(N(x)) for x in s[i]]
        if isinstance(v, Matrix):
            v = [float(N(x)) for x in v]
        if isinstance(s, Matrix):
            s = [float(N(x)) for x in s]

    else:
        err = f"plot_vector() expects 1 or 2 arguments ({len(args)} were given)"
        raise TypeError(err)

    limits = _calc_limits(v, s)
    for lim in limits:
        kwargs.setdefault(lim, limits[lim])

    kwargs.setdefault("aspect", "equal")
    kwargs.setdefault("xlabel", "x")
    kwargs.setdefault("ylabel", "y")
    if kwargs.get("label", False):
        kwargs.setdefault("legend", True)
    else:
        kwargs.setdefault("legend", False)

    global_labels = kwargs.pop("label", [])
    global_rendering_kw = kwargs.pop("rendering_kw", None)

    if dim == 2:  # noqa: PLR2004
        arrows = []
        if hasattr(s[0], "__iter__"):
            for start, vec in zip(s, v):
                arrows.extend(arrow_2d(start, vec, **kwargs))
        else:
            arrows.extend(arrow_2d(s, v, **kwargs))
        _set_labels(arrows, global_labels, global_rendering_kw)
        gs = _create_generic_data_series(**kwargs)
        return graphics(*arrows, gs, **kwargs)

    elif dim == 3:  # noqa : PLR2004
        kwargs.setdefault("zlabel", "z")
        arrows = []
        if hasattr(s[0], "__iter__"):
            for start, vec in zip(s, v):
                arrows.extend(arrow_3d(start, vec, **kwargs))
        else:
            arrows.extend(arrow_3d(s, v, **kwargs))
        _set_labels(arrows, global_labels, global_rendering_kw)
        gs = _create_generic_data_series(**kwargs)
        return graphics(*arrows, gs, **kwargs)

    else:
        err = "Mixing 2D vectors with 3D vectors is not allowed."
        raise ValueError(err)


def plot3d_line(*args, **kw_args):
    """Afbild en eller flere parameterfremstillinger for linjer i et rumligt koordinatsystem.

    - Afbild en linje.

    `plot3d_line(line, range, **kwargs)`

    - Afbild flere linjer med samme interval.

    `plot3d_line(line_1, line_2, ..., range, **kwargs)`

    - Afbild flere linjer med forskellige intervaller.

    `plot3d_line((line_1, range1), (line_2, range2), ..., **kwargs)`

    - Afbild flere linjer med forskellige intervaller og labels.

    `plot3d_line((line_1, range1, label1), (line_2, range2, label2), ..., **kwargs)`

    Parametre
    ---------
    line : 3D iterables or matrices
        Parameterfremstillingen for en linje.

    range : tuple
        Intervallet for den frie parameter. Angives som tuple: (t, t_min, t_max).

    Label : str
        Tekst til at identificere linjen.

    kwargs : se `line_parametric_3d`

    Returnerer
    ---------
    plt : Plot
        Plotobjektet.

    Se også
    ---------
    - [SPB: line_parametric_3d](https://sympy-plot-backends.readthedocs.io/en/latest/modules/graphics/functions_3d.html#spb.graphics.functions_3d.line_parametric_3d)
    """
    kw_args.setdefault("use_cm", False)

    args = _plot_sympify(args)
    plot_expr = _check_arguments(args, 1, 1)
    for i in range(len(plot_expr)):
        if plot_expr[i][3] is None:
            if plot_expr[i][2] is None:
                plot_expr[i] = (plot_expr[i][0][0], plot_expr[i][0][1], plot_expr[i][0][2], plot_expr[i][1])
            else:
                plot_expr[i] = (
                    plot_expr[i][0][0],
                    plot_expr[i][0][1],
                    plot_expr[i][0][2],
                    plot_expr[i][1],
                    plot_expr[i][2],
                )
        else:
            plot_expr[i] = (
                plot_expr[i][0][0],
                plot_expr[i][0][1],
                plot_expr[i][0][2],
                plot_expr[i][1],
                plot_expr[i][2],
                plot_expr[i][3],
            )
    return plot3d_parametric_line(*plot_expr, **kw_args)


def plot3d_plane(*args, **kw_args):
    """Afbild en eller flere parameterfremstillinger for planer i et rumligt koordinatsystem.

    - Afbild en plan.

    `plot3d_plane(plane, range_s, range_t, **kwargs)`

    - Afbild flere planer med samme intervaller.

    `plot3d_plane(plane_1, plane_2, range_s, range_t, **kwargs)`

    - Afbild flere planer med forskellige intervaller.

    `plot3d_plane((plane_1, range_s1, range_t1), (plane_2, range_s2, range_t2), **kwargs)`

    - Afbild flere planer med forskellige intervaller og labels.

    `plot3d_plane((plane_1, range_s1, range_t1, label1), (plane_2, range_s2, range_t2, label2), **kwargs)`

    Parametre
    ---------
    plane : 3D iterables or matrices
        Parameterfremstillingen for en plan.

    range_s : tuple
        Intervallet for den første frie parameter. Angives som tuple: (s, s_min, s_max).

    range_t : tuple
        Intervallet for den anden frie parameter. Angives som tuple: (t, t_min, t_max).

    Label : str
        Tekst til at identificere planen.

    kwargs : se `surface_parametric`

    Returnerer
    ---------
    plt : Plot
        Plotobjektet.

    Se også
    ---------
    - [SPB: surface_parametric](https://sympy-plot-backends.readthedocs.io/en/latest/modules/graphics/functions_3d.html#spb.graphics.functions_3d.surface_parametric)
    """
    kw_args.setdefault("use_cm", False)

    args = _plot_sympify(args)
    plot_expr = _check_arguments(args, 1, 2)
    for i in range(len(plot_expr)):
        if plot_expr[i][3] is None:
            if plot_expr[i][2] is None:
                plot_expr[i] = (plot_expr[i][0][0], plot_expr[i][0][1], plot_expr[i][0][2], plot_expr[i][1])
            else:
                plot_expr[i] = (
                    plot_expr[i][0][0],
                    plot_expr[i][0][1],
                    plot_expr[i][0][2],
                    plot_expr[i][1],
                    plot_expr[i][2],
                )
        else:
            plot_expr[i] = (
                plot_expr[i][0][0],
                plot_expr[i][0][1],
                plot_expr[i][0][2],
                plot_expr[i][1],
                plot_expr[i][2],
                plot_expr[i][3],
            )
    return plot3d_parametric_surface(*plot_expr, **kw_args)


def vector(*args):
    """Hjælpefunktion til at danne en SymPy matrix til at repræsentere en vektor.

    - 2D vektor

    `vector(x,y)`

    - 3D vektor

    `vector(x,y,z)`

    Bemærk at Vector klassen i SymPy behandler vektorer anderledes og ikke benyttes.

    Parametre
    ---------
    args: Vektorkoordinater

    Returnerer
    ---------
    m : Matrix
        Plotobjektet.

    Se også
    ---------
    - [SymPy: Matrix](https://docs.sympy.org/latest/modules/matrices/matrices.html)
    """
    return Matrix([*args])


if __name__ == "__main__":
    # a = plot_vector((0, 0), (5, 5), show=False, label="test")
    # b = plot_vector([4, 4], show=False)
    # c = plot_vector([(2, 3), (1, 1)], label="(2,3) og (1,1)", show=False)
    # plot_vector([(0, 0), (1, 1)],[(2, 3), (1, 1)])
    # (a + b + c).show()
    # print(a)
    # print(c)

    # d = plot_vector([5, 5, 5], label="hej", show=False)
    # e = plot_vector([1, 1, 1], Matrix([1, 2, 3]), label="matrix", show=False)
    # f = plot_vector([Matrix([0, 1, 1]), Matrix([1, 1, 0])], label=["matrix1", "matrix2"], show=False)
    # (d + e + f).show()

    # print(d)

    from sympy.abc import s, t

    a = Matrix([1, 2, 3])
    b = Matrix([1, 1, 1])
    line = a + t * b
    # plot3d_line(line,(t,0,10))
    # plot3d_line( line, b+t*a, (t,0,10))
    # plot3d_line((line,(t,0,20)),(b+t*a, (t,0,10)))
    # plot3d_line((line, (t, 0, 20), "hej"), (b + t * a, (t, 0, 10), "hej2"))

    c = Matrix([0, 0, 1])
    plane = a + t * b + s * c
    # plot3d_plane(plane, (t, 0, 10), (s, -10, 0))

    # plot3d_plane( plane , (t, 0, 10), (s, -10, 0))
    # plot3d_plane(plane, t*a + b + s * c, (t, 0, 10), (s, -10, 0))
    # plot3d_plane((plane,(t, 0, 10), (s, -10, 0)), (t*a + b + s * c, (t, 0, 10), (s, -10, 20)))
    # plot3d_plane((plane, (t, 0, 10), (s, -10, 0), "p1"), (t * a + b + s * c, (t, 0, 10), (s, -10, 20), "p2"))

    print(vector(3, 4))
