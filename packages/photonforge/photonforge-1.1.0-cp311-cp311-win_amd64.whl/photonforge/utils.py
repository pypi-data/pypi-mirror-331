from .extension import (
    Component,
    config,
    Expression,
    MaskSpec,
    Path,
    PoleResidueMatrix,
    PortSpec,
    Rectangle,
    Technology,
    _component_registry,
    _technology_registry,
)

import base64
import functools
import hashlib
import warnings
from typing import Callable, Optional, Sequence, Any, Union


# Speed of light in vacuum (in µm/s)
C_0: float = 2.99792458e14

_warnings_cache: set = set()

_gdsii_safe_chars: set[str] = set(
    "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_?$"
)


def _safe_hash(b: bytes) -> str:
    # Remove 4 bytes of padding at the end and use a case-insensitive alphabet
    return base64.b32encode(hashlib.sha256(b).digest())[:-4].decode("utf-8")


# Tidy3D limits the path name to 100 characters, but the ui also appends the timestamp
def _filename_cleanup(s: str, strict: bool = True, max_length: int = 64) -> str:
    if strict:
        allowed = set("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ()-._~")
    else:
        allowed = set(
            "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!#$%&'()+,-.;=@[]^_`{}~ "
        )
    result = ("".join(c if c in allowed else "" for c in s)).strip()
    if max_length > 0:
        result = result[:max_length]
    return result


def _make_str(x: Any) -> str:
    return (
        f"{x.__name__}${hash(x)}"
        if callable(x) and not isinstance(x, (PoleResidueMatrix, Expression))
        else str(x)
    )


def _suffix_from_args(*args, **kwargs) -> str:
    suffix = ""
    args_suffix = "_".join(_make_str(x) for x in args)
    if len(args_suffix) > 0:
        suffix += "_" + args_suffix
    kwargs_suffix = "_".join(f"{k}={_make_str(kwargs[k])}" for k in sorted(kwargs))
    if len(kwargs_suffix) > 0:
        suffix += "_" + kwargs_suffix
    if len(suffix) > 53:  # 1 + length of _safe_hash return value
        return "_" + _safe_hash(suffix[1:].encode("utf-8"))
    return suffix


