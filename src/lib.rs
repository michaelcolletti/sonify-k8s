/// Sonify K8s - Transform Kubernetes metrics into sound
///
/// This library provides the core functionality for monitoring Kubernetes
/// clusters and converting metrics into audio-visual feedback.

pub mod audio;
pub mod config;
pub mod display;
pub mod error;
pub mod k8s;
pub mod sonify;

pub use audio::AudioEngine;
pub use config::Config;
pub use error::{Result, SonifyError};
pub use k8s::K8sClient;
pub use sonify::{get_sound_map, map_metric};
