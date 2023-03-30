"""Serializer and deserializer mixins for YAML."""

from __future__ import annotations

import yaml
import typing

from typing_extensions import Self

from collections import OrderedDict
from typing import Dict


class SlotsSerializer:
    """Serialize and deserialize YAML slotted dataclasses in order."""

    def __init_subclass__(cls) -> None:
        # Add constructor to the yaml decoder
        def construct_yaml(loader: yaml.SafeLoader, node: yaml.nodes.Node) -> cls:
            type_hints = typing.get_type_hints(cls)
            mapping = {}
            for key_node, value_node in node.value:
                key = loader.construct_object(key_node, deep=False)
                value_type = type_hints[key]
                print(value_type)
                value = (
                    value_type._construct_yaml(loader, value_node)
                    if issubclass(value_type, SlotsSerializer)
                    else loader.construct_object(value_node)
                )
                mapping[key] = value
            return cls(**mapping)

        cls._construct_yaml = construct_yaml
        yaml.SafeLoader.add_constructor(f"!{cls.__name__}", construct_yaml)

        # Add representer to the yaml encoder
        def represent_yaml(
            dumper: yaml.SafeDumper, data: cls
        ) -> yaml.nodes.MappingNode:
            representer_tag = (
                f"!{cls.__name__}"
                if getattr(data, "_show_tag", False)
                else "tag:yaml.org,2002:map"
            )
            return dumper.represent_mapping(
                representer_tag,
                data.to_dict(),
            )

        yaml.SafeDumper.add_representer(cls, represent_yaml)

    def to_dict(self) -> OrderedDict:
        """Convert to ordered dict."""
        return OrderedDict([(k, getattr(self, k)) for k in self.__slots__])

    def to_yaml(self) -> str:
        """Convert to yaml string."""
        return yaml.dump(self, Dumper=yaml.SafeDumper, sort_keys=False)

    def to_yaml_file(self, path):
        """Write to yaml file."""
        with open(path, "w") as f:
            f.write(self.to_yaml())

    def __str__(self) -> str:
        return self.to_yaml()

    @classmethod
    def from_dict(cls, data: Dict) -> Self:
        return cls(**data)

    @classmethod
    def from_yaml(cls, yaml_string: str) -> Self:
        if not yaml_string.startswith(f"!{cls.__name__}"):
            yaml_string = f"!{cls.__name__}\n{yaml_string}"

        dump = yaml.safe_load(yaml_string)

        if isinstance(dump, dict):
            return cls.from_dict(dump)

        if isinstance(dump, cls):
            return dump

        raise TypeError(f"Cannot load {cls.__name__} from {dump}")

    @classmethod
    def from_yaml_file(cls, path) -> Self:
        with open(path, "r") as f:
            return cls.from_yaml(f.read())

    @classmethod
    def show_tag(cls, subclass) -> Self:
        subclass._show_tag = True
