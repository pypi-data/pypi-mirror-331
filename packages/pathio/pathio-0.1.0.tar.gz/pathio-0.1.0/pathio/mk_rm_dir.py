import pathlib
import shutil
from typing import Callable, Optional, Union


def mk_dir(
    path: Union[str, pathlib.Path],
    arg_name: Union[str, None] = "",
    raise_on_exists: bool = False,
    log_fn: Optional[Callable] = print,
):
    """
    Make directory if it doesn't exist.

    Parameters
    ----------
    path : str or `pathlib.Path`
        Path to directory to make.
    arg_name : str or None
        Name of path argument/variable for the log message
        when creating a directory and a `log_fn` is specified.
    raise_on_exists : bool
        Whether to raise a `FileExistsError` when the directory already exists.
    log_fn : Callable or None
        A function/method for printing/logging/... information.
        When `None`, no printing/logging is performed.
    """
    path = pathlib.Path(path)
    path_exists = path.exists()

    # Prepare arg name
    arg_name = _prep_arg_name(arg_name)

    # Check log_fn (always returns callable)
    log_fn = check_log_fn(log_fn)

    # Fail for existing directory (when specified)
    # Or exit function
    if path_exists:
        if raise_on_exists:
            raise FileExistsError(
                f"{arg_name}directory already exists: {path.resolve()}"
            )
        return

    # Message user about the creation of a new directory
    log_fn(f"{arg_name}directory does not exist and will be created: {path.resolve()}")

    # Create new directory if it does not already exist
    try:
        path.mkdir(parents=True, exist_ok=not raise_on_exists)
    except FileExistsError:
        # In this case, the directory was likely created between
        # our existence check and our creation attempt
        if raise_on_exists:
            raise FileExistsError(
                f"{arg_name}directory already exists: {path.resolve()}"
            )


def rm_dir(
    path: Union[str, pathlib.Path],
    arg_name: Union[str, None] = "",
    raise_missing: bool = False,
    raise_not_dir: bool = True,
    shutil_ignore_errors: bool = False,
    shutil_onerror: Optional[Callable] = None,
    log_fn: Optional[Callable] = print,
):
    """
    Remove directory and its contents if it exists using `shutil.rmtree()`.

    Parameters
    ----------
    path : str or `pathlib.Path`
        Path to directory to remove.
    arg_name : str or None
        Name of path argument/variable for the log message
        when creating a directory and a `log_fn` is specified.
    raise_missing : bool
        Whether to raise a RuntimeError when the directory does not exist.
    raise_not_dir : bool
        Whether to raise a RuntimeError when the path is not to a directory.
    shutil_ignore_errors : bool
        Passed to the `ignore_errors` argument in `shutil.rmtree()`.
    shutil_onerror : bool
        Passed to the `onerror` argument in `shutil.rmtree()`.
    log_fn : Callable or None
        A function/method for printing/logging/... information.
        When `None`, no printing/logging is performed.
    """
    path = pathlib.Path(path)
    path_exists = path.exists()

    # Prepare arg name
    arg_name = _prep_arg_name(arg_name)

    # Check log_fn (always returns callable)
    log_fn = check_log_fn(log_fn)

    if raise_missing and not path_exists:
        raise RuntimeError(f"{arg_name}path did not exist: {path}")

    if path_exists and raise_not_dir and not path.is_dir():
        raise RuntimeError(f"{arg_name}path was not a directory: {path}")

    if path_exists and path.is_dir():
        # Message user about the removal of the directory
        log_fn(f"{arg_name}directory will be removed: {path.resolve()}")
        shutil.rmtree(path, ignore_errors=shutil_ignore_errors, onerror=shutil_onerror)


def _prep_arg_name(arg_name):
    if arg_name is None or not arg_name:
        arg_name = ""
    else:
        arg_name = f"`{arg_name}` "
    return arg_name


def identity(*args, **kwargs):
    """
    Returns the provided arguments as-is, adapting the output format based on input.

    Parameters
    ----------
    *args: tuple
        Positional arguments.
    **kwargs: dict
        Keyword arguments.

    Returns
    -------
    result: tuple, dict, or single value
        - A single value if one positional argument is provided.
        - A tuple if multiple positional arguments are provided.
        - A dictionary if only keyword arguments are provided.
        - A tuple of (args, kwargs) if both are provided.
        - None if no arguments are provided.
    """
    if args and kwargs:
        return args, kwargs
    if args:
        return args if len(args) > 1 else args[0]
    if kwargs:
        return kwargs
    return None  # or return an empty tuple/dict if you prefer


def check_log_fn(log_fn: Optional[Callable]) -> Callable:
    """
    Check that `log_fn` is a callable function/method or `None`.
    In the latter case an identity function with no side effects is returned.

    Parameters
    ----------
    log_fn : Callable or None
        A logging function instance to check.
        Or `None`, in which case an identity function with no side effects is returned.

    Returns
    -------
    Callable
    """
    # Check the logging function
    if log_fn is None:
        return identity
    if not callable(log_fn):
        raise TypeError("`log_fn` was not callable.")
    return log_fn
