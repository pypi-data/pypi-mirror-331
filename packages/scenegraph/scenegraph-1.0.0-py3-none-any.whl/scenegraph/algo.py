"""
Simple algo on scenegraph
"""
import numpy as np


def bounding_box(scene, nid=None):
    """Bounding box of node and all its descendants.

    Args:
        scene (Scene): scenegraph
        nid (int|Noe): id of root vertex, if None will use all nodes in scene

    Returns:
        (np.array, np.array): (xmin, ymin, zmin), (xmax, ymax, zmax)
    """
    if nid is None:
        vids = list(scene.vertices())
    else:
        vids = list(scene.breadth_first(nid))

    pts = []
    for vid in vids:
        mesh = scene.shape(vid)
        if mesh is not None:
            mesh = mesh.copy()
            tr_abs = scene.transfo(vid, absolute=True)
            mesh.apply(tr_abs)
            pts.extend(mesh.points())

    pts = np.array(pts)
    return pts.min(axis=0, initial=np.inf), pts.max(axis=0, initial=-np.inf)
