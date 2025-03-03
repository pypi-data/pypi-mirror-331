"""Graphs with different internal storage formats.

Contents:
    Adjacency: a graph stored as an adjacency list.
    Edges: a graph stored as an edge list.
    Matrix: a graph stored as an adjacency matrix.

To Do:
    Add methods that currently raise NotImplementedError

"""
from __future__ import annotations

import collections
import copy
import dataclasses
from typing import TYPE_CHECKING, Any

import bunches

from . import base, check, utilities

if TYPE_CHECKING:
    from collections.abc import (
        Hashable,
        MutableMapping,
        MutableSequence,
        Sequence,
    )

""" Graph Form Base Classes """

@dataclasses.dataclass
class Adjacency(base.Graph, bunches.Dictionary):
    """Base class for adjacency-list graphs.

    Args:
        contents: keys are hashable representations of nodes. Values are the
            nodes to which the key node are connected. In a directed graph, the
            key node is assumed to come before the value node in order. Defaults
            to a defaultdict that has a set for its value type.

    """
    contents: MutableMapping[Hashable, set[Hashable]] = dataclasses.field(
            default_factory = lambda: collections.defaultdict(set))

    """ Private Methods """

    def _add(self, item: Hashable, **kwargs: Any) -> None:
        """Adds node to the stored graph.

        Args:
            item: node to add to the stored graph.
            kwargs: additional keyword arguments.

        """
        self.contents[item] = set()
        return

    def _connect(self, item: base.Edge, **kwargs: Any) -> None:
        """Adds edge to the stored graph.

        Args:
            item: edge to add to the stored graph.
            kwargs: additional keyword arguments.

        """
        self.contents[item[0]].add(item[1])
        return

    def _delete(self, item: Hashable, **kwargs: Any) -> None:
        """Deletes node from the stored graph.

        Args:
            item: node to delete from `contents`.
            kwargs: additional keyword arguments.

        """
        del self.contents[item]
        self.contents = {k: v.remove(item) for k, v in self.contents.items()}
        return

    def _disconnect(self, item: base.Edge, **kwargs: Any) -> None:
        """Removes edge from the stored graph.

        Args:
            item: edge to delete from the stored graph.
            kwargs: additional keyword arguments.

        """
        self.contents[item[0]].remove(item[1])
        return

    def _merge(self, item: base.Graph, **kwargs: Any) -> None:
        """Combines 'item' with the stored graph.

        Args:
            item: another Graph object to add to the stored graph.
            kwargs: additional keyword arguments.

        """
        other = base.transform(
            item = item,
            output = 'adjacency',
            raise_same_error = False)
        for node, edges in other.items():
            if node in self:
                self[node].update(edges)
            else:
                self[node] = edges
        return

    def _subset(
        self,
        include: Hashable | Sequence[Hashable] = None,
        exclude: Hashable | Sequence[Hashable] = None) -> Adjacency:
        """Returns a new graph without a subset of `contents`.

        Args:
            include (Union[Hashable, Sequence[Hashable]]): nodes or edges which
                should be included in the new graph.
            exclude (Union[Hashable, Sequence[Hashable]]): nodes or edges which
                should not be included in the new graph.

        Returns:
           Adjacency: with only selected nodes and edges.

        """
        excludables = [
            k for k in self.contents if k not in include] if include else []
        excludables.extend([i for i in self.contents if i in exclude])
        new_graph = copy.deepcopy(self)
        for node in utilities._iterify(excludables):
            new_graph.delete(node = node)
        return new_graph

    """ Dunder Methods """

    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        """Returns whether `instance` meets criteria to be a subclass.

        Args:
            instance (object): item to test as an instance.

        Returns:
            Whether `instance` meets criteria to be a subclass.

        """
        return check.is_adjacency(item = instance)


