# filesize CLI

![PyPI - Version](https://img.shields.io/pypi/v/filesize-cli) ![GitLab Release](https://img.shields.io/gitlab/v/release/thaikolja%2Ffilesize-cli) ![PyPI - Downloads](https://img.shields.io/pypi/dm/filesize-cli) ![GitLab Last Commit](https://img.shields.io/gitlab/last-commit/thaikolja%2Ffilesize-cli) ![GitLab Stars](https://img.shields.io/gitlab/stars/thaikolja%2Ffilesize-cli?style=flat&color=yellow)

**filesize CLI** is a simple yet useful command-line tool written in Python. Using the `filesize` command, you can see the size of a file or directory right in your CLI (e.g., `12.4 MB`). It works for singular and multiple files and directories. **filesize CLI** can be installed easily on Windows, macOS, and Linux via Homebrew, pip (in a virtual environment), or pipx`.

**Table of Contents**

[TOC]

## ✨ Features

- **Multi-Unit Support:** Display file sizes in Bytes (B), Kilobytes (KB), Megabytes (MB), Gigabytes (GB), or Terabytes (TB).
- **Customizable Conversion Rate:** Specify a custom conversion rate (default is 1000).
- **Pretty Print Option:** Toggle between plain output and formatted output with unit labels.
- **Cross-Platform Compatibility:** Works seamlessly on Windows, macOS, and Linux.
- **Easy Installation:** Install globally using `pip` for universal access.

## 🔧 Requirements

1. Python 3.6 or above

## 🛠️ Installation

For all installation methods, make sure you have Python 3.6 or above running. Check this in your CLI with `python --version`. If you don't have Python, follow the steps under "Get Python".

### Using `pip` in Virtual Environments (Recommended)

This method is recommended if you use a Python virtual environment.

1. Create your virtual Python environment (e.g., `python -m venv venv`)
2. Activate it by entering `source venv/bin/activate`
3. Install `pip install -r requirements.txt`.

The command `filesize` is now available in your environment.

### Using `pipx` for system-wide installations (only macOS)

If you use macOS and want to use **filesize CLI** globally, you must install `pipx` via Homebrew.

1. Download and install Homebrew (if not done)
2. Run `pipx install filesize-cli`

That's it!

### Build from Source

If you prefer to install **filesize CLI** from the source repository, follow these steps:

1. **Clone the Repository**

   ```bash
   git clone https://gitlab.com/thaikolja/filesize-cli.git
   cd filesize-cli
   ```

2. **Install the Package**

   ```bash
   pip install -r requirements.txt
   ```

3. **Verify Installation** (optional)

   ```bash
   filesize --help
   ```

## 🚀 Usage

The `filesize` command allows you to view the size of a specified file in your desired unit. Below are the options and examples to help you get started.

### Options

- `-u`, `--unit`: *string* (Optional) Unit to display the file size in. **Default:** `auto`
   1. `b`: Bytes
   2. `kb`: Kilobytes
   3. `mb`: Megabytes
   4. `gb`: Gigabytes
   5. `tb`: Terabytes
   6. `auto`: Determines the unit automatically based on its size
- `-r`, `--rate`: *int* (Optional) Conversion rate of the file size. **Default:** `1000`
  1. e.g., `1024`
- `-q`, `--quiet`: *string* **Description:** If enabled, only the filesize will be returned without size units. **Default:** *Deactivated*

### Examples

#### 1. Show File Size with Auto Unit Detection

```bash
filesize examples/image.jpg
```

**Output:**

```bash
191.50 KB
```

#### 2. Display Size in Kilobytes

```bash
filesize --unit mb examples/image.jpg
```

**Output:**

```bash
0.19 MB
```

#### 3. Display Size in Bytes Without Size Unit

```bash
filesize --unit b --quiet examples/base64.txt
```

**Output:**
```bash
65
```

#### 4. Use a Custom Conversion Rate

```bash
filesize --unit mb --rate 1024 examples/video.mp4
```

**Output:**

```bash
0.18 MB
```

## 🐍 Get Python

In case you don't have Python, follow these steps.

- **Windows:**

  - Download and install Python from the [official website](https://www.python.org/downloads/windows/).
  - Ensure that Python is [added](https://learn.microsoft.com/en-us/previous-versions/office/developer/sharepoint-2010/ee537574(v=office.14)) to your system's `PATH` during installation.

- **macOS:**

  - Python 3 is pre-installed on newer versions. If not, install it via [Homebrew](https://brew.sh/):

    ```bash
    brew install python
    ```

- **Linux:**

  - Python 3 can be installed via your [distribution's package manager](https://www.geekboots.com/story/list-of-linux-package-manager-and-their-utility), but should be pre-installed for most distributions. For example, on Ubuntu:

    ```bash
    sudo apt update
    sudo apt install python3 python3-pip
    ```

## 🧪 Testing

Ensuring the reliability and correctness of `filesize-cli` is paramount. The project includes a comprehensive test suite using `pytest`.

### Running Tests

1. **Clone the Repository (if not already done)**

   ```bash
   git clone https://gitlab.com/thaikolja/filesize-cli.git
   cd filesize-cli
   ```

2. **Create and Activate a Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   pip install .
   ```

4. **Run Tests**

   ```bash
   pytest
   ```

### Test Structure

Tests are located in the `tests/` directory and cover various scenarios. Run them with `pytest tests/test_*.py`

## 🤝 Contributing

Contributions are welcome! Whether it's reporting a bug, suggesting a feature, or submitting a pull request, your input helps improve **filesize CLI**.

### Steps to Contribute

1. **Fork the Repository**

   Click the "Fork" button on the [GitLab repository](https://gitlab.com/thaikolja/filesize-cli) to create your own copy.

2. **Clone Your Fork**

   ```bash
   git clone https://gitlab.com/thaikolja/filesize-cli.git
   cd filesize-cli
   ```

3. **Create a New Branch**

   ```bash
   git checkout -b feature/YourFeatureName
   ```

4. **Make Your Changes**

   Implement your feature or fix bugs.

5. **Commit Your Changes**

   ```bash
   git commit -m "Add feature: YourFeatureName"
   ```

6. **Push to Your Fork**

   ```bash
   git push origin feature/YourFeatureName
   ```

7. **Submit a Merge Request**

   Go to the original repository and create a merge request from your fork.

## 🧑‍💻 Authors and Contributors

1. **Kolja Nolte** (kolja.nolte@gmail.com )

## 📜 License

This project is licensed under the [MIT License](LICENSE).

## 📅 Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed information about changes.
