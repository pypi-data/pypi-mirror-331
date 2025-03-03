"""
Import - export scene in json friendly format
"""
import numpy as np

from scenegraph import Rotation, RotationEuler, ScNode, Scaling, Scene, Translation
from scenegraph.triangle import Triangle
from scenegraph.triangle_set import TriangleSet


def _dumps_shape(shape):
    """Convert shape to simple python elements

    Args:
        shape (Shape):

    Returns:
        (dict)
    """
    if isinstance(shape, str):
        return dict(type='ref', oid=shape)
    else:
        if isinstance(shape, Triangle):
            shp = dict(type='Triangle', pts=[vec.tolist() for vec in shape.points()])
        elif isinstance(shape, TriangleSet):
            shp = dict(type='TriangleSet',
                       pts=[vec.tolist() for vec in shape.points()],
                       faces=[tuple(face) for face in shape.faces()])
        else:
            raise NotImplementedError(f"Unrecognized shape of type '{type(shape)}'")

        shp['meta'] = shape.meta
        return shp


def _loads_shape(sh_repr):
    """Create shape from simple python elements

    Args:
        sh_repr (dict):

    Returns:
        (Shape)
    """
    if sh_repr['type'] == 'ref':
        return sh_repr['oid']
    else:
        if sh_repr['type'] == 'Triangle':
            shp = Triangle(*(np.array(vec) for vec in sh_repr['pts']))
        elif sh_repr['type'] == 'TriangleSet':
            shp = TriangleSet(points=[np.array(vec) for vec in sh_repr['pts']],
                              faces=[tuple(face) for face in sh_repr['faces']])
        else:
            raise NotImplementedError(f"Unrecognized shape of type '{sh_repr['type']}'")

        shp.meta.update(sh_repr['meta'])
        return shp


def _dumps_transfo(transfo):
    """Convert transfo to simple python elements

    Args:
        transfo (Transfo):

    Returns:
        (dict)
    """
    if isinstance(transfo, Rotation):
        ax_repr = transfo.axis
        if not isinstance(ax_repr, str):
            ax_repr = ax_repr.tolist()
        tr = dict(type='Rotation', angle=transfo.alpha, axis=ax_repr)
    elif isinstance(transfo, RotationEuler):
        tr = dict(type='RotationEuler', pitch=transfo.pitch, roll=transfo.roll, yaw=transfo.yaw)
    elif isinstance(transfo, Scaling):
        tr = dict(type='Scaling', vec=transfo.vec.tolist())
    elif isinstance(transfo, Translation):
        tr = dict(type='Translation', vec=transfo.vec.tolist())
    else:
        raise NotImplementedError(f"Unrecognized transfo of type '{type(transfo)}'")

    if transfo.name != "":
        tr['name'] = transfo.name

    return tr


def _loads_transfo(tr_repr):
    """Create transfo from simple python elements

    Args:
        tr_repr (dict): transfo representation

    Returns:
        (Transfo)
    """
    if tr_repr['type'] == 'Rotation':
        axis = tr_repr['axis']
        if not isinstance(axis, str):
            axis = np.array(axis)

        tr = Rotation(alpha=tr_repr['angle'], axis=axis)
    elif tr_repr['type'] == 'RotationEuler':
        tr = RotationEuler(pitch=tr_repr['pitch'], roll=tr_repr['roll'], yaw=tr_repr['yaw'])
    elif tr_repr['type'] == 'Scaling':
        tr = Scaling(vec=np.array(tr_repr['vec']))
    elif tr_repr['type'] == 'Translation':
        tr = Translation(vec=np.array(tr_repr['vec']))
    else:
        raise NotImplementedError(f"Unrecognized transfo of type '{tr_repr['type']}'")

    try:
        tr.name = tr_repr['name']
    except KeyError:
        pass

    return tr


def _dumps(node):
    """Convert node to simple python elements

    Args:
        node (ScNode):

    Returns:
        (dict)
    """
    res = dict(
        type="node",
        transfos=[_dumps_transfo(tr) for tr in node.transfos],
        meta=dict(node.meta),
    )

    if node.shape is not None:
        res['shape'] = _dumps_shape(node.shape)

    return res


def _loads(node_repr):
    """Create node from simple python elements

    Args:
        node_repr (dict):

    Returns:
        (ScNode)
    """
    assert node_repr['type'] == "node"
    try:
        shape = _loads_shape(node_repr['shape'])
    except KeyError:
        shape = None

    transfos = [_loads_transfo(tr) for tr in node_repr['transfos']]

    node = ScNode(shape=shape,
                  transfos=transfos,
                  meta=node_repr['meta'])

    return node


def dumps(scene):
    """Convert scene to simple python elements

    Args:
        scene (Scene):

    Returns:
        (dict)
    """
    res = dict(
        type="scene",
        defs=[dict(oid=oid, data=_dumps_shape(shp)) for oid, shp in scene._defs.items()],
        nodes=[dict(nid=nid, data=_dumps(node)) for nid, node in scene.nodes()],
        edges=[dict(eid=eid, src=sid, tgt=tid) for eid, (sid, tid) in scene._graph._edges.items()],
    )

    return res


def loads(sc_repr):
    """Create Scene from simple python elements.

    Args:
        sc_repr (dict): description

    Returns:
        (Scene)
    """
    assert sc_repr['type'] == "scene"

    sc = Scene()
    for shp_descr in sc_repr['defs']:
        sc.add_def(_loads_shape(shp_descr["data"]), shp_descr["oid"])

    for node_descr in sc_repr["nodes"]:
        sc.add(_loads(node_descr["data"]), node_descr["nid"])

    for edge_descr in sc_repr["edges"]:
        sc._graph.add_edge(edge_descr["src"], edge_descr["tgt"], edge_descr["eid"])

    return sc
