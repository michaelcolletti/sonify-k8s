/// ADSR envelope generator for smoother audio
///
/// Attack-Decay-Sustain-Release envelope shaping

#[derive(Debug, Clone)]
pub struct ADSREnvelope {
    pub attack: f64,
    pub decay: f64,
    pub sustain_level: f64,
    pub release: f64,
}

impl Default for ADSREnvelope {
    fn default() -> Self {
        Self {
            attack: 0.05,
            decay: 0.05,
            sustain_level: 0.8,
            release: 0.1,
        }
    }
}

impl ADSREnvelope {
    /// Calculate the envelope value at a specific time
    pub fn calculate(&self, t: f64, duration: f64) -> f64 {
        let attack_time = self.attack;
        let decay_time = self.attack + self.decay;
        let release_time = duration - self.release;

        if t < attack_time {
            // Attack phase: linear ramp from 0 to 1
            t / attack_time
        } else if t < decay_time {
            // Decay phase: linear ramp from 1 to sustain_level
            1.0 - (1.0 - self.sustain_level) * (t - attack_time) / self.decay
        } else if t < release_time {
            // Sustain phase: constant at sustain_level
            self.sustain_level
        } else {
            // Release phase: linear ramp from sustain_level to 0
            self.sustain_level * (1.0 - (t - release_time) / self.release)
        }
    }

    /// Generate envelope samples for a given duration and sample rate
    pub fn generate_samples(&self, duration: f64, sample_rate: u32) -> Vec<f32> {
        let total_samples = (duration * sample_rate as f64) as usize;
        let mut envelope = Vec::with_capacity(total_samples);

        for i in 0..total_samples {
            let t = i as f64 / sample_rate as f64;
            let value = self.calculate(t, duration);
            envelope.push(value as f32);
        }

        envelope
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_envelope_attack() {
        let env = ADSREnvelope::default();
        assert_eq!(env.calculate(0.0, 1.0), 0.0);
        assert!(env.calculate(0.025, 1.0) > 0.0 && env.calculate(0.025, 1.0) < 1.0);
    }

    #[test]
    fn test_envelope_sustain() {
        let env = ADSREnvelope::default();
        let mid_time = 0.5;
        let value = env.calculate(mid_time, 1.0);
        assert!((value - env.sustain_level).abs() < 0.01);
    }
}
