# alphamorph/geometry.py

import numpy as np

def generate_point_cloud(num_points=200, radius=1):
    angles = np.random.uniform(0, 2 * np.pi, num_points)
    radii = np.sqrt(np.random.uniform(0, radius ** 2, num_points))
    x = radii * np.cos(angles)
    y = radii * np.sin(angles)
    return np.column_stack((x, y))


def distort_point_cloud(original_points, noise_scale=0.3, num_bins=100):
    # Compute the center of the point cloud.
    center = np.mean(original_points, axis=0)
    shifted = original_points - center
    angles = np.arctan2(shifted[:, 1], shifted[:, 0])
    angles = np.mod(angles, 2 * np.pi)  # Ensure angles are in [0, 2*pi)
    radii = np.hypot(shifted[:, 0], shifted[:, 1])

    # Estimate the original contour by binning the angles.
    bins = np.linspace(0, 2 * np.pi, num_bins + 1)
    bin_centers = (bins[:-1] + bins[1:]) / 2
    orig_boundary = np.zeros(num_bins)

    for i in range(num_bins):
        mask = (angles >= bins[i]) & (angles < bins[i + 1])
        if np.any(mask):
            orig_boundary[i] = np.max(radii[mask])
        else:
            orig_boundary[i] = np.nan

    valid = ~np.isnan(orig_boundary)
    if not np.all(valid):
        orig_boundary = np.interp(bin_centers, bin_centers[valid], orig_boundary[valid])

    noise = noise_scale * np.random.uniform(-1, 1, num_bins)
    noisy_boundary = orig_boundary + noise
    noisy_boundary = np.clip(noisy_boundary, 0.01, None)

    extended_angles = np.concatenate([bin_centers, [2 * np.pi]])
    extended_orig = np.concatenate([orig_boundary, [orig_boundary[0]]])
    extended_noisy = np.concatenate([noisy_boundary, [noisy_boundary[0]]])

    orig_boundary_interp = np.interp(angles, extended_angles, extended_orig)
    noisy_boundary_interp = np.interp(angles, extended_angles, extended_noisy)

    eps = 1e-8
    ratio = radii / (orig_boundary_interp + eps)
    new_radii = ratio * noisy_boundary_interp

    new_x = new_radii * np.cos(angles) + center[0]
    new_y = new_radii * np.sin(angles) + center[1]

    return np.column_stack((new_x, new_y))


def compute_centroid_and_radius(points):
    centroid = np.mean(points, axis=0)
    distances = np.linalg.norm(points - centroid, axis=1)
    radius = np.max(distances)
    return centroid, radius
