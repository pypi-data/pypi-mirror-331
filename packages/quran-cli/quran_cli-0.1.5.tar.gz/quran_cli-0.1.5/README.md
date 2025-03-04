# Qur'an CLI

[![CI](https://github.com/youzarsiph/quran-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/youzarsiph/quran-cli/actions/workflows/ci.yml)
[![CD](https://github.com/youzarsiph/quran-cli/actions/workflows/cd.yml/badge.svg)](https://github.com/youzarsiph/quran-cli/actions/workflows/cd.yml)
[![Code Style: Black](https://github.com/youzarsiph/quran-cli/actions/workflows/black.yml/badge.svg)](https://github.com/youzarsiph/quran-cli/actions/workflows/black.yml)
[![Ruff](https://github.com/youzarsiph/quran-cli/actions/workflows/ruff.yml/badge.svg)](https://github.com/youzarsiph/quran-cli/actions/workflows/ruff.yml)

## Overview

The Qur'an CLI is a sophisticated command-line interface tool designed to facilitate advanced interactions with Qur'an data. It provides a comprehensive set of features for data exploration, manipulation, and exportation, making it an indispensable resource for scholars, researchers, and enthusiasts.

## Key Features

- **Intuitive User Interface**: Designed with ease-of-use in mind, offering intuitive commands and options.
- **Advanced Visualization**: Utilizes enhanced styling to improve readability and user experience.
- **CI/CD Integration**: Supports continuous integration and deployment pipelines to ensure reliability and consistency.
- **Automated Code Quality Assurance**: Employs automated linting and formatting tools to maintain high code quality standards.
- **Data Exportation**: Capable of exporting data into various formats, including CSV, JSON, and XML.
- **Database Initialization and Normalization**: Provides commands for initializing and maintaining Qur'an databases.

## Installation

To install the Qur'an CLI tool, execute the following command:

```bash
pip install quran-cli
```

## Usage

The Qur'an CLI offers a variety of commands to interact with and manage Qur'an data:

### General Command Syntax

```console
quran-cli [OPTIONS] COMMAND [ARGS]...
```

### Options

- `--install-completion`: Installs shell completion for the current shell environment.
- `--show-completion`: Displays shell completion for the current shell environment.
- `--help`: Displays help information for the tool and exits.

### Available Commands

- `explore`: Enables SQL-based querying of the Qur'an database.
- `export`: Exports Qur'an data in various formats, such as CSV, JSON, and XML.
- `init`: Initializes a new Qur'an database.
- `normalize`: Normalizes the structure and content of an existing database.

---

#### `explore`

Interact with the Qur'an database using SQL queries.

**Command Syntax:**

```console
quran-cli explore [OPTIONS] DATABASE
```

**Arguments:**

- `DATABASE`: Specifies the database file to query. `required`

**Examples:**

```bash
# Initialize a new database
quran-cli init db.sqlite3

# Explore the database using SQL queries
quran-cli explore db.sqlite3
```

---

#### `export`

Export Qur'an data to selected file formats.

**Command Syntax:**

```console
quran-cli export [OPTIONS] DATABASE
```

**Arguments:**

- `DATABASE`: Specifies the database file to export. `required`

**Options:**

- `-o, --output DIRECTORY`: Defines the output directory for the exported files. *default: quran*
- `-f, --format [csv|xml|json]`: Specifies the data format for exportation. *default: json*

**Examples:**

```bash
# Initialize a new database
quran-cli init db.sqlite3

# Normalize the database
quran-cli normalize db.sqlite3

# Export the normalized data to JSON format
quran-cli export db.sqlite3 -f json
```

---

#### `init`

Creates a new Qur'an database.

**Command Syntax:**

```console
quran-cli init [OPTIONS] DATABASE
```

**Arguments:**

- `DATABASE`: Specifies the name and path of the new database file. `required`

**Options:**

- `-v, --variant [simple-clean|simple-min|simple-plain|simple|uthmani|uthmani-min]`: Data variant to load. *default: uthmani*

**Examples:**

```bash
# Create a new database
quran-cli init db.sqlite3

# Create a new database with simple variant
quran-cli init db.sqlite3 -v simple
```

---

#### `normalize`

Normalizes the structure and content of an existing Qur'an database.

**Command Syntax:**

```console
quran-cli normalize [OPTIONS] DATABASE
```

**Arguments:**

- `DATABASE`: Specifies the database file to normalize. `required`

**Examples:**

```bash
# Normalize an existing database
quran-cli normalize db.sqlite3
```

## Contributing

We welcome contributions from the community. For guidelines on how to contribute, please refer to our [Contributing Guide](CONTRIBUTING.md).

## Code of Conduct

Please see our [Code of Conduct](CODE_OF_CONDUCT.md) for details on our standards for interactions within our project.

## License

The Qur'an CLI project is licensed under the MIT License. For detailed license information, please refer to the [LICENSE file](LICENSE) in this repository.

## Contact

For any inquiries, issues, or feedback, please contact us via:

- **Maintainer**: Yousuf Abu Shanab
- **GitHub Issues**: [Open an Issue](https://github.com/youzarsiph/quran-cli/issues)

We value your input and contributions to enhance the Qur'an CLI tool further.
