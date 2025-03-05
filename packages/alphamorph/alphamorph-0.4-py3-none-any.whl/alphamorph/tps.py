# alphamorph/tps.py

import numpy as np
from scipy.spatial.distance import cdist

def compute_tps_parameters(source_points, target_points, reg=0.0):
    """
    Computes TPS parameters from corresponding source and target landmarks.
    """
    N = source_points.shape[0]
    dists = cdist(source_points, source_points, 'euclidean')
    with np.errstate(divide='ignore', invalid='ignore'):
        K = np.where(dists == 0, 0, dists ** 2 * np.log(dists ** 2))
    K += reg * np.eye(N)
    P = np.hstack([np.ones((N, 1)), source_points])
    L = np.zeros((N + 3, N + 3))
    L[:N, :N] = K
    L[:N, N:] = P
    L[N:, :N] = P.T
    Y = np.zeros((N + 3, 2))
    Y[:N, :] = target_points
    params = np.linalg.solve(L, Y)
    weights = params[:N, :]
    affine = params[N:, :]
    return weights, affine


def tps_transform_to_circle(points, centroid, target_radius, tps_params):
    """
    Applies a TPS transformation and then warps the overall shape so that its envelope is circular.
    """
    N = points.shape[0]
    ones = np.ones((N, 1))
    points_aug = np.hstack([ones, points])
    affine_transformed = points_aug.dot(tps_params['affine'])
    control_points = tps_params['control_points']
    weights = tps_params['weights']
    diff = points[:, np.newaxis, :] - control_points[np.newaxis, :, :]
    r_vals = np.linalg.norm(diff, axis=2)
    with np.errstate(divide='ignore', invalid='ignore'):
        U = np.where(r_vals == 0, 0, r_vals ** 2 * np.log(r_vals ** 2))
    tps_warp = U.dot(weights)
    transformed_points = affine_transformed + tps_warp

    centroid = np.array(centroid)
    directions = transformed_points - centroid
    current_radii = np.linalg.norm(directions, axis=1)
    angles = np.arctan2(directions[:, 1], directions[:, 0])
    max_current_radius = np.max(current_radii)
    scale_factor = target_radius / max_current_radius if max_current_radius != 0 else 1.0
    new_radii = current_radii * scale_factor
    warped_points = centroid + np.column_stack((new_radii * np.cos(angles), new_radii * np.sin(angles)))
    return warped_points
