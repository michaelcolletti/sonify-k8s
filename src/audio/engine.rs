/// Audio engine - supports optional rodio backend
use crate::error::{Result, SonifyError};

#[cfg(feature = "audio")]
use crate::audio::generator::generate_tone;
#[cfg(feature = "audio")]
use rodio::{OutputStream, Sink, Source};
#[cfg(feature = "audio")]
use std::io::Cursor;
#[cfg(feature = "audio")]
use std::sync::{Arc, Mutex};

pub struct AudioEngine {
    #[cfg(feature = "audio")]
    _stream: Option<OutputStream>,
    #[cfg(feature = "audio")]
    sink: Option<Arc<Mutex<Sink>>>,
    sample_rate: u32,
    enabled: bool,
}

impl AudioEngine {
    /// Create a new audio engine
    pub fn new(enabled: bool) -> Result<Self> {
        #[cfg(not(feature = "audio"))]
        {
            tracing::warn!("Audio feature not compiled - running in silent mode");
            tracing::warn!("To enable audio, compile with: cargo build --features audio");
            return Ok(Self {
                sample_rate: 44100,
                enabled: false,
            });
        }

        #[cfg(feature = "audio")]
        {
            if !enabled {
                return Ok(Self {
                    _stream: None,
                    sink: None,
                    sample_rate: 44100,
                    enabled: false,
                });
            }

            // Try to initialize audio output
            match OutputStream::try_default() {
                Ok((_stream, stream_handle)) => {
                    let sink = Sink::try_new(&stream_handle)
                        .map_err(|e| SonifyError::AudioError(e.to_string()))?;

                    Ok(Self {
                        _stream: Some(_stream),
                        sink: Some(Arc::new(Mutex::new(sink))),
                        sample_rate: 44100,
                        enabled: true,
                    })
                }
                Err(e) => {
                    tracing::warn!("Failed to initialize audio output: {}", e);
                    // Fallback to disabled mode
                    Ok(Self {
                        _stream: None,
                        sink: None,
                        sample_rate: 44100,
                        enabled: false,
                    })
                }
            }
        }
    }

    /// Play a tone at the specified frequency
    pub fn play_tone(&self, frequency: f64, duration: f64) -> Result<()> {
        if !self.enabled {
            tracing::debug!("Audio disabled, skipping tone at {} Hz", frequency);
            return Ok(());
        }

        if frequency <= 0.0 {
            return Err(SonifyError::InvalidFrequency(frequency));
        }

        #[cfg(feature = "audio")]
        {
            // Generate audio samples
            let samples = generate_tone(frequency, duration, self.sample_rate);

            // Convert to bytes for rodio
            let mut bytes = Vec::new();
            for sample in samples {
                let sample_i16 = (sample * i16::MAX as f32) as i16;
                bytes.extend_from_slice(&sample_i16.to_le_bytes());
            }

            // Create a source from the buffer
            let cursor = Cursor::new(bytes);
            let source = rodio::Decoder::new(cursor)
                .map_err(|e| SonifyError::AudioError(format!("Failed to decode audio: {}", e)))?;

            // Play the audio
            if let Some(ref sink) = self.sink {
                let sink = sink.lock()
                    .map_err(|e| SonifyError::AudioError(format!("Failed to lock sink: {}", e)))?;
                sink.append(source);
            }
        }

        Ok(())
    }

    /// Wait for all audio to finish playing
    pub fn wait(&self) {
        #[cfg(feature = "audio")]
        {
            if let Some(ref sink) = self.sink {
                if let Ok(sink) = sink.lock() {
                    sink.sleep_until_end();
                }
            }
        }
    }

    /// Check if audio is enabled
    pub fn is_enabled(&self) -> bool {
        self.enabled
    }
}

#[cfg(feature = "audio")]
// Simple in-memory PCM source for rodio
struct PcmSource {
    data: Vec<i16>,
    position: usize,
    sample_rate: u32,
    channels: u16,
}

#[cfg(feature = "audio")]
impl PcmSource {
    fn new(data: Vec<i16>, sample_rate: u32) -> Self {
        Self {
            data,
            position: 0,
            sample_rate,
            channels: 1,
        }
    }
}

#[cfg(feature = "audio")]
impl Iterator for PcmSource {
    type Item = i16;

    fn next(&mut self) -> Option<Self::Item> {
        if self.position < self.data.len() {
            let sample = self.data[self.position];
            self.position += 1;
            Some(sample)
        } else {
            None
        }
    }
}

#[cfg(feature = "audio")]
impl Source for PcmSource {
    fn current_frame_len(&self) -> Option<usize> {
        Some(self.data.len() - self.position)
    }

    fn channels(&self) -> u16 {
        self.channels
    }

    fn sample_rate(&self) -> u32 {
        self.sample_rate
    }

    fn total_duration(&self) -> Option<std::time::Duration> {
        let samples = self.data.len() as u64;
        let duration_secs = samples / self.sample_rate as u64;
        Some(std::time::Duration::from_secs(duration_secs))
    }
}
