"""Base classes for composite data structures.

Contents:
    Forms: stores all direct subclasses of `Composite` and `Graph` and provides
        convenient classification and transformation methods.
    Composite: base class for all composite data structures.
    Graph: base class for graphs.
    Edge: base class for an edge in a graph. Many graphs will not require edge
        instances, but the class is made available for more complex graphs and
        type checking.
    Node: wrapper for items that can be stored in a composite data structure.

    classify: returns name of the subtype a subtype of the passed item.
    transform: general subtype transformer that allows any base form of a
        Composite or Graph to be changed to any other recognized form.

To Do:

"""
from __future__ import annotations

import abc
import contextlib
import dataclasses
import inspect
import sys
from collections.abc import (
    Collection,
    Hashable,
    MutableMapping,
    MutableSequence,
    Sequence,
)
from typing import Any, ClassVar, TypeAlias

import wonka

from . import check, utilities, workshop

if sys.version_info < (3, 12):
    GenericDict: TypeAlias = MutableMapping[Hashable, Any]
    GenericList: TypeAlias = MutableSequence[Any]
else:
    type GenericDict = MutableMapping[Hashable, Any]
    type GenericList = MutableSequence[Any]


@dataclasses.dataclass
class Forms(wonka.Registrar):
    """Registry of composite data structures.

    Attributes:
        registry: stores classes and/or instances to be used in item
            construction. Defaults to an empty `dict`.

    """

    registry: ClassVar[GenericDict] = {}

    """ Public Methods """

    @classmethod
    def classify(cls, item: object) -> str:
        """Determines which form of composite that `item` is.

        There is no difference between this classmethod and the `classify`
        function.

        Args:
            item: object to classify.

        Returns:
            Name of form that `item` is.

        """
        return classify(item)

    @classmethod
    def register(cls, item: type[Composite], name: str | None = None) -> None:
        """Adds `item` to `registry`.

        The key assigned for storing `item` is determined using the _namify
        function if `name` is not passed.

        Args:
            item: class to register.
            name: key to use for storing `item`. Defaults to None.

        """
        name = name or utilities._namify(item)
        cls.registry[name] = item
        return

    @classmethod
    def transform(
        cls,
        item: Composite,
        output: str, *,
        raise_same_error: bool | None = True) -> Composite:
        """General transform method that will call appropriate transformer.

        Unlike the `transform` function, this method will return a Composite
        wrapped in the form type stored in the Forms registry (as opposed to the
        raw type). So, if `output` is `edges`, this method will return an edge
        list in the Edges class. In contrast, the `transform` method will return
        the structural type of an edge list without using the Edges class. The
        rest of the logic is identical between the function and method.

        Args:
            item: Composite to transform.
            output: name of form to transform `item` to.
            raise_same_error: whether to return an error if the form of `item`
                is the same as `output`. If True, a ValueError will be returned.
                If False, item will be return without any change. Defaults to
                True.

        Raises:
            ValueError: if the form of `item` is the same as `output` and
                `raise_same_error` is True.

        Returns:
            Transformed composite data structure.

        """
        form = cls.classify(item)
        if form == output and raise_same_error:
            raise ValueError('The passed item and output are the same type')
        if form == output:
            return item
        transformer = getattr(workshop, [f'{form}_to_{output}'])
        return cls.registry[output](contents = transformer(item = item))


""" Base Classes for Composite Data Structures """

