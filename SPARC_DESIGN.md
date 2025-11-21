# SPARC Methodology: Sonify-K8s Rust Refactoring

## S - Specification

### Core Requirements
1. **Monitor Kubernetes cluster metrics in real-time**
   - CPU usage (%)
   - Memory usage (%)
   - Pod status (Running/Pending/Failed)
   - HTTP latency (ms)
   - Errors per second
   - Replica count
   - Node pressure indicators

2. **Convert metrics to audio-visual feedback**
   - Map metric values to musical frequencies (notes)
   - Map metric values to color codes
   - Generate pure tones programmatically
   - Play audio without pre-recorded files

3. **Cluster Integration**
   - Support kubeconfig authentication
   - Support in-cluster authentication
   - Query Kubernetes API for real metrics
   - Handle namespace filtering

4. **Configuration & CLI**
   - YAML-based configuration
   - Command-line argument overrides
   - Adjustable polling intervals
   - Optional color output
   - Verbose logging modes

### Non-Functional Requirements
1. **Reliability**: No core dumps or segfaults
2. **Performance**: Minimal latency (<100ms per metric)
3. **Memory Safety**: No buffer overflows or data races
4. **Error Handling**: Graceful degradation on failures
5. **Portability**: Linux, macOS, Windows support
6. **Maintainability**: Clear module boundaries, comprehensive tests

### Problem Statement
The existing Python implementation suffers from:
- Core dumps in the simpleaudio C extension
- Memory safety issues at the Python/C boundary
- Thread safety concerns with concurrent audio playback
- GC-related unpredictability
- Lack of compile-time guarantees

### Success Criteria
- ✅ Zero core dumps or segfaults
- ✅ 100% memory safe (no unsafe blocks except FFI boundaries)
- ✅ All existing features reimplemented
- ✅ <50ms audio generation latency
- ✅ Thread-safe concurrent operations
- ✅ Comprehensive test coverage (>80%)

---

## P - Pseudocode/Planning

### High-Level Algorithm

```
MAIN:
    1. Parse CLI arguments and load configuration
    2. Initialize logging system
    3. Connect to Kubernetes cluster
    4. Initialize audio subsystem
    5. Enter monitoring loop:
        FOR each metric in SOUND_MAP:
            a. Fetch metric value from K8s API
            b. Calculate note index from metric value
            c. Lookup frequency and color
            d. Generate audio tone
            e. Play audio tone (non-blocking)
            f. Display colored console output
        SLEEP for poll_interval
    6. Handle graceful shutdown on SIGINT
```

### Module Breakdown

#### 1. K8s Client Module
```
STRUCT K8sClient:
    core_api: CoreV1Api
    apps_api: AppsV1Api

FUNCTION initialize(use_kubeconfig: bool) -> Result<K8sClient>:
    IF use_kubeconfig:
        config = load_kube_config()
    ELSE:
        config = load_incluster_config()
    RETURN K8sClient with APIs

FUNCTION get_pod_status(namespace: str) -> Result<(f64, HashMap)>:
    pods = core_api.list_namespaced_pod(namespace)
    IF pods.is_empty():
        RETURN (0.0, {status: "Unknown"})
    status = pods[0].status.phase
    index = STATUS_MAP[status]
    RETURN (index, {status: status, count: pods.len()})
```

#### 2. Audio Generation Module
```
STRUCT AudioEngine:
    sample_rate: u32
    device: OutputDevice

FUNCTION generate_tone(frequency: f64, duration: f64) -> Vec<f32>:
    samples = duration * sample_rate
    FOR i in 0..samples:
        t = i / sample_rate
        envelope = calculate_adsr_envelope(t, duration)
        sample = sin(2π * frequency * t) * envelope
        audio[i] = sample
    RETURN audio

FUNCTION play_tone(frequency: f64) -> Result<()>:
    audio = generate_tone(frequency, 0.5)
    device.play(audio)
    RETURN Ok(())
```

#### 3. Metrics Mapping Module
```
STRUCT MetricConfig:
    name: String
    unit: String
    notes: Vec<(u32, String)>  // (frequency, note_name)
    colors: Vec<String>

FUNCTION calculate_index(value: f64, notes_len: usize, min: f64, max: f64) -> usize:
    clamped = clamp(value, min, max)
    normalized = (clamped - min) / (max - min)
    index = (normalized * (notes_len - 1)) as usize
    RETURN index

FUNCTION sonify_metric(metric_name: str, value: f64) -> (u32, String):
    config = SOUND_MAP[metric_name]
    index = calculate_index(value, config.notes.len(), 0, 100)
    (frequency, note) = config.notes[index]
    color = config.colors[index]
    RETURN (frequency, color)
```

