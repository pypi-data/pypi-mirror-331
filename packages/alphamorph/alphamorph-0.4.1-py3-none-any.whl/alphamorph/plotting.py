# alphamorph/plotting.py

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

def plot_point_cloud(ax, points, title, color_list, hull_points=None, metrics_dict=None):
    ax.scatter(points[:, 0], points[:, 1], s=10, alpha=0.7, label='Points', color=color_list)
    if hull_points is not None:
        hull_points = np.vstack([hull_points, hull_points[0]])
        ax.plot(hull_points[:, 0], hull_points[:, 1], 'k-', lw=1, label='Convex Hull')
        ax.scatter(hull_points[:-1, 0], hull_points[:-1, 1], color='red', s=20, zorder=3, label='Hull Points')
    if metrics_dict:
        metrics_text = "\n".join([f"{key}: {value:.4f}" for key, value in metrics_dict.items()])
        ax.text(0.05, 0.95, metrics_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(facecolor='white', alpha=0.5))
    ax.set_title(title)
    ax.set_aspect('equal')
    ax.set_axis_off()


def create_color_list(points):
    x_coords = points[:, 0]
    x_min, x_max = np.min(x_coords), np.max(x_coords)
    normalized_x = (x_coords - x_min) / (x_max - x_min)
    colormap = cm.get_cmap('viridis')
    colors = np.array([colormap(value) for value in normalized_x])
    return colors
