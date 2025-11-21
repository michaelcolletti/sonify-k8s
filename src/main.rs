/// Sonify K8s - Main entry point
use clap::Parser;
use sonify_k8s::{
    audio::AudioEngine, config::Config, display::colorize, error::Result, k8s::K8sClient,
    k8s::metrics::get_k8s_data, sonify::get_sound_map, sonify::map_metric,
};
use std::path::PathBuf;
use std::time::Duration;
use tokio::time;
use tracing::{error, info, warn};

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    /// Show ANSI colors in output
    #[arg(short, long)]
    color: bool,

    /// Use MIDI for sound output if available
    #[arg(short, long)]
    midi: bool,

    /// Polling interval in seconds
    #[arg(short, long)]
    interval: Option<u64>,

    /// Kubernetes namespace to monitor
    #[arg(short, long, default_value = "default")]
    namespace: String,

    /// Enable verbose logging
    #[arg(short, long)]
    verbose: bool,

    /// Configuration file path
    #[arg(short = 'f', long)]
    config: Option<PathBuf>,
}

#[tokio::main]
async fn main() -> Result<()> {
    // Parse command line arguments
    let args = Args::parse();

    // Initialize logging
    let log_level = if args.verbose { "debug" } else { "info" };
    tracing_subscriber::fmt()
        .with_env_filter(log_level)
        .with_target(false)
        .init();

    info!("🎵 Starting Sonify K8s v{}", env!("CARGO_PKG_VERSION"));

    // Load configuration
    let mut config = Config::load(args.config.as_ref())?.merge_env();

    // Override with CLI arguments
    if args.color {
        config.monitoring.use_color = true;
    }
    if let Some(interval) = args.interval {
        config.monitoring.poll_interval = interval;
    }
    config.kubernetes.namespace = args.namespace.clone();

    info!(
        "Monitoring namespace: {} with {} second polling interval",
        config.kubernetes.namespace, config.monitoring.poll_interval
    );

    // Initialize Kubernetes client
    let mut k8s_client = K8sClient::new(config.kubernetes.namespace.clone());
    k8s_client
        .initialize(config.kubernetes.use_kubeconfig)
        .await?;

    // Initialize audio engine
    let audio_engine = AudioEngine::new(config.audio.enabled)?;
    if !audio_engine.is_enabled() {
        warn!("Audio is disabled or unavailable - running in silent mode");
    }

    // Get sound map
    let sound_map = get_sound_map();

    // Main monitoring loop
    info!("Starting metric sonification...");
    let mut interval_timer = time::interval(Duration::from_secs(config.monitoring.poll_interval));

    loop {
        interval_timer.tick().await;

        for metric_name in &config.metrics.enabled {
            // Fetch metric data
            let data = match get_k8s_data(metric_name, &k8s_client).await {
                Ok(Some(data)) => data,
                Ok(None) => {
                    warn!("No data available for metric: {}", metric_name);
                    continue;
                }
                Err(e) => {
                    error!("Failed to get data for {}: {}", metric_name, e);
                    continue;
                }
            };

            let (metric_value, extra_data) = data;

            // Map metric to sound and color
            let (frequency, note_name, color) =
                match map_metric(metric_name, metric_value, &sound_map) {
                    Ok(result) => result,
                    Err(e) => {
                        error!("Failed to map metric {}: {}", metric_name, e);
                        continue;
                    }
                };

            // Play the tone
            if let Err(e) = audio_engine.play_tone(frequency as f64, config.audio.note_duration) {
                error!("Failed to play tone: {}", e);
            }

            // Get metric config for display
            if let Some(metric_config) = sound_map.get(metric_name) {
                let log_message = format!(
                    "{}: {:.2} {} | Note: {} ({} Hz) | Color: {} | Extra: {:?}",
                    metric_config.metric_name,
                    metric_value,
                    metric_config.unit,
                    note_name,
                    frequency,
                    color,
                    extra_data
                );

                // Print colored output
                if config.monitoring.use_color {
                    println!("{}", colorize(&log_message, &color, true));
                } else {
                    println!("{}", log_message);
                }

                info!("{}", log_message);
            }
        }
    }
}
