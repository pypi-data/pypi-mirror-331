# SnapThing

:warn: This tool was developed for personal use and currently has only been tested on linux -- it can be made to work on mac and windows with some tinkering. If you'd like to try the tool
on mac or windows, please open an issue! Contributors are also welcome!

A tool for taking screenshots. A transparent window will open at your mouse cursor, from there you can re-size the window and move it around by dragging. Once placed
over the desired area, press `Enter/Return` to capture a screenshot to the clipboard.

## Usage

Set a global keybinding for the CLI command `snapthing` using your preferred tool, or simply run `snapthing` from the terminal.

### Keybindings

# Keyboard Shortcuts

| Action | Key |
|--------|-----|
| Copy Image | <kbd>Enter</kbd> |
| Exit | <kbd>Esc</kbd> or <kbd>q</kbd> |
| Resize Left | <kbd>Shift</kbd>+<kbd>H</kbd> or <kbd>Shift</kbd>+<kbd>←</kbd> |
| Resize Right | <kbd>Shift</kbd>+<kbd>L</kbd> or <kbd>Shift</kbd>+<kbd>→</kbd> |
| Resize Down | <kbd>Shift</kbd>+<kbd>J</kbd> or <kbd>Shift</kbd>+<kbd>↓</kbd> |
| Resize Up | <kbd>Shift</kbd>+<kbd>K</kbd> or <kbd>Shift</kbd>+<kbd>↑</kbd> |
| Move Left | <kbd>h</kbd> or <kbd>←</kbd> |
| Move Right | <kbd>l</kbd> or <kbd>→</kbd> |
| Move Down | <kbd>j</kbd> or <kbd>↓</kbd> |
| Move Up | <kbd>k</kbd> or <kbd>↑</kbd> |
| Copy OCR Text | <kbd>c</kbd> |
| Cycle Next Window Size | <kbd>Tab</kbd> |
| Cycle Previous Window Size | <kbd>Shift</kbd>+<kbd>Tab</kbd> |

## Installation 

```sh
pip install snapthing
```

### OCR - Optical Character Recognition

`snapthing` also supports using OCR to extract text from the selected area (using `tesseract`). Press `c` while the screenshot window is open to copy the extracted OCR text
to the clipboard. This feature requires that you have `tesseract` installed on your system path, as well as the required data package for your language. See the [tesseract docs](https://tesseract-ocr.github.io/tessdoc/Installation.html) for installation instructions. Without `tesseract` installed the OCR feature will be unavailible.


### Clipboard Access

`snapthing` uses external programs installed on your system path to interact with the system clipboard. On linux systems, `xclip` will need to be installed
in order for `snapthing` to work. When `mac` and `windows` support is added, they will use the specific programs availible for cliboard interaction.

#### Linux

On Linux, `snapthing` will use `xclip` to interact with the clipboard. Since installation instructions will vary per distribution, it's easiest just to do a search for 
"install xclip on <distro>" to find instructions specific to your distro. 

##### Debian/Ubuntu

```sh
sudo apt-get install xclip
```

##### Arch/Manjaro

```sh
sudo pacman -S xclip
```
