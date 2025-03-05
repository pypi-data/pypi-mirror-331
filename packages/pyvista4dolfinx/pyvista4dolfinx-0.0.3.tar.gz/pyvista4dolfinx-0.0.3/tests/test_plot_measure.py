import dolfinx
from mpi4py import MPI
import ufl

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


def test_measure_1D():
    mesh = dolfinx.mesh.create_unit_interval(MPI.COMM_WORLD, 10)
    meshtags = create_dummy_meshtags(mesh)
    dx = ufl.Measure("dx", domain=mesh, subdomain_data=meshtags, subdomain_id=1)

    plot(mesh, clear_plotter=True)
    plotter = plot(dx, mesh=mesh)
    show_or_screenshot_or_nothing(plotter)


@pytest.mark.parametrize("cell_type", [triangle, quad])
def test_measure_2D(cell_type):
    mesh = dolfinx.mesh.create_unit_square(MPI.COMM_WORLD, 10, 10, cell_type=cell_type)
    meshtags = create_dummy_meshtags(mesh)
    dx = ufl.Measure("dx", domain=mesh, subdomain_data=meshtags, subdomain_id=1)

    plot(mesh, clear_plotter=True)
    plotter = plot(dx, mesh=mesh)
    show_or_screenshot_or_nothing(plotter)


@pytest.mark.parametrize("cell_type", [tetra, hex])
def test_measure_3D(cell_type):
    mesh = dolfinx.mesh.create_unit_cube(MPI.COMM_WORLD, 3, 3, 3, cell_type=cell_type)
    meshtags = create_dummy_meshtags(mesh)
    dx = ufl.Measure("dx", domain=mesh, subdomain_data=meshtags, subdomain_id=1)

    plot(mesh, clear_plotter=True)
    plotter = plot(dx, mesh=mesh)
    show_or_screenshot_or_nothing(plotter)
