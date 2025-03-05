# tests/test_plotting.py

import numpy as np
import matplotlib.pyplot as plt
from alphamorph.plotting import plot_point_cloud, create_color_list

def test_create_color_list():
    # Create some dummy points.
    points = np.array([[0, 0], [1, 1], [2, 2]])
    colors = create_color_list(points)
    # Check that a color is generated for each point.
    assert len(colors) == len(points)

def test_plot_point_cloud():
    # Create a dummy point cloud.
    points = np.random.rand(10, 2)
    colors = create_color_list(points)
    fig, ax = plt.subplots()
    # This should run without errors.
    plot_point_cloud(ax, points, 'Test Plot', colors)
    plt.close(fig)
