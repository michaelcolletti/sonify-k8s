/// Sound mapping definitions for metrics
use std::collections::HashMap;

#[derive(Debug, Clone)]
pub struct Note {
    pub frequency: u32,
    pub name: String,
}

#[derive(Debug, Clone)]
pub struct MetricConfig {
    pub metric_name: String,
    pub unit: String,
    pub notes: Vec<Note>,
    pub colors: Vec<String>,
    pub status_map: Option<HashMap<String, usize>>,
}

impl Note {
    pub fn new(frequency: u32, name: &str) -> Self {
        Self {
            frequency,
            name: name.to_string(),
        }
    }
}

pub fn get_sound_map() -> HashMap<String, MetricConfig> {
    let mut map = HashMap::new();

    // CPU Usage
    map.insert(
        "cpu_usage".to_string(),
        MetricConfig {
            metric_name: "CPU Usage".to_string(),
            unit: "%".to_string(),
            notes: vec![
                Note::new(262, "C4"),
                Note::new(294, "D4"),
                Note::new(330, "E4"),
                Note::new(349, "F4"),
                Note::new(392, "G4"),
                Note::new(440, "A4"),
                Note::new(494, "B4"),
                Note::new(523, "C5"),
            ],
            colors: vec![
                "#88E0EF".to_string(),
                "#39C0ED".to_string(),
                "#218380".to_string(),
                "#126E82".to_string(),
                "#145DA0".to_string(),
                "#0F4C75".to_string(),
                "#3282B8".to_string(),
                "#118AB2".to_string(),
            ],
            status_map: None,
        },
    );

    // Memory Usage
    map.insert(
        "memory_usage".to_string(),
        MetricConfig {
            metric_name: "Memory Usage".to_string(),
            unit: "%".to_string(),
            notes: vec![
                Note::new(277, "C#4"),
                Note::new(311, "D#4"),
                Note::new(349, "F4"),
                Note::new(370, "F#4"),
                Note::new(415, "G#4"),
                Note::new(466, "A#4"),
                Note::new(523, "C5"),
                Note::new(554, "C#5"),
            ],
            colors: vec![
                "#D4F5FF".to_string(),
                "#A7E9FF".to_string(),
                "#56CCF2".to_string(),
                "#29ADB2".to_string(),
                "#247BA0".to_string(),
                "#1E3A8A".to_string(),
                "#2A9D8F".to_string(),
                "#81B29A".to_string(),
            ],
            status_map: None,
        },
    );

    // Pod Status
    let mut pod_status_map = HashMap::new();
    pod_status_map.insert("Running".to_string(), 3);
    pod_status_map.insert("Pending".to_string(), 1);
    pod_status_map.insert("Succeeded".to_string(), 3);
    pod_status_map.insert("Failed".to_string(), 0);
    pod_status_map.insert("Unknown".to_string(), 0);

    map.insert(
        "pod_status".to_string(),
        MetricConfig {
            metric_name: "Pod Status".to_string(),
            unit: "".to_string(),
            notes: vec![
                Note::new(220, "A3"),
                Note::new(262, "C4"),
                Note::new(330, "E4"),
                Note::new(392, "G4"),
            ],
            colors: vec![
                "#86EF7D".to_string(),
                "#22C55E".to_string(),
                "#16A34A".to_string(),
                "#065F46".to_string(),
            ],
            status_map: Some(pod_status_map),
        },
    );

    // HTTP Latency
    map.insert(
        "http_latency".to_string(),
        MetricConfig {
            metric_name: "HTTP Latency".to_string(),
            unit: "ms".to_string(),
            notes: vec![
                Note::new(294, "D4"),
                Note::new(330, "E4"),
                Note::new(370, "F#4"),
                Note::new(415, "G#4"),
                Note::new(466, "A#4"),
                Note::new(523, "C5"),
                Note::new(587, "D5"),
                Note::new(659, "E5"),
            ],
            colors: vec![
                "#FFE5D9".to_string(),
                "#FFCAD4".to_string(),
                "#F4ACB7".to_string(),
                "#F46036".to_string(),
                "#E5383B".to_string(),
                "#B22222".to_string(),
                "#8B0000".to_string(),
                "#DC143C".to_string(),
            ],
            status_map: None,
        },
    );

    // Errors per Second
    map.insert(
        "errors_per_second".to_string(),
        MetricConfig {
            metric_name: "Errors/Second".to_string(),
            unit: "err/s".to_string(),
            notes: vec![
                Note::new(131, "C3"),
                Note::new(147, "D3"),
                Note::new(165, "E3"),
                Note::new(175, "F3"),
                Note::new(196, "G3"),
                Note::new(220, "A3"),
                Note::new(247, "B3"),
                Note::new(262, "C4"),
            ],
            colors: vec![
                "#FFF2CC".to_string(),
                "#FFD65E".to_string(),
                "#FFA41B".to_string(),
                "#F94144".to_string(),
                "#F3722C".to_string(),
                "#F8961E".to_string(),
                "#F9C74F".to_string(),
                "#90BE6D".to_string(),
            ],
            status_map: None,
        },
    );

    // Replicas
    map.insert(
        "replicas".to_string(),
        MetricConfig {
            metric_name: "Replica Count".to_string(),
            unit: "Count".to_string(),
            notes: vec![
                Note::new(262, "C4"),
                Note::new(277, "C#4"),
                Note::new(294, "D4"),
                Note::new(311, "D#4"),
                Note::new(330, "E4"),
                Note::new(349, "F4"),
                Note::new(370, "F#4"),
                Note::new(392, "G4"),
            ],
            colors: vec![
                "#E0F7FA".to_string(),
                "#B2EBF2".to_string(),
                "#80DEEA".to_string(),
                "#4DD0E1".to_string(),
                "#26C6DA".to_string(),
                "#00BCD4".to_string(),
                "#00ACC1".to_string(),
                "#0097A7".to_string(),
            ],
            status_map: None,
        },
    );

    // Node Pressure
    let mut node_pressure_map = HashMap::new();
    node_pressure_map.insert("False".to_string(), 0);
    node_pressure_map.insert("True".to_string(), 3);

    map.insert(
        "node_pressure".to_string(),
        MetricConfig {
            metric_name: "Node Pressure".to_string(),
            unit: "".to_string(),
            notes: vec![
                Note::new(262, "C4"),
                Note::new(294, "D4"),
                Note::new(330, "E4"),
                Note::new(349, "F4"),
            ],
            colors: vec![
                "#FFFFFF".to_string(),
                "#F0F4C3".to_string(),
                "#D4E157".to_string(),
                "#A4A71D".to_string(),
            ],
            status_map: Some(node_pressure_map),
        },
    );

    map
}
