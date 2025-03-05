# tests/test_tps.py

import numpy as np
from alphamorph.tps import compute_tps_parameters, tps_transform_to_circle


def test_compute_tps_parameters():
    # Define a simple correspondence: four points mapping to a scaled version on a circle.
    source_points = np.array([[1, 0], [0, 1], [-1, 0], [0, -1]])
    centroid = np.array([0, 0])
    radius = 2
    # Map each source point to the circle.
    target_points = centroid + radius * (source_points / np.linalg.norm(source_points, axis=1, keepdims=True))

    weights, affine = compute_tps_parameters(source_points, target_points, reg=1e-5)
    # Check the dimensions.
    assert weights.shape == (source_points.shape[0], 2)
    assert affine.shape == (3, 2)


def test_tps_transform_to_circle():
    # Create a simple test where the points are already roughly in a circular shape.
    theta = np.linspace(0, 2 * np.pi, 50)
    x = np.cos(theta) * 1.5  # not exactly on the unit circle
    y = np.sin(theta) * 1.5
    points = np.column_stack((x, y))
    centroid = np.array([0, 0])
    target_radius = 2

    # For testing, we use source landmarks from the current points and map them to the circle.
    source_landmarks = points.copy()
    target_landmarks = centroid + target_radius * (points / np.linalg.norm(points, axis=1, keepdims=True))

    weights, affine = compute_tps_parameters(source_landmarks, target_landmarks, reg=1e-5)
    tps_params = {
        'affine': affine,
        'control_points': source_landmarks,
        'weights': weights
    }

    transformed = tps_transform_to_circle(points, centroid, target_radius, tps_params)
    # Check that the outer boundary of the transformed points is at the target radius.
    distances = np.linalg.norm(transformed - centroid, axis=1)
    max_distance = np.max(distances)
    np.testing.assert_allclose(max_distance, target_radius, atol=1e-2)
