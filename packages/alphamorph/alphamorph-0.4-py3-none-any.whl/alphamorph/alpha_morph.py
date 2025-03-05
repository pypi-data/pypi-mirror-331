import numpy as np
import matplotlib.pyplot as plt
import alphashape
from scipy.spatial import cKDTree
from scipy.spatial.distance import cdist
import matplotlib.cm as cm



def generate_point_cloud(num_points=200, radius=1):
    angles = np.random.uniform(0, 2 * np.pi, num_points)
    radii = np.sqrt(np.random.uniform(0, radius ** 2, num_points))
    x = radii * np.cos(angles)
    y = radii * np.sin(angles)
    return np.column_stack((x, y))


# Function to generate a distorted (noisy) boundary of a circle.
def distort_point_cloud(original_points, noise_scale=0.3, num_bins=100):
    # 1. Compute the center of the point cloud.
    center = np.mean(original_points, axis=0)
    # 2. Convert to polar coordinates relative to the center.
    shifted = original_points - center
    angles = np.arctan2(shifted[:, 1], shifted[:, 0])
    # Ensure angles are in [0, 2*pi)
    angles = np.mod(angles, 2 * np.pi)
    radii = np.hypot(shifted[:, 0], shifted[:, 1])

    # 3. Estimate the original contour by binning the angles.
    bins = np.linspace(0, 2 * np.pi, num_bins + 1)
    bin_centers = (bins[:-1] + bins[1:]) / 2
    orig_boundary = np.zeros(num_bins)

    for i in range(num_bins):
        # Find points whose angles fall in the current bin.
        mask = (angles >= bins[i]) & (angles < bins[i + 1])
        if np.any(mask):
            # Maximum radius in this bin approximates the boundary.
            orig_boundary[i] = np.max(radii[mask])
        else:
            # In case a bin has no points, we'll fill it later.
            orig_boundary[i] = np.nan

    # Fill any bins with no points by interpolating between neighboring bins.
    # Identify bins with valid values.
    valid = ~np.isnan(orig_boundary)
    if not np.all(valid):
        orig_boundary = np.interp(bin_centers, bin_centers[valid], orig_boundary[valid])

    # 4. Create a noisy version of the boundary.
    noise = noise_scale * np.random.uniform(-1, 1, num_bins)
    noisy_boundary = orig_boundary + noise
    # Prevent negative or zero radii.
    noisy_boundary = np.clip(noisy_boundary, 0.01, None)

    # To allow interpolation for any angle, extend the arrays to wrap around.
    extended_angles = np.concatenate([bin_centers, [2 * np.pi]])
    extended_orig = np.concatenate([orig_boundary, [orig_boundary[0]]])
    extended_noisy = np.concatenate([noisy_boundary, [noisy_boundary[0]]])

    # 5. For each original point, get the original and noisy boundary radii via interpolation.
    orig_boundary_interp = np.interp(angles, extended_angles, extended_orig)
    noisy_boundary_interp = np.interp(angles, extended_angles, extended_noisy)

    # 6. For each point, compute its relative radial position and map it to the noisy contour.
    # (Avoid division by zero by using a small epsilon.)
    eps = 1e-8
    ratio = radii / (orig_boundary_interp + eps)
    new_radii = ratio * noisy_boundary_interp

    # 7. Convert the modified polar coordinates back to Cartesian coordinates.
    new_x = new_radii * np.cos(angles) + center[0]
    new_y = new_radii * np.sin(angles) + center[1]

    return np.column_stack((new_x, new_y))
def compute_alpha_shape(points, alpha):
    """
    Compute the alpha shape of a point cloud and return the boundary points and indices.
    """
    # Compute the alpha shape
    alpha_shape = alphashape.alphashape(points, alpha)

    # Extract boundary points from the alpha shape
    boundary_coords = np.array(alpha_shape.exterior.coords)

    # Find indices of boundary points in the original point cloud
    tree = cKDTree(points)  # Create a spatial tree for fast lookup
    indices = tree.query(boundary_coords, k=1)[1]  # Get the nearest neighbor indices
    return indices, points[indices]


def plot_point_cloud(ax, points, title, color_list, hull_points=None, metrics_dict=None):
    """Plot the point cloud on the given axis and optionally display the convex hull and metrics."""
    ax.scatter(points[:, 0], points[:, 1], s=10, alpha=0.7, label='Points', color=color_list)

    if hull_points is not None:
        # Plot the convex hull lines
        hull_points = np.vstack([hull_points, hull_points[0]])  # Close the hull
        ax.plot(hull_points[:, 0], hull_points[:, 1], 'k-', lw=1, label='Convex Hull')
        # Plot hull points in red
        ax.scatter(hull_points[:-1, 0], hull_points[:-1, 1], color='red', s=20, zorder=3, label='Hull Points')

    if metrics_dict:
        metrics_text = "\n".join([f"{key}: {value:.4f}" for key, value in metrics_dict.items()])
        ax.text(0.05, 0.95, metrics_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(facecolor='white', alpha=0.5))

    ax.set_title(title)
    ax.set_aspect('equal')
    ax.set_axis_off()





