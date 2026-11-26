"""FAC credential helpers.

Public API is intentionally small: namespace-aware get/set/delete/list and mask.
"""

from ._core import (
    delete,
    get,
    list_all,
    load_json,
    masked_list,
    namespace_dir,
    save_json,
    set,
)

__all__ = [
    "delete",
    "get",
    "list_all",
    "load_json",
    "masked_list",
    "namespace_dir",
    "save_json",
    "set",
]
