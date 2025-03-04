# maamgr

`maamgr` is a command-line tool for managing MAA packages using the Scoop package manager.

## Installation

To install `maamgr`, you need to have Python 3.8 or higher installed. You can install `maamgr` using pip:

```sh
pip install maamgr
```

## Usage

`maamgr` provides several commands to manage MAA packages. Below are the available commands and their usage:

### maamgr

This is the main command to initialize and manage MAA packages.

```sh
maamgr [OPTIONS] NAME
```

#### Options

- `-u, --update`: Check for updates.

#### Arguments

- `NAME`: The name of the MAA package to manage.

### maamgr cat

Displays the contents of the MAA package.

```sh
maamgr cat
```

### maamgr start

Starts the MAA package.

```sh
maamgr start PATH
```

#### Arguments

- `PATH`: The path to the executable file of the MAA package.

### maamgr patch

Patches and saves data between files using path-based operations.

```sh
maamgr patch ARGS...
```

#### Arguments

- `ARGS`: Variable number of strings in the format `source->destination` where source and destination can include:
  - File paths with optional key paths (e.g., `path/to/file:key1/key2`)
  - Variable substitution using `{{var}}` syntax (e.g., `{{CONFIG}}/file.json`)

#### Examples

```sh
maamgr patch 'source.json:data->{{CONFIG}}/dest.json:new_data'
maamgr patch 'file1.json->file2.json'
maamgr patch 'file1.json:key1/key2->file2.json:new_key'
```

### maamgr kv

Patches a specific key-value pair in a file.

```sh
maamgr kv PATH KEY VALUE
```

#### Arguments

- `PATH`: The path to the file.
- `KEY`: The key to patch.
- `VALUE`: The new value to set.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.