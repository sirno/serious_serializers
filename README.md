# Serious Serializers

![tests](https://github.com/sirno/serious_serializers/actions/workflows/tests.yml/badge.svg)

Simple class mixin to add YAML serialization and deserialization to dataclass
objects that use slots.

## Examples

To add serialization to dataclass object:

```python
from serious_serializers import SlotsSerializer

@dataclass(slots=True)
class Data(SlotsSerializer):
    n: int
    data: List[float]
```

To represent the class tag as `!Data`:

```python
from serious_serializers import SlotsSerializer

@SlotsSerializer.show_tag
@dataclass(slots=True)
class Data(SlotsSerializer):
    n: int
    data: List[float]
```
