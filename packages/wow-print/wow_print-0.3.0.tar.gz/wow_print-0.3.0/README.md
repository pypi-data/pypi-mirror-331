# wow-print

A Python package that allows you to colorize text by specifying HEX colors.

## Installation

You can install this package via pip:

```bash
pip install wow-print
```

## Usage
```python

from wow_print import color_print as cprint

# Print text with a red foreground color and bold styling using inline tags
cprint("[red][bold] Hello, World![reset]")

# Print text with a custom purple background and italic styling
# Use double brackets `[[ ]]` for background colors
cprint("[[#d143b8]] Hello[reset], [cyan][italic] World![reset]")

# Print text with function arguments, overriding inline tags
cprint("Hello, World!", fg="cyan", bold=True, frame=True)

# Print text exactly as written, including inline tags
# Use exclamation marks `!` to mark it as ignored styling
cprint("My favorite color is [!#ff0000] and [!blue]")
```

## License
This project is licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0). See the LICENSE file for more details.

## Contributing
Feel free to fork the repository and submit pull requests. If you encounter bugs or have feature requests, please open an issue.