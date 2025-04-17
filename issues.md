"""
Renders ASCII text output with each line colored according to a specified color code.
This feature allows the outputted ASCII art or text to display with line-specific colors,
enhancing visual distinction and accessibility.

Features:
- Accepts a mapping of line numbers to color codes (ANSI escape codes or similar).
- Applies the corresponding color code to each line of ASCII text during rendering.
- Falls back to a default color if a line does not have a specified color code.

Usage:
    render_colored_ascii(ascii_lines: List[str], line_colors: Dict[int, str]) -> None

Args:
    ascii_lines: List of strings, each representing a line of ASCII text.
    line_colors: Dictionary mapping line indices (int) to color codes (str).

Example:
    ascii_lines = [
        "  ____  ",
        " / __ \\ ",
        "| |  | |"
    ]
    line_colors = {
        0: "\033[91m",  # Red
        1: "\033[92m",  # Green
        2: "\033[94m"   # Blue
    }
    render_colored_ascii(ascii_lines, line_colors)

Note:
- Color codes should be valid ANSI escape sequences for terminal output.
- Remember to reset color after each line (e.g., with "\033[0m").
"""