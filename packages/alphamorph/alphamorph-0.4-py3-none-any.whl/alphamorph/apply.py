from alphamorph.geometry import compute_centroid_and_radius
from alphamorph.alpha import compute_alpha_shape, generate_landmark_correspondences
from alphamorph.tps import compute_tps_parameters, tps_transform_to_circle
from alphamorph.circular_algos import ellipse_to_circle

def alphamorph_apply(points, alpha=2.5, pca_mode=True):
    """
    Apply the full Alphamorph transformation to a set of points.

    Parameters:
        points (np.ndarray): A Nx2 array representing the input point cloud.
        alpha (float): Parameter for computing the alpha shape.

    Returns:
        new_points (np.ndarray): The transformed point cloud.
    """
    centroid, radius = compute_centroid_and_radius(points)
    _, reconstructed_hull_points = compute_alpha_shape(points, alpha)
    source_landmarks, target_landmarks = generate_landmark_correspondences(reconstructed_hull_points, centroid, radius)
    weights, affine = compute_tps_parameters(source_landmarks, target_landmarks, reg=1e-5)
    tps_params = {
        'affine': affine,
        'control_points': source_landmarks,
        'weights': weights
    }
    new_points = tps_transform_to_circle(points, centroid, radius, tps_params)
    # Update: extra step to de-ellipsify
    if pca_mode:
        new_points, _ = ellipse_to_circle(new_points)

    return new_points