@dataclasses.dataclass
class Composite(abc.ABC):  # noqa: B024
    """Base class for composite data structures.

    Args:
         contents: stored nodes or node labels. Subclasses should narrow the
            type for contents based on the internal storage format used.

    """
    contents: Collection[Any] | None = None

    """ Initialization Methods """

    @classmethod
    def __init_subclass__(cls, *args: Any, **kwargs: Any):
        """Automatically registers subclass.."""
        # Because Composite will be used with mixins, it is important to call
        # other `__init_subclass__` methods, if they exist.
        with contextlib.suppress(AttributeError):
            super().__init_subclass__(*args, **kwargs)
        # Adds a subclass to the Forms registry only if it is a direct subclass
        # of Composite.
        if Composite in cls.__bases__ and abc.ABC not in cls.__bases__:
            Forms.register(item = cls)

    """ Public Methods """

    def add(self, item: Hashable, **kwargs: Any) -> None:
        """Adds node to the stored composite data structure.

        Args:
            item: node to add to the stored composite data structure.
            kwargs: additional keyword arguments.

        Raises:
            TypeError: if `item` is not a node type.
            ValueError: if `item` is already in the stored composite data
                structure.

        """
        if not check.is_node(item = item):
            raise TypeError(f'{item} is not a node type')
        if item in self.contents:
            raise ValueError(
                f'{item} is already in the composite data structure')
        self._add(item, **kwargs)
        return

    def delete(self, item: Hashable, **kwargs: Any) -> None:
        """Deletes node from the stored composite data structure.

        Subclasses must provide their own specific methods for deleting a single
        node. The provided `delete` method offers all of the error checking and
        the ability to delete multiple nodes at once. Subclasses just need to
        provide the mechanism for deleting a single node without worrying about
        validation or error-checking.

        Args:
            item: node to delete from `contents`.
            kwargs: additional keyword arguments.

        Raises:
            KeyError: if `item` is not in `contents`.
            TypeError: if `item` is not in `contents`.

        """
        if not check.is_node(item = item):
            raise TypeError(f'{item} is not a node type')
        try:
            self._delete(item, **kwargs)
        except KeyError as e:
            message = f'{item} does not exist in the composite data structure'
            raise KeyError(message) from e
        return

    def merge(self, item: Composite, **kwargs: Any) -> None:
        """Adds `item` to this Composite.

        This method is roughly equivalent to a dict.update, just adding `item`
        to the existing stored composite data structure while maintaining its
        structure.

        Args:
            item: another Composite to merge with
            kwargs: additional keyword arguments.

        Raises:
            TypeError: if `item` is not compatible composite data structure
                type.

        """
        if not check.is_composite(item = item):
            raise TypeError(f'{item} is not a compatible type')
        self._merge(item, **kwargs)
        return

    def subset(
        self,
        include: Hashable | Sequence[Hashable] = None,
        exclude: Hashable | Sequence[Hashable] = None) -> Composite:
        """Returns a new Composite without a subset of `contents`.

        All edges will be removed that include any nodes that are not part of
        the new composite data structure.

        Any extra attributes that are part of a Composite (or a subclass) should
        be maintained in the returned composite data structure.

        Args:
            include: nodes or edges which should be included in the new
                composite data structure.
            exclude: nodes or edges which should not be included in the new
                composite data structure.

        Raises:
            ValueError: if include and exclude are none or if any item in
                include or exclude is not in the stored composite data
                structure.

        Returns:
           Composite with only selected nodes and edges.

        """
        if include is None and exclude is None:
            raise ValueError('Either include or exclude must not be None')
        if not all(i for i in include if i in self.contents):
            raise ValueError(
                'Some values in include are not in the composite data '
                'structure')
        if not all(i for i in exclude if i in self.contents):
            raise ValueError(
                'Some values in exclude are not in the composite data '
                'structure')
        return self._subset(include, exclude)

    """ Private Methods """

    def _add(self, item: Hashable, **kwargs: Any) -> None:
        """Adds node to the stored composite data structure.

        Subclasses must provide their own specific methods for adding a single
        node. The provided `add` method offers all of the error checking and
        the ability to add multiple nodes at once. Subclasses just need to
        provide the mechanism for adding a single node without worrying about
        validation or error-checking.

        Args:
            item: node to add to the stored composite data structure.
            kwargs: additional keyword arguments.

        """
        raise NotImplementedError

    def _delete(self, item: Hashable, **kwargs: Any) -> None:
        """Deletes node from the stored composite data structure.

        Subclasses must provide their own specific methods for deleting a single
        node. The provided `delete` method offers all of the error checking and
        the ability to delete multiple nodes at once. Subclasses just need to
        provide the mechanism for deleting a single node without worrying about
        validation or error-checking.

        Args:
            item: node to delete from `contents`.
            kwargs: additional keyword arguments.

        """
        raise NotImplementedError

    def _merge(self, item: Composite, **kwargs: Any) -> None:
        """Combines `item` with the stored composite data structure.

        Subclasses must provide their own specific methods for merging with
        another composite data structure. The provided `merge` method offers all
        of the error checking. Subclasses just need to provide the mechanism for
        merging without worrying about validation or error-checking.

        Args:
            item: another Composite object to add to the stored
                composite data structure.
            kwargs: additional keyword arguments.

        """
        raise NotImplementedError

    def _subset(
        self,
        include: Hashable | Sequence[Hashable] = None,
        exclude: Hashable | Sequence[Hashable] = None) -> Composite:
        """Returns a new Composite without a subset of `contents`.

        Subclasses must provide their own specific methods for deleting a single
        edge. Subclasses just need to provide the mechanism for returning a
        subset without worrying about validation or error-checking.

        Args:
            include: nodes or edges which
                should be included in the new composite data structure.
            exclude: nodes or edges which
                should not be included in the new composite data structure.

        Returns:
           Graph with only selected nodes and edges.

        """
        raise NotImplementedError

    """ Dunder Methods """

    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        """Returns whether `instance` meets criteria to be a subclass.

        Args:
            instance (object): item to test as an instance.

        Returns:
            bool: whether `instance` meets criteria to be a subclass.

        """
        return check.is_composite(item = instance)


