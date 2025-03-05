# alphamorph/alpha.py

import numpy as np
import alphashape
from scipy.spatial import cKDTree
from shapely.geometry import MultiPolygon, Polygon


def compute_alpha_shape(points, alpha):
    """
    Compute the alpha shape of a point cloud and return the boundary points and indices.
    """
    alpha_shape = alphashape.alphashape(points, alpha)
    if alpha_shape.geom_type == 'MultiPolygon':  # For especially difficult point clouds
        alpha_shape = max(alpha_shape.geoms, key=lambda p: p.area)
        boundary_coords = np.array(alpha_shape.exterior.coords)
    elif alpha_shape.geom_type == 'GeometryCollection':
        polygons = [geom for geom in alpha_shape.geoms if isinstance(geom, Polygon)]
        if not polygons:
            raise ValueError("No polygons found in the GeometryCollection")
        chosen_polygon = max(polygons, key=lambda p: p.area)
        boundary_coords = np.array(chosen_polygon.exterior.coords)
    else:  # Usual point cloud
        boundary_coords = np.array(alpha_shape.exterior.coords)
    tree = cKDTree(points)
    indices = tree.query(boundary_coords, k=1)[1]
    return indices, points[indices]


def generate_landmark_correspondences(convex_hull_points, centroid, radius):
    """
    Generates target landmark points for TPS computation by projecting each convex hull
    point onto the circle defined by centroid and radius.
    """
    convex_hull_points = np.array(convex_hull_points)
    centroid = np.array(centroid)
    directions = convex_hull_points - centroid
    angles = np.arctan2(directions[:, 1], directions[:, 0])
    target_points = centroid + radius * np.column_stack((np.cos(angles), np.sin(angles)))
    return convex_hull_points, target_points
