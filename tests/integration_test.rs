/// Integration tests for Sonify K8s
use sonify_k8s::sonify::{calculate_index, get_color, get_sound_map};

#[test]
fn test_sound_map_completeness() {
    let sound_map = get_sound_map();

    // Verify all expected metrics are present
    assert!(sound_map.contains_key("cpu_usage"));
    assert!(sound_map.contains_key("memory_usage"));
    assert!(sound_map.contains_key("pod_status"));
    assert!(sound_map.contains_key("http_latency"));
    assert!(sound_map.contains_key("errors_per_second"));
    assert!(sound_map.contains_key("replicas"));
    assert!(sound_map.contains_key("node_pressure"));
}

#[test]
fn test_sound_map_cpu_notes() {
    let sound_map = get_sound_map();
    let cpu_config = sound_map.get("cpu_usage").unwrap();

    assert_eq!(cpu_config.notes.len(), 8);
    assert_eq!(cpu_config.colors.len(), 8);
    assert_eq!(cpu_config.notes[0].frequency, 262); // C4
    assert_eq!(cpu_config.notes[7].frequency, 523); // C5
}

#[test]
fn test_calculate_index_range() {
    for i in 0..=100 {
        let index = calculate_index(i as f64, 8, 0.0, 100.0);
        assert!(index < 8, "Index {} out of bounds for value {}", index, i);
    }
}

#[test]
fn test_get_color_safety() {
    let colors = vec![
        "#111111".to_string(),
        "#222222".to_string(),
        "#333333".to_string(),
    ];

    // Test various indices including out of bounds
    for i in 0..10 {
        let color = get_color(&colors, i);
        assert!(!color.is_empty());
        assert!(color.starts_with('#'));
    }
}
