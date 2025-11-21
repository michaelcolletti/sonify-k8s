/// Tone generation using pure Rust mathematics
use crate::audio::envelope::ADSREnvelope;
use std::f64::consts::PI;

/// Generate a sine wave tone with ADSR envelope
pub fn generate_tone(frequency: f64, duration: f64, sample_rate: u32) -> Vec<f32> {
    let envelope = ADSREnvelope::default();
    let total_samples = (duration * sample_rate as f64) as usize;
    let mut samples = Vec::with_capacity(total_samples);

    for i in 0..total_samples {
        let t = i as f64 / sample_rate as f64;

        // Generate sine wave
        let sine = (2.0 * PI * frequency * t).sin();

        // Apply envelope
        let env_value = envelope.calculate(t, duration);
        let sample = (sine * env_value) as f32;

        samples.push(sample);
    }

    samples
}

/// Normalize audio samples to prevent clipping
pub fn normalize_samples(samples: &mut [f32]) {
    let max_amplitude = samples.iter()
        .map(|&s| s.abs())
        .fold(0.0f32, f32::max);

    if max_amplitude > 0.0 {
        let scale = 0.95 / max_amplitude; // Leave headroom
        for sample in samples.iter_mut() {
            *sample *= scale;
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_generate_tone_length() {
        let samples = generate_tone(440.0, 1.0, 44100);
        assert_eq!(samples.len(), 44100);
    }

    #[test]
    fn test_generate_tone_bounds() {
        let samples = generate_tone(440.0, 0.1, 44100);
        for sample in samples {
            assert!(sample >= -1.0 && sample <= 1.0);
        }
    }

    #[test]
    fn test_normalize() {
        let mut samples = vec![0.5, 1.5, -2.0, 0.8];
        normalize_samples(&mut samples);
        for sample in samples {
            assert!(sample.abs() <= 1.0);
        }
    }
}
