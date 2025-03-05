# alphamorph/main.py

import numpy as np
import matplotlib.pyplot as plt
from alphamorph.geometry import generate_point_cloud, distort_point_cloud, compute_centroid_and_radius
from alphamorph.alpha import compute_alpha_shape, generate_landmark_correspondences
from alphamorph.tps import compute_tps_parameters, tps_transform_to_circle
from alphamorph.plotting import plot_point_cloud, create_color_list
# from alphamorph.circular_algos import ellipse_to_circle
from alphamorph.apply import alphamorph_apply


def main():
    np.random.seed(42)
    original_points = generate_point_cloud(num_points=2000)

    color_list = create_color_list(original_points)
    noisy_points = distort_point_cloud(original_points, noise_scale=0.2, num_bins=15)
    centroid, radius = compute_centroid_and_radius(noisy_points)


    # TPS optimization.
    alpha = 2.5  # Change alpha as needed.
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
    # new_points, _ = ellipse_to_circle(new_points)
    new_points_hull_points = new_points[reconstructed_hull_indices]

    # Plotting the results.
    fig, axes = plt.subplots(1, 3, figsize=(12, 6))
    plot_point_cloud(axes[0], original_points, 'Original', color_list=color_list, hull_points=original_hull_points)
    plot_point_cloud(axes[1], noisy_points, 'Noisy', color_list=color_list, hull_points=reconstructed_hull_points)
    plot_point_cloud(axes[2], new_points, 'Noisy + Alphamorph', color_list=color_list, hull_points=new_points_hull_points)
    plt.tight_layout()
    plt.savefig('alphamorph_example.png')
    plt.show()

if __name__ == "__main__":
    main()