def create_color_list(points):
    """
    Assign colors to points based on their x-coordinate using a gradient.
    Args:
        points (numpy.ndarray): Nx2 or Nx3 array of 2D/3D points.
    Returns:
        list: A list of RGB colors corresponding to each point.
    """
    x_coords = points[:, 0]  # Extract x-coordinates
    x_min, x_max = np.min(x_coords), np.max(x_coords)  # Find the range of x
    normalized_x = (x_coords - x_min) / (x_max - x_min)  # Normalize x to [0, 1]

    # Map normalized x to a colormap (e.g., viridis)
    colormap = cm.get_cmap('viridis')  # You can change the colormap here
    colors = np.array([colormap(value) for value in normalized_x])  # Map to RGBA values

    return colors



def compute_centroid_and_radius(points):
    """
    Compute the centroid and the radius of a 2D point cloud.
    The radius is defined as the mean distance of the points from the centroid.

    Parameters:
        points (np.ndarray): A Nx2 numpy array of 2D coordinates.

    Returns:
        tuple: (centroid, radius) where centroid is a (2,) numpy array and radius is a float.
    """
    centroid = np.mean(points, axis=0)
    distances = np.linalg.norm(points - centroid, axis=1)
    radius = np.max(distances)

    return centroid, radius


def tps_transform_to_circle(points, centroid, target_radius, tps_params):
    """
    Transforms a set of 2D points using a thin-plate spline (TPS) transformation and then warps
    the overall shape so that its envelope is circular. This is achieved by:
      1. Applying the TPS (affine + non-affine warping) transformation.
      2. Converting the transformed points to polar coordinates relative to the given centroid.
      3. Scaling the radial coordinate so that the furthest point lies exactly at the target radius,
         while interior points are scaled proportionally. The angular positions are preserved.

    Parameters:
        points (np.ndarray): Array of shape (N, 2) representing the input points.
        centroid (array-like): A 2-element array or list representing the center of the target circle.
        target_radius (float): The target radius that the outer envelope of the point cloud should match.
        tps_params (dict): Dictionary with TPS parameters including:
            - 'affine': A (3, 2) numpy array for the affine component.
            - 'control_points': A (K, 2) numpy array of TPS control points.
            - 'weights': A (K, 2) numpy array of TPS weights.

    Returns:
        np.ndarray: Array of shape (N, 2) with the transformed points forming a circular envelope.
    """
    # === Step 1: TPS Transformation ===
    # Apply the affine part.
    N = points.shape[0]
    ones = np.ones((N, 1))
    points_aug = np.hstack([ones, points])  # Shape: (N, 3)
    affine_transformed = points_aug.dot(tps_params['affine'])  # Shape: (N, 2)

    # Compute the non-affine TPS warping.
    control_points = tps_params['control_points']  # Shape: (K, 2)
    weights = tps_params['weights']  # Shape: (K, 2)

    # Compute distances between each point and each control point.
    diff = points[:, np.newaxis, :] - control_points[np.newaxis, :, :]  # (N, K, 2)
    r_vals = np.linalg.norm(diff, axis=2)  # (N, K)

    # Evaluate the radial basis function U(r) = r^2 * log(r^2), with U(0)=0.
    with np.errstate(divide='ignore', invalid='ignore'):
        U = np.where(r_vals == 0, 0, r_vals ** 2 * np.log(r_vals ** 2))

    tps_warp = U.dot(weights)  # (N, 2)

    # Combined TPS transformation.
    transformed_points = affine_transformed + tps_warp

    # === Step 2: Warping to a Circular Envelope ===
    # Convert the TPS-transformed points to polar coordinates relative to the centroid.
    centroid = np.array(centroid)
    directions = transformed_points - centroid
    current_radii = np.linalg.norm(directions, axis=1)

    # Prevent division by zero for points exactly at the centroid.
    current_radii_safe = np.where(current_radii == 0, 1, current_radii)
    angles = np.arctan2(directions[:, 1], directions[:, 0])

    # Determine a uniform scaling factor so that the maximum radius becomes the target radius.
    max_current_radius = np.max(current_radii)
    if max_current_radius == 0:
        scale_factor = 1.0
    else:
        scale_factor = target_radius / max_current_radius

    # Scale each point's radius while preserving its angle.
    new_radii = current_radii * scale_factor

    # Convert back to Cartesian coordinates.
    warped_points = centroid + np.column_stack((new_radii * np.cos(angles), new_radii * np.sin(angles)))

    return warped_points


