import dolfinx
from mpi4py import MPI

from pyvista4dolfinx import plot

import pytest
from tests import (
    show_or_screenshot_or_nothing,
    create_dummy_scalarfield,
    create_dummy_vectorfield,
)

triangle = dolfinx.mesh.CellType.triangle
quad = dolfinx.mesh.CellType.quadrilateral
tetra = dolfinx.mesh.CellType.tetrahedron
hex = dolfinx.mesh.CellType.hexahedron


@pytest.mark.parametrize(
    "cell_type, family", [(triangle, "Lagrange"), (triangle, "DG"), (quad, "Lagrange")]
)
@pytest.mark.parametrize("degree", [1, 4])
@pytest.mark.parametrize("warp", [False, True, "vec"])
@pytest.mark.parametrize("warpdegree", [1, 4])
def test_scalar_function_2D(cell_type, family, degree, warp, warpdegree):
    mesh = dolfinx.mesh.create_unit_square(MPI.COMM_WORLD, 10, 10, cell_type=cell_type)
    u = create_dummy_scalarfield(mesh, family, degree)

    if warp == "vec":
        warp = create_dummy_vectorfield(mesh, "Lagrange", warpdegree)

    plotter = plot(u, warp=warp, clear_plotter=True)
    show_or_screenshot_or_nothing(plotter)


@pytest.mark.parametrize("warp", [False, True])
def test_scalar_function_2D_DG0_CG2warp(warp):
    mesh = dolfinx.mesh.create_unit_square(MPI.COMM_WORLD, 10, 10, cell_type=triangle)
    u = create_dummy_scalarfield(mesh, "DG", 0)
    if warp:
        warp = create_dummy_vectorfield(mesh, "Lagrange", 1)
    plotter = plot(u, warp=warp, clear_plotter=True)
    show_or_screenshot_or_nothing(plotter)


@pytest.mark.parametrize(
    "cell_type, family", [(tetra, "Lagrange"), (tetra, "DG"), (hex, "Lagrange")]
)
@pytest.mark.parametrize("degree", [1, 4])
@pytest.mark.parametrize("warp", [False, True])
@pytest.mark.parametrize("warpdegree", [1, 4])
def test_scalar_function_3D(cell_type, family, degree, warp, warpdegree):
    mesh = dolfinx.mesh.create_unit_cube(MPI.COMM_WORLD, 3, 3, 3, cell_type=cell_type)
    u = create_dummy_scalarfield(mesh, family, degree)

    if warp:
        warp = create_dummy_vectorfield(mesh, "Lagrange", warpdegree)

    plotter = plot(u, warp=warp, clear_plotter=True)
    show_or_screenshot_or_nothing(plotter)