def parametric_component(
    decorated_function: Optional[Callable] = None,
    name_prefix: Optional[str] = None,
    gdsii_safe_name: bool = True,
    use_parametric_cache_default: bool = True,
) -> Callable:
    """Decorator to create parametric components from functions.

    If the name of the created component is empty, this decorator sets it
    with name prefix and the values of the function arguments when called.

    Components can be cached to avoid duplication. They are cached based on
    the calling arguments (specifically, argument ``id``). Regardless of the
    default setting, each component can use or skip caching by setting the
    ``bool`` keyword argument ``use_parametric_cache`` in the decorated
    function call.

    Args:
        decorated_function: Function that returns a Component.
        name_prefix: Prefix for the component name. If ``None``, the
          decorated function name is used.
        gdsii_safe_name: If set, only use GDSII-safe characters in the name
          (``name_prefix`` is not modified by this flag).
        use_parametric_cache_default: Controls the default caching behavior
          for the decorated function.

    Examples:
        >>> @parametric_component
        ... def straight(*, length, port_spec_name, technology):
        ...     port_spec = technology.ports[port_spec_name]
        ...     c = Component(technology=technology)
        ...     for layer, path in port_spec.get_paths((0, 0)):
        ...         c.add(layer, path.segment((length, 0)))
        ...     c.add_port(Port(center=(0, 0), input_direction=0, spec=port_spec))
        ...     c.add_port(Port(center=(length, 0), input_direction=180, spec=port_spec))
        ...     c.add_model(Tidy3DModel(port_symmetries=[(1, 0)]))
        ...     return c
        ...
        >>> technology = basic_technology()
        >>> component = straight(length=5, port_spec_name="Strip", technology=technology)
        >>> print(component.name)
        straight_10_Strip_Basic_Technology_1.0

        Caching behavior:

        >>> component1 = straight(length=2, port_spec_name="Strip", technology=technology)
        >>> component2 = straight(length=2, port_spec_name="Strip", technology=technology)
        >>> component3 = straight(
        ...     length=2, port_spec_name="Strip", technology=technology, use_parametric_cache=False
        ... )
        >>> component2 == component1
        True
        >>> component2 is component1
        True
        >>> component3 == component1
        True
        >>> component3 is component1
        False

    Note:
        It is generally a good idea to force parametric components to accept
        only keyword arguments (by using the ``*`` as first argument in the
        argument list), because those are stored for future updates of the
        created component with :func:`Component.update`.

    See also:
        `Custom Parametric Components
        <../guides/Custom_Parametric_Components.ipynb>`__
    """

    def _decorator(component_func):
        _cache = {}
        prefix = component_func.__name__ if name_prefix is None else name_prefix
        full_name = f"{component_func.__module__}.{component_func.__qualname__}"
        if full_name in _component_registry:
            warnings.warn(
                f"Component function '{full_name}' previously registered will be overwritten.",
                RuntimeWarning,
                2,
            )

        @functools.wraps(component_func)
        def _component_func(*args, **kwargs):
            if len(args) > 0:
                warning_key = ("Parametric component with args", full_name)
                if warning_key not in _warnings_cache:
                    _warnings_cache.add(warning_key)
                    warnings.warn(
                        f"Parametric component '{full_name}' called with positional arguments. "
                        "Positional arguments are not remembered in parametric updates.",
                        RuntimeWarning,
                        2,
                    )

            use_parametric_cache = kwargs.pop("use_parametric_cache", use_parametric_cache_default)

            c = component_func(*args, **kwargs)
            if not isinstance(c, Component):
                raise TypeError(
                    f"Updated object returned by parametric function '{full_name}' is not a "
                    "'Component' instance."
                )

            if not c.name:
                suffix = _suffix_from_args(*args, **kwargs)
                if gdsii_safe_name:
                    suffix = "".join(x if x in _gdsii_safe_chars else "_" for x in suffix)
                c.name = prefix + suffix

            c.parametric_function = full_name

            kwdefaults = (
                dict(component_func.__kwdefaults__)
                if hasattr(component_func, "__kwdefaults__") and component_func.__kwdefaults__
                else {}
            )
            kwdefaults.update(kwargs)
            c.parametric_kwargs = kwdefaults

            if use_parametric_cache:
                key = c.as_bytes
                if key in _cache:
                    cached = _cache[key]
                    if cached.as_bytes == key:
                        c = cached
                    else:
                        _cache[key] = c
                else:
                    _cache[key] = c
            return c

        _component_registry[full_name] = _component_func

        return _component_func

    if decorated_function:
        return _decorator(decorated_function)

    return _decorator


