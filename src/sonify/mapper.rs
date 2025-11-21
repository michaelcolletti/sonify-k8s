/// Metrics to sound mapping logic
use crate::error::{Result, SonifyError};
use crate::sonify::sound_map::{get_sound_map, MetricConfig};
use std::collections::HashMap;

/// Calculate the index for selecting a note based on a metric value
pub fn calculate_index(value: f64, notes_length: usize, min_value: f64, max_value: f64) -> usize {
    if max_value <= min_value {
        return 0;
    }

    let clamped_value = value.max(min_value).min(max_value);
    let normalized_value = (clamped_value - min_value) / (max_value - min_value);
    let index = (normalized_value * (notes_length - 1) as f64) as usize;

    index.min(notes_length - 1)
}

/// Get the color from a color list, handling out-of-bounds indices
pub fn get_color(color_list: &[String], index: usize) -> String {
    if index < color_list.len() {
        color_list[index].clone()
    } else if !color_list.is_empty() {
        color_list[color_list.len() - 1].clone()
    } else {
        "#808080".to_string() // Default gray
    }
}

/// Map a metric value to frequency and color
pub fn map_metric(
    metric_name: &str,
    value: f64,
    sound_map: &HashMap<String, MetricConfig>,
) -> Result<(u32, String, String)> {
    let config = sound_map
        .get(metric_name)
        .ok_or_else(|| SonifyError::InvalidMetric(metric_name.to_string()))?;

    let index = if metric_name == "pod_status" || metric_name == "node_pressure" {
        value as usize
    } else {
        let max_value = match metric_name {
            "http_latency" => 500.0,
            "errors_per_second" => 10.0,
            "replicas" => 5.0,
            _ => 100.0, // cpu_usage, memory_usage
        };
        calculate_index(value, config.notes.len(), 0.0, max_value)
    };

    let index = index.min(config.notes.len() - 1);
    let note = &config.notes[index];
    let color = get_color(&config.colors, index);

    Ok((note.frequency, note.name.clone(), color))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_calculate_index_bounds() {
        assert_eq!(calculate_index(0.0, 8, 0.0, 100.0), 0);
        assert_eq!(calculate_index(100.0, 8, 0.0, 100.0), 7);
        assert_eq!(calculate_index(50.0, 8, 0.0, 100.0), 3);
    }

    #[test]
    fn test_calculate_index_clamping() {
        assert_eq!(calculate_index(-10.0, 8, 0.0, 100.0), 0);
        assert_eq!(calculate_index(110.0, 8, 0.0, 100.0), 7);
    }

    #[test]
    fn test_calculate_index_edge_case() {
        assert_eq!(calculate_index(10.0, 5, 10.0, 10.0), 0);
    }

    #[test]
    fn test_get_color_in_bounds() {
        let colors = vec!["#111111".to_string(), "#222222".to_string(), "#333333".to_string()];
        assert_eq!(get_color(&colors, 1), "#222222");
    }

    #[test]
    fn test_get_color_out_of_bounds() {
        let colors = vec!["#111111".to_string(), "#222222".to_string(), "#333333".to_string()];
        assert_eq!(get_color(&colors, 10), "#333333");
    }

    #[test]
    fn test_get_color_empty() {
        let colors: Vec<String> = vec![];
        assert_eq!(get_color(&colors, 0), "#808080");
    }
}
