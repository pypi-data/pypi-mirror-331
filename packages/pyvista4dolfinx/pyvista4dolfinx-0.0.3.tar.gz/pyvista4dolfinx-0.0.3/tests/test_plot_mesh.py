import dolfinx
from mpi4py import MPI

from pyvista4dolfinx import plot

import pytest
from tests import show_or_screenshot_or_nothing, create_dummy_vectorfield


triangle = dolfinx.mesh.CellType.triangle
quad = dolfinx.mesh.CellType.quadrilateral
tetra = dolfinx.mesh.CellType.tetrahedron
hex = dolfinx.mesh.CellType.hexahedron


@pytest.mark.parametrize("warp", [False, True])
@pytest.mark.parametrize("show_partitioning", [False, True])
def test_mesh_1D(warp, show_partitioning):
    if warp and show_partitioning:
        pytest.skip("not implemented")

    mesh = dolfinx.mesh.create_unit_interval(MPI.COMM_WORLD, 10)

    if warp:
        warp = create_dummy_vectorfield(mesh, "Lagrange", degree=2)

    plotter = plot(
        mesh, warp=warp, show_partitioning=show_partitioning, clear_plotter=True
    )
    show_or_screenshot_or_nothing(plotter)


@pytest.mark.parametrize("cell_type", [triangle, quad])
@pytest.mark.parametrize("warp", [False])
@pytest.mark.parametrize("show_partitioning", [False, True])
def test_mesh_2D(cell_type, warp, show_partitioning):
    if warp and show_partitioning:
        pytest.skip("not implemented")

    mesh = dolfinx.mesh.create_unit_square(MPI.COMM_WORLD, 10, 10, cell_type=cell_type)

    if warp:
        warp = create_dummy_vectorfield(mesh, "Lagrange", degree=2)

    plotter = plot(
        mesh, warp=warp, show_partitioning=show_partitioning, clear_plotter=True
    )
    show_or_screenshot_or_nothing(plotter)


@pytest.mark.parametrize("cell_type", [tetra, hex])
@pytest.mark.parametrize("warp", [False, True])
@pytest.mark.parametrize("show_partitioning", [False, True])
def test_mesh_3D(cell_type, warp, show_partitioning):
    if warp and show_partitioning:
        pytest.skip("not implemented")

    mesh = dolfinx.mesh.create_unit_cube(MPI.COMM_WORLD, 3, 3, 3, cell_type=cell_type)

    if warp:
        warp = create_dummy_vectorfield(mesh, "Lagrange", degree=2)

    plotter = plot(
        mesh, warp=warp, show_partitioning=show_partitioning, clear_plotter=True
    )
    show_or_screenshot_or_nothing(plotter)