@dataclasses.dataclass
class Graph(Composite, abc.ABC):
    """Base class for holden graphs.

    Graph adds the requirements of `_connect` and `_disconnect` methods in
    addition to the requirements of Composite.

    Args:
         contents: stored nodes, node labels, edges, or edge labels. Subclasses
            should narrow the type for contents based on the internal storage
            format used.

    """
    contents: Collection[Any] | None = None

    """ Initialization Methods """

    @classmethod
    def __init_subclass__(cls, *args: Any, **kwargs: Any):
        """Automatically registers subclass.."""
        # Because Graph will be used with mixins, it is important to call other
        # `__init_subclass__` methods, if they exist.
        with contextlib.suppress(AttributeError):
            super().__init_subclass__(*args, **kwargs)
        # Adds a subclass to the Forms registry only if it is a direct subclass
        # of Graph.
        if Graph in cls.__bases__:
            Forms.register(item = cls)

    """ Public Methods """

    def connect(self, item: Edge, **kwargs: Any) -> None:
        """Adds edge to the stored graph.

        Args:
            item: edge to add to the stored graph.
            kwargs: additional keyword arguments.

        Raises:
            ValueError: if the ends of the item are the same or if one of the
                edge ends does not currently exist in the stored graph.

        """
        if not check.is_edge(item = item):
            raise TypeError(f'{item} is not an edge type')
        if item[0] == item[1]:
            raise ValueError(
                'The starting point of an edge cannot be the same as the '
                'ending point')
        if item[0] not in self:
            raise ValueError(f'{item[0]} is not in the graph')
        if item[1] not in self:
            raise ValueError(f'{item[1]} is not in the graph')
        self._connect(item, **kwargs)
        return

    def disconnect(self, item: Edge, *kwargs: Any) -> None:
        """Removes edge from the stored graph.

        Args:
            item: edge to delete from the stored graph.
            kwargs: additional keyword arguments.

        Raises:
            ValueError: if the edge does not exist in the stored graph.

        """
        if not check.is_edge(item = item):
            raise TypeError(f'{item} is not an edge type')
        if item[0] == item[1]:
            raise ValueError(
                'The starting point of an edge cannot be the same as the '
                'ending point')
        try:
            self._disconnect(item, **kwargs)
        except (KeyError, ValueError) as e:
            message = f'The edge ({item[0]}, {item[1]}) is not in the graph'
            raise ValueError(message) from e
        return

    """ Private Methods """

    def _connect(self, item: Edge, **kwargs: Any) -> None:
        """Adds edge to the stored graph.

        Subclasses must provide their own specific methods for adding a single
        edge. The provided `connect` method offers all of the error checking and
        the ability to add multiple edges at once. Subclasses just need to
        provide the mechanism for adding a single edge without worrying about
        validation or error-checking.

        Args:
            item: edge to add to the stored graph.
            kwargs: additional keyword arguments.

        """
        raise NotImplementedError

    def _disconnect(self, item: Edge, **kwargs: Any) -> None:
        """Removes edge from the stored graph.

        Subclasses must provide their own specific methods for deleting a single
        edge. The provided `disconnect` method offers all of the error checking
        and the ability to delete multiple edges at once. Subclasses just need
        to provide the mechanism for deleting a single edge without worrying
        about validation or error-checking.

        Args:
            item: edge to delete from the stored graph.
            kwargs: additional keyword arguments.

        """
        raise NotImplementedError

    """ Dunder Methods """

    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        """Returns whether `instance` meets criteria to be a subclass.

        Args:
            instance: item to test as an instance.

        Returns:
            Whether `instance` meets criteria to be a subclass.

        """
        return check.is_graph(item = instance)


