# pathio

Path collection class for checking paths for input and output files/directories.

- Initializing a collection (and later path additions) runs the suite of checks:
  - Duplication, existence (inputs), ... TODO add all checks
- Printing/logging the collection provides a summary of the paths. 
- Paths are converted to `pathlib.Path` objects and missing directories can be created.
- Can create missing output directories.

> https://pypi.python.org/pypi/pathio/


# Installation

Install from PyPI:

```shell
pip install pathio
```

Install from GitHub:

```shell
python -m pip install git+https://github.com/ludvigolsen/pathio
```


# Main class/functions

| Class/Function | Description                                           |
| :------------- | :---------------------------------------------------- |
| `IOPaths`      | Collection of paths with built-in checks.             |
| `mk_dir`       | Wrapper for creating directory if it doesn't exist.   |
| `rm_dir`       | Wrapper for removing directory with relevant options. |


# Examples

Initialize the collection of path collections. Often the paths come from input arguments (like via `argparse`).
Additional paths can be added later with `set_path()` or `set_paths()`.


```python
# Create path collection
paths = IOPaths(
    in_files={
        "in_file": "../dir1/dir2/john.csv",
        "stream_in": "-"
    },
    in_dirs={
        "in_dir": "../dir1/dir2/",
    },
    out_files={
        "out_file": "../dir1/dir2/output/no_john.csv"
    },
    out_dirs={
        "out_path": "../dir1/dir2/output/"
    }
)
```

Add additional path. Reruns checks to ensure consistency.

```python
paths.set_path(
    name="in_file_2",
    path="../dir1/dir2/dennis.csv",
    collection="in_files"
)
```

Or set multiple at a time to avoid rerunning checks unnecessarily:

```python
paths.set_paths(
    paths={
        "out_file_2": "../dir1/dir2/output/no_dennis.csv"
        "out_file_3": "../dir1/dir2/output/readme.txt"
    },
    collection="out_files"
)
```

Create the output directories that do not exist:

```python
paths.mk_output_dirs(collection="out_dirs")
```

Get a path:

```python
paths["in_file"]  # or
paths.get_path(name="in_file", as_str=False, raise_on_fail=True)
```

Remove file from disk:

```python
paths.rm_file(name="in_file")
```

Update collection with another `IOPaths` collection.
The sub collections are simple dicts, why this is just dict.update()
on each sub collection.

```python
paths.update(other=other_paths)
```

Find the combinations of keys and paths in the collections of this object
that are not in the collections of another object:

```python
paths.difference(other=other_paths)
```
