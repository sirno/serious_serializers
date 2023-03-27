# Serious Serializer

Simple class mixin to add YAML serialization to dataclass objects that use
slots.

```python
from serious_serializers import SlotsSerializer

@dataclass(slots=True)
class Data(SlotsSerializer):
    n: int
    data: List[float]
```

To represent the class tag:

```python
from serious_serializers import SlotsSerializer

@SlotsSerializer.show_tag
@dataclass(slots=True)
class Data(SlotsSerializer):
    n: int
    data: List[float]
```
