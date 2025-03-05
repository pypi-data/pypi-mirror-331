import dolfinx
from mpi4py import MPI

from pyvista4dolfinx import plot

import pytest
from tests import (
    show_or_screenshot_or_nothing,
    create_dummy_vectorfield,
    create_dummy_meshtags,
)


triangle = dolfinx.mesh.CellType.triangle
quad = dolfinx.mesh.CellType.quadrilateral
tetra = dolfinx.mesh.CellType.tetrahedron
hex = dolfinx.mesh.CellType.hexahedron


@pytest.mark.parametrize("codim", [0, 1])
def test_meshtags_1D(codim):
    mesh = dolfinx.mesh.create_unit_interval(MPI.COMM_WORLD, 10)
    meshtags = create_dummy_meshtags(mesh, codim)

    plotter = plot(meshtags, mesh=mesh, clear_plotter=True)
    show_or_screenshot_or_nothing(plotter)


@pytest.mark.parametrize("cell_type", [triangle, quad])
@pytest.mark.parametrize("codim", [0, 1, 2])
def test_meshtags_2D(cell_type, codim):
    mesh = dolfinx.mesh.create_unit_square(MPI.COMM_WORLD, 10, 10, cell_type=cell_type)
    meshtags = create_dummy_meshtags(mesh, codim)

    plotter = plot(meshtags, mesh=mesh, clear_plotter=True)
    show_or_screenshot_or_nothing(plotter)


@pytest.mark.parametrize("cell_type", [tetra, hex])
@pytest.mark.parametrize("codim", [0, 1, 2, 3])
def test_meshtags_3D(cell_type, codim):
    mesh = dolfinx.mesh.create_unit_cube(MPI.COMM_WORLD, 3, 3, 3, cell_type=cell_type)
    meshtags = create_dummy_meshtags(mesh, codim)

    plotter = plot(meshtags, mesh=mesh, clear_plotter=True)
    show_or_screenshot_or_nothing(plotter)