---

## A - Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CLI Entry Point                       │
│                   (clap argument parser)                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Configuration Layer                     │
│           (YAML config + ENV vars + CLI args)            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   Main Controller                        │
│              (Orchestrates monitoring loop)              │
└──────┬──────────────────────────────┬───────────────────┘
       │                              │
       ▼                              ▼
┌──────────────────┐          ┌──────────────────┐
│  K8s Client      │          │  Audio Engine    │
│  Module          │          │  Module          │
├──────────────────┤          ├──────────────────┤
│ - CoreV1Api      │          │ - ToneGenerator  │
│ - AppsV1Api      │          │ - OutputDevice   │
│ - MetricsClient  │          │ - ADSR Envelope  │
│                  │          │ - ThreadPool     │
└──────────────────┘          └──────────────────┘
       │                              │
       ▼                              ▼
┌──────────────────┐          ┌──────────────────┐
│ Metrics Mapper   │          │  Display Module  │
│                  │          │                  │
│ - SOUND_MAP      │          │ - ColorFormatter │
│ - Index Calc     │          │ - Logger         │
└──────────────────┘          └──────────────────┘
```

### Directory Structure

```
sonify-k8s-rust/
├── Cargo.toml
├── README.md
├── config.yaml
├── src/
│   ├── main.rs              # Entry point, CLI
│   ├── lib.rs               # Library exports
│   ├── config.rs            # Configuration management
│   ├── error.rs             # Error types and handling
│   ├── k8s/
│   │   ├── mod.rs           # K8s module exports
│   │   ├── client.rs        # K8s API client
│   │   └── metrics.rs       # Metric fetching logic
│   ├── audio/
│   │   ├── mod.rs           # Audio module exports
│   │   ├── engine.rs        # Audio engine
│   │   ├── generator.rs     # Tone generation
│   │   └── envelope.rs      # ADSR envelope
│   ├── sonify/
│   │   ├── mod.rs           # Sonification module
│   │   ├── mapper.rs        # Metrics to sound mapping
│   │   └── sound_map.rs     # SOUND_MAP definitions
│   └── display/
│       ├── mod.rs           # Display module
│       └── color.rs         # ANSI color formatting
└── tests/
    ├── integration_test.rs
    └── unit_tests.rs
