"""Serializer and deserializer mixins for YAML."""

from __future__ import annotations

__all__ = ["SlotsSerializer", "SlotsLoader", "SlotsDumper"]

import yaml
import typing

from typing_extensions import Self

from collections import OrderedDict
from typing import Dict


class SlotsLoader(yaml.SafeLoader):
    pass


class SlotsDumper(yaml.SafeDumper):
    pass


class SlotsSerializer:
    """Serialize and deserialize YAML slotted dataclasses in order."""

    def __init_subclass__(cls) -> None:
        # Add constructor to the yaml decoder
        def construct_yaml(loader: SlotsSerializer, node: yaml.nodes.Node) -> cls:
            type_hints = typing.get_type_hints(cls)
            mapping = {}
            for key_node, value_node in node.value:
                key = loader.construct_object(key_node, deep=False)
                value_type = type_hints[key]
                value = (
                    value_type.__construct_yaml(loader, value_node)
                    if issubclass(value_type, SlotsSerializer)
                    else loader.construct_object(value_node)
                )
                mapping[key] = value
            return cls(**mapping)

        cls.__construct_yaml = construct_yaml
        SlotsLoader.add_constructor(f"!{cls.__name__}", construct_yaml)

        # Add representer to the yaml encoder
        def represent_yaml(dumper: SlotsDumper, data: cls) -> yaml.nodes.MappingNode:
            representer_tag = (
                f"!{cls.__name__}"
                if getattr(data, "_show_tag", False)
                else "tag:yaml.org,2002:map"
            )
            return dumper.represent_mapping(
                representer_tag,
                data.to_dict(),
            )

        SlotsDumper.add_representer(cls, represent_yaml)

    def __items(self) -> typing.Iterator[typing.Tuple[str, typing.Any]]:
        for k in self.__slots__:
            yield k, getattr(self, k)

    def to_dict(self, recursive=False) -> OrderedDict:
        """Convert to ordered dict."""
        if not recursive:
            return OrderedDict(self.__items())

        type_hints = typing.get_type_hints(self)
        return OrderedDict(
            (k, v.to_dict() if issubclass(type_hints[k], SlotsSerializer) else v)
            for k, v in self.__items()
        )

    def to_yaml(self) -> str:
        """Convert to yaml string."""
        return yaml.dump(self, Dumper=SlotsDumper, sort_keys=False)

    def to_yaml_file(self, path):
        """Write to yaml file."""
        with open(path, "w") as f:
            f.write(self.to_yaml())

    def __str__(self) -> str:
        return self.to_yaml()

    @classmethod
    def from_dict(cls, data: Dict) -> Self:
        """Convert from dict."""
        type_hints = typing.get_type_hints(cls)
        return cls(
            **{
                k: type_hints[k].from_dict(v)
                if issubclass(type_hints[k], SlotsSerializer)
                else v
                for k, v in data.items()
            }
        )

    @classmethod
    def from_yaml(cls, yaml_string: str) -> Self:
        """Convert from yaml string."""
        if not yaml_string.startswith(f"!{cls.__name__}"):
            yaml_string = f"!{cls.__name__}\n{yaml_string}"

        dump = yaml.load(yaml_string, Loader=SlotsLoader)

        if isinstance(dump, dict):
            return cls.from_dict(dump)

        if isinstance(dump, cls):
            return dump

        raise TypeError(f"Cannot load {cls.__name__} from {dump}")

    @classmethod
    def from_yaml_file(cls, path) -> Self:
        """Read from yaml file."""
        with open(path, "r") as f:
            return cls.from_yaml(f.read())

    @classmethod
    def show_tag(cls, subclass) -> Self:
        """Decorator to show tag in yaml output."""
        subclass._show_tag = True
