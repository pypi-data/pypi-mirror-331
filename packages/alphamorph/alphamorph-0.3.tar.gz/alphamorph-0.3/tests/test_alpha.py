# tests/test_alpha.py

import numpy as np
from alphamorph.alpha import compute_alpha_shape, generate_landmark_correspondences


def test_compute_alpha_shape():
    # Generate a set of points in a circle.
    theta = np.linspace(0, 2 * np.pi, 200)
    x = np.cos(theta)
    y = np.sin(theta)
    points = np.column_stack((x, y))

    # Use a reasonable alpha to get a boundary.
    indices, boundary_points = compute_alpha_shape(points, alpha=0.5)
    # Check that the boundary has a reasonable number of points.
    assert len(indices) > 0
    assert boundary_points.shape[1] == 2


def test_generate_landmark_correspondences():
    # Create simple convex hull points.
    convex_hull_points = np.array([[1, 0], [0, 1], [-1, 0], [0, -1]])
    centroid = np.array([0, 0])
    radius = 2
    source, target = generate_landmark_correspondences(convex_hull_points, centroid, radius)
    # Ensure that the target points lie on the circle of radius 2.
    distances = np.linalg.norm(target - centroid, axis=1)
    np.testing.assert_allclose(distances, np.full(distances.shape, radius), atol=1e-5)
