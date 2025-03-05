import functools as ft
from collections.abc import Callable
from typing import Any, NoReturn

from beartype.door import is_bearable
from jax import (
    tree as jt,
    tree_util as jtu,
)
from jaxtyping._array_types import (
    _anonymous_dim,
    _check_dims,
    _DimType,
    _FixedDim,
    _NamedDim,
    _SymbolicDim,
)
from jaxtyping._storage import get_shape_memo, set_shape_memo

from .error import TypinoxAnnotationError

_vmapped_dim = object()

VMAPPED_LETTER = "$"


def err_array_name(key_path: jtu.KeyPath) -> str:
    if len(key_path) == 0:
        return "Array"
    else:
        return f"Array at key path {key_path}"


def single_check_vmapped(
    arr: Any,
    key_path: jtu.KeyPath,
    dim_left: tuple,
    dim_right: tuple,
    single_memo: dict[str, int],
    arg_memo: dict[str, Any],
):
    if not hasattr(arr, "shape") or not hasattr(arr, "dtype"):
        # Not an array, ignored
        return arr
    shape = arr.shape
    if len(shape) < len(dim_left) + len(dim_right):
        return (
            err_array_name(key_path)
            + " has fewer dimensions than the vmapped axes"
        )
    left_idx = len(dim_left)
    right_idx = len(shape) - len(dim_right)
    if left_idx != 0:
        check = _check_dims(
            dim_left,  # type: ignore
            shape[:left_idx],
            single_memo,
            arg_memo,
        )
        if check != "":
            return err_array_name(key_path) + ": " + check
    if right_idx != len(shape):
        check = _check_dims(
            dim_right,  # type: ignore
            shape[right_idx:],
            single_memo,
            arg_memo,
        )
        if check != "":
            return err_array_name(key_path) + ": " + check
    item_idx = [
        0 if i < left_idx or i >= right_idx else slice(None)
        for i in range(len(shape))
    ]
    return arr[tuple(item_idx)]


def instancecheck_vmapped(
    inner: type,
    dims: tuple[tuple, tuple],
    checker: Callable,
    obj,
    single_memo,
    arg_memo,
):
    dim_left, dim_right = dims
    nodedefs, treedef = jt.flatten_with_path(obj)
    leaves = []
    for key_path, arr in nodedefs:
        # check if arr is a str
        if isinstance(arr, str):
            leaves.append(arr)
            continue
        check = single_check_vmapped(
            arr,
            key_path,
            dim_left,
            dim_right,
            single_memo,
            arg_memo,
        )
        if isinstance(check, str):
            if check != "":
                return check
            check = arr
        leaves.append(check)
    new_obj = jt.unflatten(treedef, leaves)
    if hasattr(inner, "__instancecheck_str__"):
        return inner.__instancecheck_str__(new_obj)
    if checker(new_obj, inner):
        return ""
    return f"{new_obj} is not an instance of {inner}"


class VmappedMeta(type):
    def __instancecheck__(cls, obj):
        return cls.__instancecheck_str__(obj) == ""

    def __instancecheck_str__(cls, obj) -> str:
        if (
            not hasattr(cls, "inner")
            or not hasattr(cls, "dims")
            or not hasattr(cls, "checker")
        ):
            raise TypinoxAnnotationError(
                "Invalid `Vmapped` class; must have `inner`, `dims` and `checker` attributes."
            )
        single_memo, variadic_memo, pytree_memo, arg_memo = get_shape_memo()
        single_memo_bak = single_memo.copy()
        variadic_memo_bak = variadic_memo.copy()
        pytree_memo_bak = pytree_memo.copy()
        arg_memo_bak = arg_memo.copy()

        try:
            check = instancecheck_vmapped(
                cls.inner,  # type: ignore
                cls.dims,  # type: ignore
                cls.checker,  # type: ignore
                obj,
                single_memo,
                arg_memo,
            )
        except Exception as e:
            set_shape_memo(
                single_memo_bak,
                variadic_memo_bak,
                pytree_memo_bak,
                arg_memo_bak,
            )
            raise e
        if check == "":
            return check
        else:
            set_shape_memo(
                single_memo_bak,
                variadic_memo_bak,
                pytree_memo_bak,
                arg_memo_bak,
            )
            return check

    def __repr__(cls):
        return cls.__module__ + "." + cls.__qualname__

    def __str__(cls):
        return cls.__module__ + "." + cls.__qualname__


class AbstractVmapped(metaclass=VmappedMeta):
    inner: type
    dim_str: str
    dims: tuple[tuple, tuple]
    checker: Callable
    base_name: str

    @classmethod
    def replace_inner(cls, inner):
        return create_vmapped_class(
            cls.base_name, inner, cls.dim_str, cls.dims, cls.checker
        )


@ft.cache
def create_vmapped_class(base_name, inner, dim_str, dims, checker):
    name = f"{base_name}[{inner}, {dim_str}]"
    cls = VmappedMeta(
        name,
        (AbstractVmapped,),
        dict(
            inner=inner,
            dim_str=dim_str,
            dims=dims,
            checker=checker,
            base_name=base_name,
        ),
    )
    cls.__module__ = "typinox"
    return cls


