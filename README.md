# Watermark

A cross-platform command-line utility for adding diagonal text watermarks to images. Compatible with Linux, macOS, and Windows.

## Features

- Add diagonal text watermarks to multiple images at once
- Customize watermark text, opacity, and size
- Save configuration for repeated use
- Batch process entire directories of images
- Supports various image formats (JPG, PNG, BMP, GIF, TIFF, WebP)
- Automatically finds system fonts
- Creates a separate output directory for watermarked images

## Installation

### Requirements

- Python 3.x
- Pillow (PIL) library

### Install Dependencies

```bash
pip install pillow
```

### Download

Clone or download this repository to your local machine.

### Making the Script Available as a Command

#### Linux

Method 1: Using `/usr/local/bin` (system-wide installation):
```bash
sudo cp watermark.py /usr/local/bin/watermark
sudo chmod +x /usr/local/bin/watermark
```

Method 2: Using `~/.local/bin` (user-specific installation):
```bash
mkdir -p ~/.local/bin
cp watermark.py ~/.local/bin/watermark
chmod +x ~/.local/bin/watermark
```
Make sure `~/.local/bin` is in your PATH by adding this line to your `~/.bashrc` or `~/.zshrc`:
```bash
export PATH="$HOME/.local/bin:$PATH"
```
Then reload your shell configuration:
```bash
source ~/.bashrc  # or source ~/.zshrc
```

#### macOS

Method 1: Using a personal bin directory (recommended):
```bash
# First, create a directory for your scripts if you don't have one
mkdir -p ~/bin

# Copy the script there
cp watermark.py ~/bin/watermark

# Make it executable
chmod +x ~/bin/watermark

# Add to PATH in your ~/.zshrc or ~/.bash_profile
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc

# Reload your shell configuration
source ~/.zshrc
```

Method 2: Using `/usr/local/bin`:
```bash
sudo cp watermark.py /usr/local/bin/watermark
sudo chmod +x /usr/local/bin/watermark
```

#### Windows

Method 1: Create a batch file wrapper:
1. Create a file named `watermark.bat` with the following content:
```batch
@echo off
python "C:\path\to\watermark.py" %*
```
2. Save this file to a location in your PATH (e.g., `C:\Windows` or create a custom folder and add it to PATH)

Method 2: Using Python's pip to install as a script:
1. Create a `setup.py` file in the same directory as your script:
```python
from setuptools import setup

setup(
    name="watermark",
    version="1.0",
    py_modules=["watermark"],
    install_requires=["pillow"],
    entry_points={
        "console_scripts": [
            "watermark=watermark:main",
        ],
    },
)
```
2. Install using pip:
```
pip install -e .
```

Method 3: Add the script's directory to PATH:
1. Right-click on "This PC" and select "Properties"
2. Click on "Advanced system settings"
3. Click on "Environment Variables"
4. Under "System variables" or "User variables", edit "Path"
5. Add the full path to the directory containing `watermark.py`
6. Create a batch file named `watermark.bat` in the same directory with:
```batch
@echo off
python watermark.py %*
```

## Usage

### Basic Usage

```bash
python watermark.py /path/to/images
```

This will watermark all images in the specified directory using your current configuration.

### View Current Configuration

```bash
python watermark.py --config
```

### Set Permanent Configuration

```bash
# Set watermark text
python watermark.py --set-text "Your Name\nCopyright 2025"

# Set opacity (0-100)
python watermark.py --set-opacity 25

# Set font size factor (higher numbers = smaller text)
python watermark.py --set-font-size-factor 6

# Set maximum text width relative to diagonal (0.1-1.0)
python watermark.py --set-max-text-width 0.7

# Set diagonal fill factor (0.1-1.0)
python watermark.py --set-diagonal-fill 0.8
```

### Override Configuration for a Single Run

```bash
python watermark.py /path/to/images -t "One-time Text" -o 50
```

### Command-Line Options

| Option | Long Option | Description |
|--------|-------------|-------------|
| `-t TEXT` | `--text TEXT` | Custom text for this run only |
| `-o N` | `--opacity N` | Opacity for this run only (0-100) |
| `-f N` | `--font-size-factor N` | Font size factor for this run only |
| `-w N` | `--max-text-width N` | Maximum text width for this run only (0.1-1.0) |
| `-d N` | `--diagonal-fill N` | Diagonal fill for this run only (0.1-1.0) |
| | `--config` | Show current configuration |
| | `--set-text TEXT` | Set permanent watermark text |
| | `--set-opacity N` | Set permanent opacity percentage |
| | `--set-font-size-factor N` | Set permanent font size factor |
| | `--set-max-text-width N` | Set permanent maximum text width |
| | `--set-diagonal-fill N` | Set permanent diagonal fill factor |

## Configuration Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `text` | The text to overlay on images | "Your Name\nMade by Natha Kusuma" |
| `opacity` | Transparency level (0-100) | 25 |
| `font_size_factor` | Controls text size (higher = smaller) | 6 |
| `max_text_width` | Maximum text width relative to diagonal | 0.7 |
| `diagonal_fill` | How much of the diagonal to fill | 0.8 |

Configuration is stored in `~/.watermark_config.json`.

## Examples

### Basic Watermarking

```bash
python watermark.py ~/Pictures/vacation
```

This will create a new directory `~/Pictures/vacation/watermarked_images/` containing all the watermarked images.

### Custom Watermark for a Portfolio

```bash
python watermark.py ~/Portfolio/photos -t "Jane Smith Photography\n© 2025" -o 30
```

### Changing the Default Configuration

```bash
python watermark.py --set-text "© Jane Smith\nwww.janesmith.com" --set-opacity 20
```

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- GIF (.gif)
- TIFF (.tiff)
- WebP (.webp)

## Cross-Platform Compatibility

This script is designed to work on all major operating systems:

- **Linux**: Full support for various distributions
- **macOS**: Full support for macOS systems
- **Windows**: Full support for Windows environments

The script automatically detects your operating system and looks for fonts in the appropriate system locations.

## Troubleshooting

### Font Issues

If you experience font issues, the script will attempt to use common system fonts in this order:
- Arial
- Helvetica
- Verdana
- Tahoma
- DejaVuSans
- FreeSans
- LiberationSans
- NotoSans

If none of these fonts are found, it will fall back to the default font.

### File Permissions

Ensure you have read permissions for the source images and write permissions for the output directory.

