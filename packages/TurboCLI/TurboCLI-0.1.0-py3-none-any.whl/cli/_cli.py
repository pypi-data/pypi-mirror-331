def showhex(data: bytes) -> None:
    """Display a hex dump of the given bytes"""
    width = 16  # Number of bytes per line
    lines = []
    
    for i in range(0, len(data), width):
        chunk = data[i:i + width]
        hex_part = ' '.join(f"{b:02X}" for b in chunk)  # Convert bytes to hex
        ascii_part = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)  # Convert to ASCII
        lines.append(f"{i:08X}  {hex_part:<47}  {ascii_part}")

    print("\n".join(lines))

