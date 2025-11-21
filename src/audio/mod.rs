/// Audio module for tone generation and playback
pub mod engine;
pub mod envelope;
pub mod generator;

pub use engine::AudioEngine;
pub use envelope::ADSREnvelope;
pub use generator::{generate_tone, normalize_samples};
