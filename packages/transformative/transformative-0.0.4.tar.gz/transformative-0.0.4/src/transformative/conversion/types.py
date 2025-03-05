from dataclasses import dataclass
from typing import Optional, Type, Any


@dataclass(frozen=True)
class ConversionSignature:
    """Represents a unique signature for a conversion function"""

    from_type: Type[Any]
    to_type: Type[Any]
    description: Optional[str] = None

    def get_description(self) -> str:
        """Get the description of the conversion"""
        return self.description if self.description else f"Convert {self.from_type.__name__} to {self.to_type.__name__}"

    def __init__(
            self,
            from_type: Type[Any],
            to_type: Type[Any],
            description: Optional[str] = None,
            file_name: Optional[str] = None,
            function_name: Optional[str] = None
    ):
        """Initialize the conversion signature
        
        Args:
            from_type: Type to convert from
            to_type: Type to convert to
            description: Optional description of the conversion
            file_name: Optional custom file name
            function_name: Optional custom function name
        """
        object.__setattr__(self, 'from_type', from_type)
        object.__setattr__(self, 'to_type', to_type)
        object.__setattr__(self, 'description', description)
        object.__setattr__(self, '_file_name', file_name)
        object.__setattr__(self, '_function_name', function_name)

        if description is None:
            object.__setattr__(self, 'description', self.get_description())

    def file_name(self) -> str:
        """Get the file name for this conversion"""
        if self._file_name:
            return self._file_name
        return f"{self.from_type.__name__.lower()}_to_{self.to_type.__name__.lower()}"

    def function_name(self) -> str:
        """Get the function name for this conversion"""
        if self._function_name:
            return self._function_name
        return f"convert_{self.from_type.__name__.lower()}_to_{self.to_type.__name__.lower()}"

    def short_name(self) -> str:
        """Create a string representation suitable for function/file names"""
        base = f"{self.from_type.__name__}_to_{self.to_type.__name__}"
        if self.description:
            # TODO: incorporate description into signature in a clean way
            pass
        return base

    def __str__(self) -> str:
        """Create a string representation suitable for function/file names"""
        base = f"{self.from_type.__name__} to {self.to_type.__name__}"
        if self.description:
            short_description = self.description.replace("\n", " ").strip()[0:50]
            base += f", {short_description}"
        return base

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ConversionSignature):
            return NotImplemented
        return self.from_type == other.from_type and self.to_type == other.to_type and self.description == other.description

    def __hash__(self) -> int:
        # TODO Fix modules, they are too often "__main__"
        from_type_str = f"{self.from_type.__module__}.{self.from_type.__name__}"
        to_type_str = f"{self.to_type.__module__}.{self.to_type.__name__}"
        hash_result = hash((from_type_str, to_type_str, self.description))
        # print(f"Hashing signature with:\n  from: {from_type_str}\n  to: {to_type_str}\n  desc: {self.description}\n  result: {hash_result}")
        return hash_result