```

### Data Flow

```
1. CLI Input → Config Loader → Merged Config
2. Config → K8s Client Initializer → Authenticated Client
3. Monitoring Loop Start
4. Metric Name → K8s Client → Raw Metric Value
5. Raw Value → Metrics Mapper → (Frequency, Color, Note)
6. Frequency → Audio Generator → Audio Buffer
7. Audio Buffer → Audio Device → Sound Output
8. (Color, Value, Note) → Display → Terminal Output
9. Sleep Poll Interval → Loop Continue
```

### Key Design Decisions

1. **Use rodio for audio**: Safe, pure-Rust audio library (no C deps)
2. **Use kube-rs**: Official Rust Kubernetes client
3. **Use tokio**: Async runtime for K8s API calls
4. **Use clap v4**: Modern CLI argument parsing
5. **Use serde + serde_yaml**: Config deserialization
6. **Use tracing**: Structured logging
7. **Use thiserror**: Ergonomic error handling
8. **Use crossterm**: Cross-platform terminal colors

### Thread Safety Strategy

- Main thread: Monitoring loop
- Audio thread pool: Non-blocking audio playback
- Mutex-protected shared state: Minimal (config only)
- Message passing: For audio commands

---

## R - Refinement

### Optimizations

1. **Audio Generation**
   - Pre-calculate ADSR envelope coefficients
   - Use SIMD for sine wave generation (optional)
   - Pool audio buffers to reduce allocations
   - Use ring buffer for smooth playback

2. **K8s API Calls**
   - Batch multiple metric queries
   - Cache pod lists within polling interval
   - Use watch API for real-time updates (future)
   - Connection pooling

3. **Memory Management**
   - Use `Box<[f32]>` for fixed audio buffers
   - Avoid string allocations in hot path
   - Lazy initialization of color formatters
   - Pre-allocate Vec capacity

### Error Handling Strategy

```rust
#[derive(thiserror::Error, Debug)]
pub enum SonifyError {
    #[error("Kubernetes API error: {0}")]
    KubeError(#[from] kube::Error),

    #[error("Audio playback error: {0}")]
    AudioError(String),

    #[error("Configuration error: {0}")]
    ConfigError(#[from] serde_yaml::Error),

    #[error("Invalid metric: {0}")]
    InvalidMetric(String),
}

type Result<T> = std::result::Result<T, SonifyError>;
```

### Testing Strategy

1. **Unit Tests**
   - `calculate_index()` with edge cases
   - ADSR envelope generation
   - Color formatting
   - Config parsing

2. **Integration Tests**
   - K8s client with mock API server
   - Audio generation (write to buffer)
   - End-to-end metric sonification

3. **Property-Based Tests**
   - Index calculation always in bounds
   - Audio samples normalized [-1.0, 1.0]

### Security Considerations

1. **Input Validation**
   - Validate YAML config structure
   - Sanitize kubeconfig paths
   - Bound numeric inputs

2. **Dependency Audit**
   - Use `cargo audit` in CI
   - Pin critical dependencies
   - Minimal unsafe code

3. **Resource Limits**
   - Max audio buffer size
   - K8s API timeout
   - Max log file size

---

## C - Coding (Implementation Plan)

### Phase 1: Project Setup
- [x] Initialize Cargo project
- [ ] Add dependencies to Cargo.toml
- [ ] Create module structure
- [ ] Setup CI/CD skeleton

### Phase 2: Core Infrastructure
- [ ] Implement error types (error.rs)
- [ ] Implement config loading (config.rs)
- [ ] Implement logging setup (main.rs)
- [ ] Implement CLI parsing (main.rs)

### Phase 3: Kubernetes Integration
- [ ] Implement K8s client initialization (k8s/client.rs)
- [ ] Implement pod status fetching (k8s/metrics.rs)
- [ ] Implement deployment replicas fetching
- [ ] Implement node pressure fetching
- [ ] Implement resource usage estimation

### Phase 4: Audio System
- [ ] Implement ADSR envelope generator (audio/envelope.rs)
- [ ] Implement sine wave tone generator (audio/generator.rs)
- [ ] Implement audio engine with rodio (audio/engine.rs)
- [ ] Add thread pool for concurrent playback

### Phase 5: Sonification Logic
- [ ] Define SOUND_MAP constants (sonify/sound_map.rs)
- [ ] Implement metric value to index calculation (sonify/mapper.rs)
- [ ] Implement metric to sound/color mapping
- [ ] Integrate with K8s and audio modules

### Phase 6: Display & Polish
- [ ] Implement ANSI color formatting (display/color.rs)
- [ ] Implement console output formatting
- [ ] Add progress indicators
- [ ] Polish logging output

### Phase 7: Testing & Documentation
- [ ] Write unit tests for all modules
- [ ] Write integration tests
- [ ] Update README.md for Rust version
- [ ] Add inline documentation
- [ ] Create usage examples

### Rust Dependencies (Cargo.toml)

```toml
[dependencies]
# Kubernetes client
kube = { version = "0.87", features = ["runtime", "derive"] }
k8s-openapi = { version = "0.20", features = ["v1_28"] }

# Async runtime
tokio = { version = "1", features = ["full"] }

# Audio
rodio = "0.17"

# CLI
clap = { version = "4", features = ["derive"] }

# Config
serde = { version = "1", features = ["derive"] }
serde_yaml = "0.9"

# Logging
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter"] }

# Error handling
thiserror = "1"
anyhow = "1"

# Terminal colors
crossterm = "0.27"

# Math
libm = "0.2"

[dev-dependencies]
mockall = "0.12"
```

---

## Summary

This SPARC-based design addresses all core dump issues by:
1. Eliminating Python/C FFI boundary (pure Rust)
2. Compile-time memory safety guarantees
3. Thread-safe audio playback with message passing
4. Robust error handling with Result types
5. Zero-cost abstractions for performance

The Rust implementation will be:
- **Safer**: No segfaults, buffer overflows, or data races
- **Faster**: Lower latency, efficient resource usage
- **More Reliable**: Predictable behavior, graceful error recovery
- **Maintainable**: Strong typing, clear module boundaries
