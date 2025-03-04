from .format_sequences import format_long_sequence
from .poly_data_utils import set_polydata_colors, set_polydata_property
from .tree_info import TreeInfo


from collections import defaultdict
def nested_dict() -> defaultdict:
    return defaultdict(nested_dict)
