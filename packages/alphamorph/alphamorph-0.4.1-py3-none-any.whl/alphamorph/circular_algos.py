import numpy as np

# De-ellipsification tricks!


def pca_ellipse_to_circle(points):
    centroid = points.mean(axis=0)
    centered = points - centroid
    cov = np.cov(centered.T)
    eigvals, eigvecs = np.linalg.eig(cov)
    idx = np.argsort(eigvals)[::-1]
    eigvals = eigvals[idx]
    eigvecs = eigvecs[:, idx]
    scale_mat = np.diag(1.0 / np.sqrt(eigvals))
    transform = scale_mat @ eigvecs.T
    return centroid, transform


def apply_transform(points, centroid, transform):
    centered = points - centroid
    return (transform @ centered.T).T


def preserve_average_radius(points_original, points_flattened):
    orig_centroid = points_original.mean(axis=0)
    avg_rad_orig = np.mean(np.linalg.norm(points_original - orig_centroid, axis=1))
    flat_centroid = points_flattened.mean(axis=0)
    avg_rad_flat = np.mean(np.linalg.norm(points_flattened - flat_centroid, axis=1))
    if avg_rad_flat == 0:
        return 1.0
    scale_factor = avg_rad_orig / avg_rad_flat
    return scale_factor


# Putting it together
def ellipse_to_circle(points):
    centroid, T = pca_ellipse_to_circle(points)
    flattened = apply_transform(points, centroid, T)
    s = preserve_average_radius(points, flattened)
    flattened_rescaled = flattened * s
    return flattened_rescaled, (centroid, T, s)