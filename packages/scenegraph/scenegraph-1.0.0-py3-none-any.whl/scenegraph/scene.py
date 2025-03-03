"""
Base description of graph of objects in space
"""
from dataclasses import dataclass, field
from typing import List, Union

import numpy as np

from .shape import Shape
from .topo.graph import Graph
from .transfo import Scaling, Transfo, Translation


@dataclass
class ScNode:
    """Node/Graph for shapes in space
    """
    shape: Union[Shape, str] = None
    """Actual geometry (or ref to def) for that node.
    """

    transfos: List[Transfo] = field(default_factory=list)
    """Set of transformations associated to this node.
    
    Transfo are applied from first to last.
    """

    meta: dict = field(default_factory=dict)
    """Meta data associated to this node.
    
    Only simple python objects are allowed (for io json)
    """

    def transfo(self):
        """Concatenate all transformations for this node.

        Returns:
            (np.array)
        """
        tr_loc = np.identity(4)
        for transfo in self.transfos:
            tr_loc = transfo.matrix() @ tr_loc

        return tr_loc

    def add_transfo(self, transfo):
        """Add new transformation

        Args:
            transfo (Transfo): transfo to append (will be applied last)

        Returns:
            None
        """
        self.transfos.append(transfo)

    def get_transfo(self, name):
        """Access a transfo by its name.

        Raises: KeyError if no transfo by that name can be found.

        Args:
            name (str): name of transfo (must have been previously defined in transfo)

        Returns:
            (Transfo): ref to first transfo with that name in list of transformations
        """
        for tr in self.transfos:
            try:
                if tr.name == name:
                    return tr
            except AttributeError:
                pass

        raise KeyError(f"no transfo with that name '{name}' in the list")

    def translate(self, dx, dy, dz):
        """Append translation to actual transformations

        Args:
            dx (float): displacement along Ox
            dy (float): displacement along Oy
            dz (float): displacement along Oz

        Returns:
            None
        """
        self.add_transfo(Translation(vec=np.array([dx, dy, dz])))

    def scale(self, sx, sy, sz):
        """Append scaling to actual transformations

        Args:
            sx (float): scaling along Ox
            sy (float): scaling along Oy
            sz (float): scaling along Oz

        Returns:
            None
        """
        self.add_transfo(Scaling(vec=np.array([sx, sy, sz])))


class Scene:
    def __init__(self):
        self._graph = Graph()
        self._nodes = {}
        self._defs = {}

    def node(self, nid):
        """Retrieve node associated with vertex

        Args:
            nid (int): id of vertex

        Returns:
            (ScNode)
        """
        return self._nodes[nid]
    
    def vertices(self):
        return self._graph.vertices()

    def nodes(self):
        """Iterate on all nodes in the scene, no particular order.

        Returns:
            (iter of (int, ScNode)): vid, node
        """
        for vid in self._graph.vertices():
            yield vid, self._nodes[vid]

    def add(self, node, nid=None, pid=None):
        """Add new node in the graph

        Args:
            node (ScNode): object containing data for this node
            nid (int|None): id to use for node, create one if None
            pid (int|None): id of parent or None if top level vertex

        Returns:
            (int): id used for vertex
        """
        nid = self._graph.add_vertex(nid)
        self._nodes[nid] = node
        if pid is not None:
            eid = self._graph.add_edge(pid, nid)

        return nid

    def add_def(self, obj, oid=None):
        """Store any object in scene as def.

        Raises: KeyError if oid already used

        Args:
            oid (str): id to use to later access this object
            obj (Shape):

        Returns:
            (str): id used to store object
        """
        if oid is None:
            ind = len(self._defs)
            while f"obj_{ind:03d}" in self._defs:
                ind += 1

            oid = f"obj_{ind:03d}"

        self._defs[oid] = obj

        return oid

    def shape(self, nid):
        """Shape associated to given node.

        Args:
            nid (int): id of vertex

        Returns:
            (Shape): dereferenced (if needed) instance of shape
        """
        node = self._nodes[nid]
        if isinstance(node.shape, str):  # def
            shp = self._defs[node.shape]
        else:
            shp = node.shape

        return shp

    def shape_abs(self, nid):
        """Copy of shape associated to given node with absolute position

        Args:
            nid (int): id of vertex

        Returns:
            (Shape): copy with transformations applied
        """
        shp = self.shape(nid).copy()
        shp.apply(self.transfo(nid, absolute=True))
        return shp

    def meta(self, nid, name, default=None):
        """Get meta property associated to node.

        This function will explore ancestors to find the first defined meta
        if necessary.

        Args:
            name (str): name of property
            default (any): in case no meta is defined for any parent

        Returns:
            (any)
        """
        node = self._nodes[nid]
        try:
            return node.meta[name]
        except KeyError:
            try:
                pid, = self._graph.in_neighbors(nid)
                return self.meta(pid, name, default)
            except ValueError:
                return default

    def transfo(self, nid, absolute=False):
        """Transformation associated to a node.

        Args:
            nid (int): id of node
            absolute (bool): whether transfo use ancestors

        Returns:
            (np.array)
        """
        node = self._nodes[nid]
        tr_loc = node.transfo()

        if absolute:
            try:
                pid, = self._graph.in_neighbors(nid)
                tr_parent = self.transfo(pid, absolute)
                tr_loc = tr_parent @ tr_loc
            except ValueError:
                pass

        return tr_loc

    def merge(self, other):
        """Merge another scene in this one.

        Args:
            other (Scene): other scene to merge (no copy of nodes)

        Returns:
            (None): merge in place
        """
        trans_vid, trans_eid = self._graph.extend(other._graph)
        self._defs.update(other._defs)  # potential risk of duplication, to check?
        for oid, node in other._nodes.items():
            self._nodes[trans_vid[oid]] = node

    def __iadd__(self, other):
        self.merge(other)
        return self

    def breadth_first(self, nid):
        """Traverse scene down from nid.

        Args:
            nid (int): vid of node to use as upper ancestor

        Returns:
            (iter of int)
        """
        front = [nid]
        while front:
            vid = front.pop(0)
            yield vid
            front.extend(self._graph.out_neighbors(vid))