@dataclasses.dataclass(frozen = True, order = True)
class Edge(Sequence):
    """Base class for an edge in a graph structure.

    Edges are not required for most of the base graph classes in holden. But
    they can be used by subclasses of those base classes for more complex data
    structures.

    Args:
        start: starting point for the edge.
        stop: stopping point for the edge.

    """
    start: Hashable
    stop: Hashable

    """ Dunder Methods """

    def __getitem__(self, index: int) -> Hashable:
        """Allows Edge subclass to be accessed by index.

        Args:
            index: the number of the field in the dataclass based on order.

        Raises:
            IndexError: if `index` is greater than 1.

        Returns:
            Contents of field identified by `index`.

        """
        if index > 1:
            raise IndexError('Index out of bounds - edges are only two points')
        return getattr(self, dataclasses.fields(self)[index].name)

    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        """Returns whether `instance` meets criteria to be a subclass.

        Args:
            instance: item to test as an instance.

        Returns:
            Whether `instance` meets criteria to be a subclass.

        """
        return check.is_edge(item = instance)

    def __len__(self) -> int:
        """Returns length of 2.

        Returns:
            int: 2

        """
        return 2


@dataclasses.dataclass
class Node(Hashable):
    """Vertex wrapper to provide hashability to any object.

    Node acts a basic wrapper for any item stored in a graph structure.

    Args:
        contents: any stored item(s). Defaults to None.

    """
    contents: Any | None = None

    """ Initialization Methods """

    def __init_subclass__(cls, *args: Any, **kwargs: Any):
        """Forces subclasses to use the same hash methods as Node.

        This is necessary because dataclasses, by design, do not automatically
        inherit the hash and equivalance dunder methods from their super
        classes.

        """
        # Calls other `__init_subclass__` methods for parent and mixin classes.
        with contextlib.suppress(AttributeError):
            super().__init_subclass__(*args, **kwargs)
        # Copies hashing related methods to a subclass.
        cls.__hash__ = Node.__hash__
        cls.__eq__ = Node.__eq__
        cls.__ne__ = Node.__ne__

    """ Dunder Methods """

    # @classmethod
    # def __subclasshook__(cls, subclass: Type[Any]) -> bool:
    #     """Returns whether `subclass` is a virtual or real subclass.

    #     Args:
    #         subclass (Type[Any]): item to test as a subclass.

    #     Returns:
    #         bool: whether `subclass` is a real or virtual subclass.

    #     """
    #     return check.is_node(item = subclass)

    # @classmethod
    # def __instancecheck__(cls, instance: object) -> bool:
    #     """Returns whether `instance` meets criteria to be a subclass.

    #     Args:
    #         instance (object): item to test as an instance.

    #     Returns:
    #         bool: whether `instance` meets criteria to be a subclass.

    #     """
    #     return check.is_node(item = instance)

    def __hash__(self) -> int:
        """Makes Node hashable so that it can be used as a key in a dict.

        Rather than using the object ID, this method prevents two Nodes with
        the same name from being used in a graph object that uses a dict as
        its base storage type.

        Returns:
            int: hashable of `name`.

        """
        return hash(dataclasses.astuple(self))


""" Subtype Checker """

def classify(item: object) -> str:
    """Determines which form of graph that `item` is.

    Args:
        item: object to classify.

    Returns:
        Name of form that `item` is.

    """
    # Chcecks for a matching parent clas in `registry`.
    subtype = item if inspect.isclass(item) else item.__class__
    for name, form in Forms.registry.items():
        if issubclass(subtype, form):
            return name
    # Chaecks for matching raw form using functions in the `check` module.
    for name in Forms.registry:
        with contextlib.suppress(AttributeError):
            checker = getattr(check, f'is_{name}')
            if checker(item = item):
                return name
    raise TypeError('The passed item is not a recognized Graph form')

""" Graph Transformer """

def transform(
    item: Graph,
    output: str, *,
    raise_same_error: bool | None = True) -> Graph:
    """General transform function that will call appropriate transformer.

    Args:
        item: Graph to transform.
        output: name of form to transform `item` to.
        raise_same_error: whether to return an error if the form of `item` is
            the same as `output`. If True, a ValueError will be returned. If
            False, item will be return without any change. Defaults to True.

    Raises:
        ValueError: if the form of `item` is the same as `output` and
            `raise_same_error` is True.

    Returns:
        Transformed graph.

    """
    form = classify(item)
    if form == output and raise_same_error:
        raise ValueError('The passed item and output are the same type')
    if form == output:
        return item
    transformer = getattr(workshop, f'{form}_to_{output}')
    return transformer(item = item)