def parse_dims(dim_str: str):
    dims = []
    for index, elem in enumerate(dim_str.split()):
        anonymous = False
        vmapped = False
        if "," in elem and "(" not in elem:
            # Common mistake.
            # Disable in the case that there's brackets to allow for function calls,
            # e.g. `min(foo,bar)`, in symbolic axes.
            raise TypinoxAnnotationError(
                "Axes should be separated with spaces, not commas"
            )
        if elem == "...":
            raise TypinoxAnnotationError(
                "jaxtyping multiple axis not supported in Vmapped; "
                "`...` is not allowed"
            )
        while True:
            if len(elem) == 0:
                # This branch needed as just `_` or `$` is valid
                break
            first_char = elem[0]
            if first_char == "#":
                raise TypinoxAnnotationError(
                    "jaxtyping broadcastable annotation is unsupported in Vmapped; "
                    "`#foo` is not allowed"
                )
            elif first_char == "*":
                raise TypinoxAnnotationError(
                    "jaxtyping multiple axis annotation is unsupported in Vmapped; "
                    "`*foo` is not allowed"
                )
            elif first_char == "_":
                if anonymous:
                    raise TypinoxAnnotationError(
                        "Do not use _ twice to denote anonymity, e.g. `__foo` "
                        "is not allowed"
                    )
                anonymous = True
                elem = elem[1:]
            elif first_char == "?":
                raise TypinoxAnnotationError(
                    "jaxtyping treepath-dependent annotation is unsupported in Vmapped; "
                    "`?foo` is not allowed"
                )
            elif first_char == VMAPPED_LETTER:
                if vmapped:
                    raise TypinoxAnnotationError(
                        "Do not use "
                        + VMAPPED_LETTER
                        + " twice to denote vmapped axes, e.g. `"
                        + VMAPPED_LETTER
                        + VMAPPED_LETTER
                        + "` is not allowed"
                    )
                vmapped = True
                elem = elem[1:]
            elif elem.count("=") == 1:
                _, elem = elem.split("=")
            else:
                break
        elem_size = 0
        if len(elem) == 0 or elem.isidentifier():
            dim_type = _DimType.named
        else:
            try:
                elem_size = int(elem)
            except ValueError:
                dim_type = _DimType.symbolic
            else:
                dim_type = _DimType.fixed

        out: _FixedDim | _NamedDim | _SymbolicDim | object
        if dim_type is _DimType.fixed:
            if anonymous:
                raise TypinoxAnnotationError(
                    "Cannot have a fixed axis be anonymous, e.g. `_4` is not allowed."
                )
            if vmapped:
                raise TypinoxAnnotationError(
                    "Cannot have a fixed axis be vmapped, e.g. `"
                    + VMAPPED_LETTER
                    + "4` is not allowed."
                )
            out = _FixedDim(elem_size, False)
        elif dim_type is _DimType.named:
            if vmapped:
                out = _vmapped_dim
            elif anonymous:
                out = _anonymous_dim
            else:
                out = _NamedDim(elem, False, False)
        else:
            assert dim_type is _DimType.symbolic
            if anonymous:
                raise TypinoxAnnotationError(
                    "Cannot have a symbolic axis be anonymous, "
                    "e.g. `_foo+bar` is not allowed."
                )
            if vmapped:
                raise TypinoxAnnotationError(
                    "Cannot have a symbolic axis be vmapped, "
                    "e.g. `" + VMAPPED_LETTER + "foo+bar` is not allowed."
                )
            out = _SymbolicDim(elem, False)
        dims.append(out)
    n_vmapped_dims = sum(1 for dim in dims if dim is _vmapped_dim)
    if n_vmapped_dims > 1:
        raise TypinoxAnnotationError(
            "Only one axis can be marked as vmapped, e.g. `n "
            + VMAPPED_LETTER
            + " m p` is allowed, but `n "
            + VMAPPED_LETTER
            + " m "
            + VMAPPED_LETTER
            + " p` is not."
        )
    if n_vmapped_dims == 0:
        dims.append(_vmapped_dim)
    if len(dims) == 1:
        return None
    idx = dims.index(_vmapped_dim)
    left, right = dims[:idx], dims[idx + 1 :]
    return tuple(left), tuple(right)


@ft.cache
def make_vmapped(name, inner, dim_str, checker):
    dims = parse_dims(dim_str)
    if dims is None:
        return inner
    dim_left, dim_right = dims
    if (
        inner is not None
        and isinstance(inner, type)
        and issubclass(inner, AbstractVmapped)
    ):
        old_inner, (old_left, old_right) = inner.inner, inner.dims
        dim_left = dim_left + old_left
        dim_right = old_right + dim_right
        inner = old_inner

    return create_vmapped_class(
        name, inner, dim_str, (dim_left, dim_right), checker
    )


def get_vmapped_origin_or_none(cls):
    if not isinstance(cls, type):
        return None
    if not issubclass(cls, AbstractVmapped):
        return None
    return cls.inner


class VmappedHelperMeta(type):
    def __instancecheck__(cls, obj) -> NoReturn:
        raise TypinoxAnnotationError(
            "Do not use `Vmapped` as a type hint without specifying"
            " the PyTree structure and the vmapped dimension."
        )

    def __getitem__(cls, params):
        if not isinstance(params, tuple) or len(params) != 2:
            raise TypinoxAnnotationError(
                "Vmapped type hint must be a tuple of a PyTree structure and a string."
            )
        checker = getattr(cls, "checker", isinstance)
        inner, dim_str = params
        dim_str = dim_str.strip()
        return make_vmapped(cls.__qualname__, inner, dim_str, checker)


class Vmapped(metaclass=VmappedHelperMeta):
    checker = isinstance


class VmappedT(metaclass=VmappedHelperMeta):
    checker = is_bearable
