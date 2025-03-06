"""Premises Extender Mixin"""

import sys
import importlib


class ExtenderMixin():
    """Dynamic Premises processing"""

    @property
    def rule(self):
        """Returns premises rule class"""
        rule_num = ''.join(['0' if self.is_empty(k) else '1' for k in self.building_attrs])
        package_name = getattr(sys.modules[__name__], '__package__', None)
        module_name = f'rule{rule_num}'
        module = importlib.import_module(f'{package_name}.{module_name}')
        class_name = f'Rule{rule_num}'
        return getattr(module, class_name)

    def extend(self):
        """Dynamically extends instance with appropriate rule"""
        base_cls = self.__class__
        object.__setattr__(self, '__class__', type(base_cls.__name__, (base_cls, self.rule), {}))
