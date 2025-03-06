# Open Windsurf

<div align="center">

![Windsurf](https://img.shields.io/badge/Windsurf-IDE-007ACC?style=for-the-badge&logo=visual-studio-code&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Poetry](https://img.shields.io/badge/Poetry-Package-60A5FA?style=for-the-badge&logo=poetry&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)
![Generated](https://img.shields.io/badge/Generated_by-Sonnet_3.7-FF5A00?style=for-the-badge&logo=codeium&logoColor=white)

A simple utility to open multiple Windsurf (VS Code-based) instances for different directories/paths.

[Features](#features) •
[Installation](#installation) •
[Usage](#usage) •
[Examples](#examples) •
[Options](#options)

</div>

## ✨ Features

<div align="center">

🚀 **Multiple Instances** - Open different projects in separate Windsurf windows  
🔍 **Path Validation** - Automatically checks if paths exist  
⚙️ **Flexible Options** - Supports profiles, custom data directories, and more  
💻 **Simple Interface** - Easy to use command-line tool  
📦 **Poetry Package** - Easy installation and dependency management

</div>

## 📦 Installation

<div align="center">

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/open-windsurf.git
cd open-windsurf

# Install with Poetry
poetry install

# Activate the virtual environment
poetry shell
```

### Using pip (once published)

```bash
pip install open-windsurf
```

</div>

## 🚀 Usage

<div align="center">

### When installed with Poetry

```bash
# Within Poetry shell
open-windsurf PATH1 PATH2 PATH3 ...

# Or using Poetry run
poetry run open-windsurf PATH1 PATH2 PATH3 ...
```

### When installed with pip

```bash
open-windsurf PATH1 PATH2 PATH3 ...
```

</div>

## 📋 Examples

<div align="center">

### Open two separate Windsurf instances for different projects:

```bash
open-windsurf ~/projects/project1 ~/projects/project2
```

### Open multiple projects with a specific profile:

```bash
open-windsurf --profile coding ~/projects/project1 ~/projects/project2
```

### Open multiple projects and wait for all instances to close:

```bash
open-windsurf --wait ~/projects/project1 ~/projects/project2
```

</div>

## ⚙️ Options

<div align="center">

| Option | Description |
|--------|-------------|
| `--wait` | Wait for all Windsurf instances to close before exiting |
| `--user-data-dir DIR` | Specify a custom user data directory for all instances |
| `--profile PROFILE` | Use a specific profile for all instances |
| `--new-window` | Force opening in new windows |

</div>

## 📋 Requirements

<div align="center">

- Python 3.8+
- Windsurf installed and available in your PATH
- Poetry (for development)

</div>

## 🛠️ Development

<div align="center">

```bash
# Clone the repository
git clone https://github.com/yourusername/open-windsurf.git
cd open-windsurf

# Install development dependencies
poetry install

# Run tests
poetry run pytest

# Format code
poetry run black open_windsurf
poetry run isort open_windsurf
```

</div>

---

<div align="center">

**Generated with ❤️ by [Windsurf](https://codeium.com/windsurf) and [Sonnet 3.7](https://codeium.com/sonnet)**

<sub>Created on March 5, 2025</sub>

</div>
