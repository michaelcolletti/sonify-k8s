/// Error types for the Sonify K8s application
use thiserror::Error;

#[derive(Error, Debug)]
pub enum SonifyError {
    #[error("Kubernetes API error: {0}")]
    KubeError(#[from] kube::Error),

    #[error("Kube config error: {0}")]
    KubeConfigError(String),

    #[error("Audio playback error: {0}")]
    AudioError(String),

    #[error("Configuration error: {0}")]
    ConfigError(#[from] serde_yaml::Error),

    #[error("Invalid metric: {0}")]
    InvalidMetric(String),

    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),

    #[error("Invalid frequency: {0}")]
    InvalidFrequency(f64),

    #[error("K8s client not initialized")]
    ClientNotInitialized,

    #[error("No audio output device available")]
    NoAudioDevice,
}

pub type Result<T> = std::result::Result<T, SonifyError>;
