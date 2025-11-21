/// Configuration management for Sonify K8s
use serde::{Deserialize, Serialize};
use std::path::PathBuf;

use crate::error::Result;

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct Config {
    pub kubernetes: KubernetesConfig,
    pub monitoring: MonitoringConfig,
    pub audio: AudioConfig,
    pub metrics: MetricsConfig,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct KubernetesConfig {
    pub namespace: String,
    pub use_kubeconfig: bool,
    #[serde(default)]
    pub api_url: Option<String>,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct MonitoringConfig {
    pub poll_interval: u64,
    pub verbose: bool,
    pub use_color: bool,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct AudioConfig {
    pub use_midi: bool,
    pub note_duration: f64,
    pub enabled: bool,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct MetricsConfig {
    pub enabled: Vec<String>,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            kubernetes: KubernetesConfig {
                namespace: "default".to_string(),
                use_kubeconfig: true,
                api_url: None,
            },
            monitoring: MonitoringConfig {
                poll_interval: 5,
                verbose: false,
                use_color: true,
            },
            audio: AudioConfig {
                use_midi: false,
                note_duration: 0.5,
                enabled: true,
            },
            metrics: MetricsConfig {
                enabled: vec![
                    "cpu_usage".to_string(),
                    "memory_usage".to_string(),
                    "pod_status".to_string(),
                    "http_latency".to_string(),
                    "errors_per_second".to_string(),
                    "replicas".to_string(),
                    "node_pressure".to_string(),
                ],
            },
        }
    }
}

impl Config {
    /// Load configuration from a YAML file
    pub fn from_file(path: &PathBuf) -> Result<Self> {
        let content = std::fs::read_to_string(path)?;
        let config: Config = serde_yaml::from_str(&content)?;
        Ok(config)
    }

    /// Load configuration from file with fallback to default
    pub fn load(path: Option<&PathBuf>) -> Result<Self> {
        if let Some(path) = path {
            if path.exists() {
                return Self::from_file(path);
            }
        }
        Ok(Self::default())
    }

    /// Merge with environment variables
    pub fn merge_env(mut self) -> Self {
        if let Ok(ns) = std::env::var("K8S_NAMESPACE") {
            self.kubernetes.namespace = ns;
        }
        if let Ok(interval) = std::env::var("POLL_INTERVAL") {
            if let Ok(val) = interval.parse() {
                self.monitoring.poll_interval = val;
            }
        }
        if let Ok(use_config) = std::env::var("USE_KUBE_CONFIG") {
            self.kubernetes.use_kubeconfig = use_config.to_lowercase() == "true";
        }
        if let Ok(test_mode) = std::env::var("TEST_MODE") {
            if test_mode.to_lowercase() == "true" {
                self.audio.enabled = false;
            }
        }
        self
    }
}
