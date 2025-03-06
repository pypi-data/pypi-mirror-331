# TypeSnatch

TypeSnatch is a command-line tool designed to help users search for, install, and manage fonts efficiently. It leverages the power of Python and several libraries to provide a seamless experience for font enthusiasts and developers alike.

*NOTE: This tool was largely generated using Aider and OpenAI GPT4o (I helped a little)*

## Features

- **Search Fonts**: Quickly search for fonts using a query string.
- **Install Fonts**: Easily install fonts directly from the command line.
- **Manage Fonts**: View and manage installed fonts.

## Installation

To install the TypeSnatch package and its dependencies, use `pip`:

```bash
pip install .
```

Ensure you have the latest version of `pip` installed.

This project uses [Poetry](https://python-poetry.org/) for dependency management. To set up the project, follow these steps:

1. **Install the Package**: Use `pip` to install the package and its dependencies.

   ```bash
   pip install .
   ```

2. **Install Playwright**: Playwright is used for browser automation and needs to be installed separately.

   ```bash
   playwright install
   ```

## Usage

After installing, you can use the `typesnatch` module. For example, to run the CLI:

```bash
typesnatch
```

### Commands

- **Search**: Use the `search` command to find fonts.

  ```bash
  typesnatch search <query>
  ```

- **Install**: Use the `install` command to install a font.

  ```bash
  typesnatch install <font-name>
  ```

- **List**: Use the `list` command to view all installed fonts.

  ```bash
  typesnatch list
  ```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
