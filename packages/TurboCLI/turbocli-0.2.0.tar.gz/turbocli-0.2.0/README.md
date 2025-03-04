# TurboCLI

A simple Python package for displaying CLI Tools.

## Features:
- Show data as a hex editor.

## Example Usage:

```python
from TurboCLI import showhex

# Example byte sequence
data = b'\xde\xad\xbe\xef'

# Display the hex dump
showhex(data)
```
### Expected Output:
```
00000000  DE AD BE EF                                      ....
```
This will print out a hex dump where each line contains the offset (starting at `00000000`), the hexadecimal representation of the bytes, and their corresponding ASCII characters (non-printable characters are displayed as a dot).

## Lisence:
This project uses the MIT License.
##
Thank you for using the CLI Python module! 🎉