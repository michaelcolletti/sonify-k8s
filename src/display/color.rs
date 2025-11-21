/// ANSI color formatting for terminal output
use crossterm::style::Color;

/// Convert hex color to RGB values
pub fn hex_to_rgb(hex: &str) -> Option<(u8, u8, u8)> {
    let hex = hex.trim_start_matches('#');

    if hex.len() != 6 {
        return None;
    }

    let r = u8::from_str_radix(&hex[0..2], 16).ok()?;
    let g = u8::from_str_radix(&hex[2..4], 16).ok()?;
    let b = u8::from_str_radix(&hex[4..6], 16).ok()?;

    Some((r, g, b))
}

/// Colorize text using ANSI escape codes
pub fn colorize(text: &str, hex_color: &str, use_color: bool) -> String {
    if !use_color {
        return text.to_string();
    }

    if let Some((r, g, b)) = hex_to_rgb(hex_color) {
        format!("\x1b[38;2;{};{};{}m{}\x1b[0m", r, g, b, text)
    } else {
        text.to_string()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_hex_to_rgb() {
        assert_eq!(hex_to_rgb("#FF0000"), Some((255, 0, 0)));
        assert_eq!(hex_to_rgb("#00FF00"), Some((0, 255, 0)));
        assert_eq!(hex_to_rgb("#0000FF"), Some((0, 0, 255)));
        assert_eq!(hex_to_rgb("invalid"), None);
    }

    #[test]
    fn test_colorize_disabled() {
        let text = "Hello";
        let colored = colorize(text, "#FF0000", false);
        assert_eq!(colored, "Hello");
    }

    #[test]
    fn test_colorize_enabled() {
        let text = "Hello";
        let colored = colorize(text, "#FF0000", true);
        assert!(colored.contains("Hello"));
        assert!(colored.contains("\x1b["));
    }
}