def compute_tps_parameters(source_points, target_points, reg=0.0):
    """
    Computes TPS parameters from corresponding source and target landmarks.

    Parameters:
        source_points (np.ndarray): Array of shape (N, 2) with source landmark coordinates.
        target_points (np.ndarray): Array of shape (N, 2) with target landmark coordinates.
        reg (float): Regularization parameter. Default is 0.0.

    Returns:
        weights (np.ndarray): Non-affine weights (N, 2).
        affine (np.ndarray): Affine transformation parameters (3, 2).
    """
    N = source_points.shape[0]

    # Compute pairwise distances between source points.
    dists = cdist(source_points, source_points, 'euclidean')

    # Compute K matrix using TPS kernel: U(r) = r^2 * log(r^2), with U(0)=0.
    with np.errstate(divide='ignore', invalid='ignore'):
        K = np.where(dists == 0, 0, dists ** 2 * np.log(dists ** 2))

    # Add regularization.
    K += reg * np.eye(N)

    # Construct matrix P (N x 3) with a column of ones and the source coordinates.
    P = np.hstack([np.ones((N, 1)), source_points])

    # Build the full system matrix L.
    L = np.zeros((N + 3, N + 3))
    L[:N, :N] = K
    L[:N, N:] = P
    L[N:, :N] = P.T  # The affine constraints.

    # Right-hand side: target points for the first N rows, zeros for affine part.
    Y = np.zeros((N + 3, 2))
    Y[:N, :] = target_points

    # Solve the linear system.
    params = np.linalg.solve(L, Y)
    weights = params[:N, :]
    affine = params[N:, :]

    return weights, affine


def generate_landmark_correspondences(convex_hull_points, centroid, radius):
    """
    Generates target landmark points for TPS computation by projecting each convex hull
    point onto the circle defined by centroid and radius.

    Parameters:
        convex_hull_points (np.ndarray): Array of shape (N, 2) with convex hull vertices.
        centroid (array-like): The center of the target circle.
        radius (float): The target circle's radius.

    Returns:
        source_points (np.ndarray): Same as convex_hull_points.
        target_points (np.ndarray): Array of shape (N, 2) with points on the circle.
    """
    convex_hull_points = np.array(convex_hull_points)
    centroid = np.array(centroid)

    # Compute direction vectors and angles.
    directions = convex_hull_points - centroid
    angles = np.arctan2(directions[:, 1], directions[:, 0])

    # Compute target points on the circle.
    target_points = centroid + radius * np.column_stack((np.cos(angles), np.sin(angles)))

    return convex_hull_points, target_points



def main():
    # seed 42
    np.random.seed(42)
    original_points = generate_point_cloud(num_points=2000)
    color_list = create_color_list(original_points)
    noisy_points = distort_point_cloud(original_points, noise_scale=0.2, num_bins=15)
    centroid, radius = compute_centroid_and_radius(noisy_points)

    #### TPS optimization
    alpha = 2.5   # 3.5
    original_hull_indices, original_hull_points = compute_alpha_shape(original_points, alpha)
    reconstructed_hull_indices, reconstructed_hull_points = compute_alpha_shape(noisy_points, alpha)
    source_landmarks, target_landmarks = generate_landmark_correspondences(reconstructed_hull_points, centroid, radius)
    weights, affine = compute_tps_parameters(source_landmarks, target_landmarks, reg=1e-5)
    tps_params = {
        'affine': affine,
        'control_points': source_landmarks,
        'weights': weights
    }
    new_points = tps_transform_to_circle(noisy_points, centroid, radius, tps_params)
    new_points_hull_points = new_points[reconstructed_hull_indices]
    # Plotting the results
    fig, axes = plt.subplots(1, 3, figsize=(12, 6))  # 1 row, 3 columns
    plot_point_cloud(axes[0], original_points, 'Original', color_list=color_list, hull_points=original_hull_points)
    plot_point_cloud(axes[1], noisy_points, 'Noisy', color_list=color_list, hull_points=reconstructed_hull_points)
    plot_point_cloud(axes[2], new_points, 'Noisy + Alphamorph', color_list=color_list, hull_points=new_points_hull_points,)
    plt.tight_layout()  # Adjust layout to prevent overlap
    plt.savefig(f'fit_2d_shape_from_slidetags_feb2025_package_image.png')
    plt.show()


if __name__ == "__main__":
    main()