def parametric_technology(
    decorated_function: Optional[Callable] = None,
    name_prefix: Optional[str] = None,
    use_parametric_cache_default: bool = True,
) -> Callable:
    """Decorator to create parametric technologies from functions.

    If the name of the created technology is empty, this decorator sets it
    with name prefix and the values of the function arguments when called.

    Technologies can be cached to avoid duplication. They are cached based
    on the calling arguments (specifically, argument ``id``). Regardless of
    the default setting, each technology can use or skip caching by setting
    the ``bool`` keyword argument ``use_parametric_cache`` in the decorated
    function call.

    Args:
        decorated_function: Function that returns a Technology.
        name_prefix: Prefix for the technology name. If ``None``, the
          decorated function name is used.
        use_parametric_cache_default: Controls the default caching behavior
          for the decorated function.

    Example:
        >>> @parametric_technology
        ... def demo_technology(*, thickness=0.250, sidewall_angle=0):
        ...     layers = {
        ...         "Si": LayerSpec(
        ...             (1, 0), "Silicon layer", "#d2132e18", "//"
        ...         )
        ...     }
        ...     extrusion_specs = [
        ...         ExtrusionSpec(
        ...             MaskSpec((1, 0)),
        ...             td.Medium(permittivity=3.48**2),
        ...             (0, thickness),
        ...             sidewall_angle=sidewall_angle,
        ...         )
        ...     ]
        ...     port_specs = {
        ...         "STE": PortSpec(
        ...             "Single mode strip",
        ...             1.5,
        ...             (-0.5, thickness + 0.5),
        ...             target_neff=3.48,
        ...             path_profiles=[(0.45, 0, (1, 0))],
        ...         )
        ...     }
        ...     technology = Technology(
        ...         "Demo technology",
        ...         "1.0",
        ...         layers,
        ...         extrusion_specs,
        ...         port_specs,
        ...         td.Medium(permittivity=1.45**2),
        ...     )
        ...     # Add random variables to facilitate Monte Carlo runs:
        ...     technology.random_variables = [
        ...         monte_carlo.RandomVariable(
        ...             "sidewall_angle", value=sidewall_angle, stdev=2
        ...         ),
        ...         monte_carlo.RandomVariable(
        ...             "thickness",
        ...             value_range=[thickness - 0.01, thickness + 0.01],
        ...         ),
        ...     ]
        ...     return technology
        >>> technology = demo_technology(sidewall_angle=10, thickness=0.3)
        >>> technology.random_variables
        [RandomVariable('sidewall_angle', **{'value': 10, 'stdev': 2}),
         RandomVariable('thickness', **{'value_range': (0.29, 0.31)})]

    Note:
        It is generally a good idea to force parametric technologies to
        accept only keyword arguments (by using the ``*`` as first argument
        in the argument list), because those are stored for future updates
        of the created technology with :func:`Technology.update`.
    """

    def _decorator(technology_func):
        _cache = {}
        prefix = technology_func.__name__ if name_prefix is None else name_prefix
        full_name = f"{technology_func.__module__}.{technology_func.__qualname__}"
        if full_name in _technology_registry:
            warnings.warn(
                f"Technology function '{full_name}' previously registered will be overwritten.",
                RuntimeWarning,
                2,
            )

        @functools.wraps(technology_func)
        def _technology_func(*args, **kwargs):
            if len(args) > 0:
                warning_key = ("Parametric technology with args", full_name)
                if warning_key not in _warnings_cache:
                    _warnings_cache.add(warning_key)
                    warnings.warn(
                        f"Parametric technology '{full_name}' called with positional arguments. "
                        "Positional arguments are not remembered in parametric updates.",
                        RuntimeWarning,
                        2,
                    )

            use_parametric_cache = kwargs.pop("use_parametric_cache", use_parametric_cache_default)

            t = technology_func(*args, **kwargs)
            if not isinstance(t, Technology):
                raise TypeError(
                    f"Updated object returned by parametric function '{full_name}' is not a "
                    "'Technology' instance."
                )
            if not t.name:
                t.name = prefix + _suffix_from_args(*args, **kwargs)
            t.parametric_function = full_name

            kwdefaults = (
                dict(technology_func.__kwdefaults__)
                if hasattr(technology_func, "__kwdefaults__") and technology_func.__kwdefaults__
                else {}
            )
            kwdefaults.update(kwargs)
            t.parametric_kwargs = kwdefaults

            if use_parametric_cache:
                key = t.as_bytes
                if key in _cache:
                    cached = _cache[key]
                    if cached.as_bytes == key:
                        t = cached
                    else:
                        _cache[key] = t
                else:
                    _cache[key] = t
            return t

        _technology_registry[full_name] = _technology_func

        return _technology_func

    if decorated_function:
        return _decorator(decorated_function)

    return _decorator


def route_length(component: Component, layer: Optional[Sequence[int]] = None) -> float:
    """Measure the length of parametric routes.

    Internally, this funcions adds up the path lengths for all paths in the
    given component for a specific layer. If the component contains multiple
    paths, the sum of their lengths will be returned.

    Args:
        component: Component with routes to be measured.
        layer: Layer to be used to search for paths. If not set, all will be
          inspected and the largest length is returned.

    Returns:
        Total path length.

    See also:
        `Parametric routes <../parametric.rst#routing>`__
    """
    structures = component.get_structures(layer)
    if len(structures) == 0:
        return 0.0
    if layer is None:
        return max(
            sum(path.length() for path in structure_list if isinstance(path, Path))
            for structure_list in structures.values()
        )
    return sum(path.length() for path in structures if isinstance(path, Path))


def _layer_in_mask_score(layer, mask):
    if mask.layer is not None:
        return 1 if mask.layer == layer else None
    operands = mask.operand1 + mask.operand2
    if mask.operation == "+":
        for inner in operands:
            score = _layer_in_mask_score(layer, inner)
            if score is not None:
                return 10 * score + len(operands)
    elif mask.operation == "*":
        for inner in operands:
            score = _layer_in_mask_score(layer, inner)
            if score is not None:
                return 20 * score + len(operands)
    elif mask.operation == "-":
        for inner in mask.operand1:
            score = _layer_in_mask_score(layer, inner)
            if score is not None:
                return 20 * score + len(operands)
    return None


