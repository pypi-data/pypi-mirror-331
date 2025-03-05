# tests/test_geometry.py

import numpy as np
from alphamorph.geometry import generate_point_cloud, distort_point_cloud, compute_centroid_and_radius

def test_generate_point_cloud():
    points = generate_point_cloud(num_points=100, radius=1)
    # Check that we have 100 points and each point is 2D.
    assert points.shape == (100, 2)
    # Check that points are roughly within the expected range.
    max_dist = np.max(np.linalg.norm(points, axis=1))
    assert max_dist <= 1.0

def test_distort_point_cloud():
    original = generate_point_cloud(num_points=100, radius=1)
    distorted = distort_point_cloud(original, noise_scale=0.1, num_bins=20)
    # Check that the distorted point cloud has the same shape as original.
    assert distorted.shape == original.shape
    # Check that the points have changed.
    assert not np.allclose(original, distorted)

def test_compute_centroid_and_radius():
    # Create a simple circular point cloud.
    theta = np.linspace(0, 2 * np.pi, 100)
    x = np.cos(theta)
    y = np.sin(theta)
    points = np.column_stack((x, y))
    centroid, radius = compute_centroid_and_radius(points)
    # For a unit circle, centroid should be close to (0, 0) and radius close to 1.
    np.testing.assert_allclose(centroid, [0, 0], atol=1e-2)
    np.testing.assert_allclose(radius, 1, atol=1e-2)
