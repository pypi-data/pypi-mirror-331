# draft_basic/__init__.py
__version__ = "0.11.3"
from . import neuralnetwork  # 从当前包中导入 BP 模块
from . import ml_basic
from . import metrics
from . import pretreat
from . import example_dataset
#from . import calculations # 从当前包中导入 calculations 模块
#from .sub_package import advanced_math # 从子包 sub_package 中导入 advanced_math 模块

# (也可以选择性地从模块中导入特定的函数或类，例如)
# from .math_utils import add, subtract

__all__ = ['neuralnetwork', 'ml_basic', 'metrics', 'pretreat', 'example_dataset']