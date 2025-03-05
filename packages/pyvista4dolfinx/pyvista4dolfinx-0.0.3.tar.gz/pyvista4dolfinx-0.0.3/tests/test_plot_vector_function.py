import dolfinx
from mpi4py import MPI

from pyvista4dolfinx import plot

import pytest
from tests import show_or_screenshot_or_nothing, create_dummy_vectorfield


triangle = dolfinx.mesh.CellType.triangle
quad = dolfinx.mesh.CellType.quadrilateral
tetra = dolfinx.mesh.CellType.tetrahedron
hex = dolfinx.mesh.CellType.hexahedron


@pytest.mark.parametrize(
    "cell_type, family",
    [
        (triangle, "Lagrange"),
        (triangle, "DG"),
        (quad, "Lagrange"),
        (triangle, "N1curl"),
        (triangle, "RT"),
        (quad, "RTCF"),
    ],
)
@pytest.mark.parametrize("degree", [1, 4])
@pytest.mark.parametrize("warp", [False, True, "vec"])
def test_vector_function_2D(cell_type, family, degree, warp):
    mesh = dolfinx.mesh.create_unit_square(MPI.COMM_WORLD, 10, 10, cell_type=cell_type)

    u = create_dummy_vectorfield(mesh, family, degree)

    if type(warp) == str:
        warp = u

    plotter = plot(u, warp=warp, clear_plotter=True)
    show_or_screenshot_or_nothing(plotter)
