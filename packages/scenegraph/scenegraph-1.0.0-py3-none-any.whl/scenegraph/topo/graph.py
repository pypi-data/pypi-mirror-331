from .id_dict import IdDict


class GraphError(Exception):
    """
    base class of all graph exceptions
    """


class InvalidEdge(GraphError, KeyError):
    """
    exception raised when a wrong edge id is provided
    """


class InvalidVertex(GraphError, KeyError):
    """
    exception raised when a wrong vertex id is provided
    """


class Graph:
    """Directed graph with multiple links

    in this implementation :

        - vertices are tuple of edge_in,edge_out
        - edges are tuple of source,target
    """

    def __init__(self, graph=None, idgenerator="set"):
        """constructor

        if graph is not none make a copy of the topological structure of graph
        (i.e. don't use the same id)

        :param graph: the graph to copy, default=None
        :type graph: Graph
        """
        self._vertices = IdDict(idgenerator=idgenerator)
        self._edges = IdDict(idgenerator=idgenerator)
        if graph is not None:
            self.extend(graph)

    # ##########################################################
    #
    # Graph concept
    #
    # ##########################################################
    def source(self, eid):
        """Retrieve the source of an edge

        Args:
            eid (int): id of edge

        Returns:
            (int): vid
        """
        try:
            return self._edges[eid][0]
        except KeyError:
            raise InvalidEdge(eid)

    def target(self, eid):
        """Retrieve the target of an edge

        Args:
            eid (int): id of edge

        Returns:
            (int): vid
        """
        try:
            return self._edges[eid][1]
        except KeyError:
            raise InvalidEdge(eid)

    def edge_vertices(self, eid):
        """Retrieve the source and target of an edge

        Args:
            eid (int): id of edge

        Returns:
            (int, int): src, tgt
        """
        try:
            return self._edges[eid]
        except KeyError:
            raise InvalidEdge(eid)

    def edge(self, source, target):
        """Find the matching edges with same source and same target

        return None if it don't succeed

        Args:
            source (int): vid
            target (int): vid

        Returns:
            (int): eid
        """
        link_in, link_out = self._vertices[source]
        for eid in link_in:
            if self._edges[eid][0] == target:
                return eid
        for eid in link_out:
            if self._edges[eid][1] == target:
                return eid
        return None

    def __contains__(self, vid):
        """Test whether a vertex belong to the graph, see `has_vertex`

        Args:
            vid (int):

        Returns:
            (bool)
        """
        return self.has_vertex(vid)

    def has_vertex(self, vid):
        """Test whether a vertex belong to the graph

        Args:
            vid (int):

        Returns:
            (bool)
        """
        return vid in self._vertices

    def has_edge(self, eid):
        """Test whether an edge belong to the graph

        Args:
            eid (int):

        Returns:
            (bool)
        """
        return eid in self._edges

    # ##########################################################
    #
    # Vertex List Graph Concept
    #
    # ##########################################################
    def vertices(self):
        """Iterator on vertices

        Returns:
            (iter of int)
        """
        return iter(self._vertices)

    def __iter__(self):
        """Magic function for `vertices`

        Returns:
            (iter of int)
        """
        return iter(self._vertices)

    def nb_vertices(self):
        """Total number of vertices

        Returns:
        """
        return len(self._vertices)

    def __len__(self):
        """Magic function for `nb_vertices`

        Returns:
            (int)
        """
        return self.nb_vertices()

    def in_neighbors(self, vid):
        """iterator on the neighbors of vid where edges are from neighbor to self

        Args:
            vid (int):

        Returns:
            (iter of int): iterator on vids
        """
        if vid not in self:
            raise InvalidVertex(vid)
        neighbors_list = [self.source(eid) for eid in self._vertices[vid][0]]
        return iter(set(neighbors_list))

    def out_neighbors(self, vid):
        """iterator on the neighbors of vid where edges are from self to neighbor

        Args:
            vid (int):

        Returns:
            (iter of int): iterator on vids
        """
        if vid not in self:
            raise InvalidVertex(vid)
        neighbors_list = [self.target(eid) for eid in self._vertices[vid][1]]
        return iter(set(neighbors_list))

    def neighbors(self, vid):
        """iterator on the neighbors of vid

        Args:
            vid (int):

        Returns:
            (iter of int): iterator on vids
        """
        neighbors_list = list(self.in_neighbors(vid))
        neighbors_list.extend(self.out_neighbors(vid))
        return iter(set(neighbors_list))

    def nb_in_neighbors(self, vid):
        """Number of in neighbors

        Args:
            vid (int):

        Returns:
            (int)
        """
        neighbors_set = list(self.in_neighbors(vid))
        return len(neighbors_set)

    def nb_out_neighbors(self, vid):
        """Number of out neighbors

        Args:
            vid (int):

        Returns:
            (int)
        """
        neighbors_set = list(self.out_neighbors(vid))
        return len(neighbors_set)

    def nb_neighbors(self, vid):
        """Number of neighbors

        Args:
            vid (int):

        Returns:
            (int)
        """
        neighbors_set = list(self.neighbors(vid))
        return len(neighbors_set)

    # ##########################################################
    #
    # Edge List Graph Concept
    #
    # ##########################################################
    def _iter_edges(self, vid):
        """
        internal function that perform 'edges' with vid not None
        """
        link_in, link_out = self._vertices[vid]
        for eid in link_in: yield eid
        for eid in link_out: yield eid

    def edges(self, vid=None):
        """Iterate on all edges connected to vertex

        Args:
            vid (int|None): Source vertex, iterate on all edges in graph if None

        Returns:
            (iter of int)
        """
        if vid is None:
            return iter(self._edges)
        if vid not in self:
            raise InvalidVertex(vid)
        return self._iter_edges(vid)

    def nb_edges(self, vid=None):
        """Number of edges connected to vertex

        Args:
            vid (int|None): Source vertex, total number of edges in graph if None

        Returns:
            (int)
        """
        if vid is None:
            return len(self._edges)
        if vid not in self:
            raise InvalidVertex(vid)
        return len(self._vertices[vid][0]) + len(self._vertices[vid][1])

    def in_edges(self, vid):
        """Iterate on all edges pointing toward vertex

        Args:
            vid (int): Target vertex

        Returns:
            (iter of int)
        """
        if vid not in self:
            raise InvalidVertex(vid)
        for eid in self._vertices[vid][0]: yield eid

    def out_edges(self, vid):
        """Iterate on all edges pointing outward vertex

        Args:
            vid (int): Source vertex

        Returns:
            (iter of int)
        """
        if vid not in self:
            raise InvalidVertex(vid)
        for eid in self._vertices[vid][1]: yield eid

    def nb_in_edges(self, vid):
        """Number of edges pointing toward vertex

        Args:
            vid (int): Target vertex

        Returns:
            (int)
        """
        if vid not in self:
            raise InvalidVertex(vid)
        return len(self._vertices[vid][0])

    def nb_out_edges(self, vid):
        """Number of edges pointing outward vertex

        Args:
            vid (int): Source vertex

        Returns:
            (int)
        """
        if vid not in self:
            raise InvalidVertex(vid)
        return len(self._vertices[vid][1])

    # ##########################################################
    #
    # Mutable Vertex Graph concept
    #
    # ##########################################################
    def add_vertex(self, vid=None):
        """Add new unconnected vertex to graph

        Args:
            vid (int|None): Id of vertex, create one if None

        Returns:
            (int): id used for vertex
        """
        return self._vertices.add((set(), set()), vid)

    def remove_vertex(self, vid):
        """Remove vertex from graph

        Also remove all edges attached to it.

        Args:
            vid (int):

        Returns:
            (None)
        """
        if vid not in self:
            raise InvalidVertex(vid)
        link_in, link_out = self._vertices[vid]
        for edge in list(link_in): self.remove_edge(edge)
        for edge in list(link_out): self.remove_edge(edge)
        del self._vertices[vid]

    def clear(self):
        """Clear graph from all vertices and edges

        Returns:
            (None)
        """
        self._edges.clear()
        self._vertices.clear()

    # ##########################################################
    #
    # Mutable Edge Graph concept
    #
    # ##########################################################
    def add_edge(self, sid, tid, eid=None):
        """Link two vertices together

        Args:
            sid (int): Id of vertex source
            tid (int): Id of vertex target
            eid (int|None): Id to use for edge, create one if None

        Returns:
            (int): id of edge
        """
        if sid not in self:
            raise InvalidVertex(sid)
        if tid not in self:
            raise InvalidVertex(tid)
        eid = self._edges.add((sid, tid), eid)
        self._vertices[sid][1].add(eid)
        self._vertices[tid][0].add(eid)
        return eid

    def remove_edge(self, eid):
        """Remove edge from graph

        Args:
            eid (int):

        Returns:
            (None)
        """
        if not self.has_edge(eid):
            raise InvalidEdge(eid)
        sid, tid = self._edges[eid]
        self._vertices[sid][1].remove(eid)
        self._vertices[tid][0].remove(eid)
        del self._edges[eid]

    def clear_edges(self):
        """Remove all edges from graph

        Returns:
            (None)
        """
        self._edges.clear()
        for vid, (in_edges, out_edges) in self._vertices.items():
            in_edges.clear()
            out_edges.clear()

    # ##########################################################
    #
    # Extend Graph concept
    #
    # ##########################################################
    def extend(self, graph):
        """Add other graph

        External graph will be added and new ids will be created

        Args:
            graph (Graph):  other graph to add

        Returns:
            (dict, dict): trans_vid, trans_eid
        """
        # vertex adding
        trans_vid = {}
        for vid in list(graph.vertices()):
            trans_vid[vid] = self.add_vertex()

        # edge adding
        trans_eid = {}
        for eid in list(graph.edges()):
            sid = trans_vid[graph.source(eid)]
            tid = trans_vid[graph.target(eid)]
            trans_eid[eid] = self.add_edge(sid, tid)

        return trans_vid, trans_eid