@dataclasses.dataclass
class Edges(base.Graph, bunches.Listing):
    """Base class for edge-list graphs.

    Args:
        contents: Listing of edges. Defaults to an empty list.

    """
    contents: MutableSequence[base.Edge] = dataclasses.field(
        default_factory = list)

    """ Private Methods """

    def _add(self, item: base.Edge, **kwargs: Any) -> None:
        """Adds edge to the stored graph.

        Args:
            item: edge to add to the stored graph.
            kwargs: additional keyword arguments.

        """
        self.contents.append(item)
        return

    def _connect(self, item: base.Edge, **kwargs: Any) -> None:
        """Adds edge to the stored graph.

        Args:
            item: edge to add to the stored graph.
            kwargs: additional keyword arguments.

        """
        self.contents.append(item)
        return

    def _delete(self, item: base.Edge, **kwargs: Any) -> None:
        """Removes edge from the stored graph.

        Args:
            item: edge to delete from the stored graph.
            kwargs: additional keyword arguments.

        """
        self.contents.remove(item)
        return

    def _disconnect(self, item: base.Edge, **kwargs: Any) -> None:
        """Removes edge from the stored graph.

        Args:
            item: edge to delete from the stored graph.
            kwargs: additional keyword arguments.

        """
        self.contents.remove(item)
        return

    def _merge(self, item: base.Graph, **kwargs: Any) -> None:
        """Combines 'item' with the stored graph.

        Args:
            item: another Graph object to add to the stored graph.
            kwargs: additional keyword arguments.

        """
        other = base.transform(
            item = item,
            output = 'edges',
            raise_same_error = False)
        self.contents.extend(other)
        return

    def _subset(
        self,
        include: Hashable | Sequence[Hashable] = None,
        exclude: Hashable | Sequence[Hashable] = None) -> Adjacency:
        """Returns a new graph without a subset of `contents`.

        Args:
            include: nodes or edges which should be included in the new graph.
            exclude: nodes or edges which should not be included in the new
                graph.

        Returns:
           Adjacency with only selected nodes and edges.

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
        return check.is_edges(item = instance)


@dataclasses.dataclass
class Matrix(base.Graph, bunches.Listing):
    """Base class for adjacency-matrix graphs.

    Args:
        contents: a list of list of integers indicating edges between nodes in
            the matrix. Defaults to an empty list.
        labels: names of nodes in the matrix. Defaults to an empty list.

    """
    contents: MutableSequence[MutableSequence[int]] = dataclasses.field(
        default_factory = list)
    labels: MutableSequence[Hashable] = dataclasses.field(
        default_factory = list)

    """ Private Methods """

    def _add(self, item: base.Edge, **kwargs: Any) -> None:
        """Adds edge to the stored graph.

        Args:
            item: edge to add to the stored graph.
            kwargs: additional keyword arguments.

        """
        raise NotImplementedError

    def _connect(self, item: base.Edge, **kwargs: Any) -> None:
        """Adds edge to the stored graph.

        Args:
            item: edge to add to the stored graph.
            kwargs: additional keyword arguments.

        """
        raise NotImplementedError

    def _delete(self, item: base.Edge, **kwargs: Any) -> None:
        """Removes edge from the stored graph.

        Args:
            item: edge to delete from the stored graph.
            kwargs: additional keyword arguments.

        """
        raise NotImplementedError

    def _disconnect(self, item: base.Edge, **kwargs: Any) -> None:
        """Removes edge from the stored graph.

        Args:
            item: edge to delete from the stored graph.
            kwargs: additional keyword arguments.

        """
        raise NotImplementedError

    def _merge(self, item: base.Graph, **kwargs: Any) -> None:
        """Combines `item` with the stored graph.

        Args:
            item: another Graph object to add to the stored graph.
            kwargs: additional keyword arguments.

        """
        other = base.transform(
            item = item,
            output = 'matrix',
            raise_same_error = False)
        new_matrix = other[0]
        length = len(self.contents)
        for row in enumerate(new_matrix):
            for column in enumerate(row):
                self.contents[row + length][column + length] = (
                    new_matrix[row][column])
        self.labels.extend(other[1])
        return

    def _subset(
        self,
        include: Hashable | Sequence[Hashable] = None,
        exclude: Hashable | Sequence[Hashable] = None) -> Adjacency:
        """Returns a new graph without a subset of `contents`.

        Args:
            include: nodes or edges which should be included in the new graph.
            exclude: nodes or edges which should not be included in the new
                graph.

        Returns:
           Adjacency with only selected nodes and edges.

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
        return check.is_matrix(item = instance)