def cpw_spec(
    layer: Union[str, Sequence[int]],
    signal_width: float,
    gap: float,
    ground_width: Optional[float] = None,
    description: Optional[str] = None,
    width: Optional[float] = None,
    limits: Optional[Sequence[float]] = None,
    num_modes: int = 1,
    added_solver_modes: int = 0,
    target_neff: float = 4.0,
    gap_layer: Union[None, str, Sequence[int]] = None,
    include_ground: bool = True,
    conductor_limits: Optional[Sequence[float]] = None,
    technology: Technology = None,
) -> PortSpec:
    """Template to generate a coplanar transmission line PortSpec.

    Args:
        layer: Layer used for the transmission line layout.
        signal_width: Width of the central conductor.
        gap: Distance between the central conductor and the grounds.
        ground_width: Width of the ground conductors.
        description: Description used in :attr:`PortSpec.description`.
        width: Dimension used in :attr:`PortSpec.width`.
        limits: Vertical port limits used in :attr:`PortSpec.limits`.
        num_modes: Value used for :attr:`PortSpec.num_modes`.
        added_solver_modes: Value used for
          :attr:`PortSpec.added_solver_modes`.
        target_neff: Value used for :attr:`PortSpec.target_neff`.
        gap_layer: If set, path profiles for the gap region are included in
          this layer.
        include_ground: If ``False``, ground path profiles are not included.
        conductor_limits: Lower and upper bounds of the conductor layer
          extrusion.
        technology: Technology in use. If ``None``, the default is used.

    Returns:
        PortSpec for the CPW transmission line.

    Note:
        If ``conductor_limits`` is not given, the extrusion specifications
        in ``technology`` are inspected. If an specification for the
        selected ``layer`` is found, its extrusion limits are used.
    """
    if technology is None:
        technology = config.default_technology

    if isinstance(layer, str):
        layer = technology.layers[layer].layer
    if isinstance(gap_layer, str):
        gap_layer = technology.layers[gap_layer].layer

    if conductor_limits is None:
        best_score = 1e30
        ideal_mask = MaskSpec(layer)
        for extrusion in technology.extrusion_specs:
            if extrusion.mask_spec == ideal_mask:
                conductor_limits = extrusion.limits
                break

            score = _layer_in_mask_score(layer, extrusion.mask_spec)
            if score is not None and score < best_score:
                conductor_limits = extrusion.limits
                best_score = score

        if conductor_limits is None:
            raise RuntimeError(f"No usable extrusion specification found for layer {layer}.")

    z_center = 0.5 * (conductor_limits[0] + conductor_limits[1])
    z_thickness = abs(conductor_limits[1] - conductor_limits[0])
    cpw_min = min(signal_width, gap, z_thickness)
    cpw_max = max(signal_width, gap, z_thickness)

    if ground_width is None:
        ground_width = 2 * cpw_max

    offset = (signal_width + ground_width) / 2 + gap
    full_width = signal_width + 2 * gap + 2 * ground_width

    if description is None:
        description = f"CPW (signal width: {signal_width}, gap: {gap})"

    if width is None:
        width = min(full_width, signal_width + 2 * gap + 4 * cpw_max) - cpw_min
    elif width >= full_width:
        warnings.warn(
            "CPW width is larger than the ground conductor extension. Please increase "
            "'ground_width' or decrease 'width'."
        )

    if limits is None:
        z_margin = z_thickness / 2 + 2 * cpw_max
        limits = (z_center - z_margin, z_center + z_margin)

    path_profiles = {"signal": (signal_width, 0, layer)}
    if include_ground:
        path_profiles["gnd0"] = (ground_width, -offset, layer)
        path_profiles["gnd1"] = (ground_width, offset, layer)
    if gap_layer is not None:
        gap_offset = (signal_width + gap) / 2
        path_profiles["gap0"] = (gap, -gap_offset, gap_layer)
        path_profiles["gap1"] = (gap, gap_offset, gap_layer)

    return PortSpec(
        description=description,
        width=width,
        limits=limits,
        num_modes=num_modes,
        added_solver_modes=added_solver_modes,
        target_neff=target_neff,
        path_profiles=path_profiles,
        voltage_path=[(signal_width / 2 + gap, z_center), (signal_width / 2, z_center)],
        current_path=Rectangle(center=(0, z_center), size=(signal_width + gap, z_thickness + gap)),
    )
