# 🎵 Sonify K8s

> **Transform your Kubernetes cluster metrics into sound!**
> Sonify K8s monitors your Kubernetes cluster metrics and converts them into musical tones and colors, making cluster health monitoring more intuitive and engaging.

---

<details>
<summary>✨ Features</summary>

- 🔔 **Real-time Metric Sonification**
    Hear your cluster's CPU, memory, pod status, and more as musical tones.

- 🎨 **Visual Color Mapping**
    Each metric is mapped to both sound frequencies and colors for multi-sensory feedback.

- 🎚️ **Customizable Configuration**
    Configure polling intervals, namespaces, and monitoring settings via config.yaml.

- 🛠️ **Easy Integration**
    Works with any K8s cluster using kubeconfig or in-cluster configuration.

- 📦 **Lightweight & Fast**
    Minimal dependencies, quick to set up, no external sound files needed.

- 🎵 **Programmatic Sound Generation**
    Generates tones dynamically using numpy and simpleaudio—no WAV files required.

</details>

---

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/michaelcolletti/sonify-k8s.git
cd sonify-k8s
pip install -r requirements.txt
```

### Basic Usage

```bash
# Monitor the default namespace
python src/main.py

# Monitor a specific namespace with colors
python src/main.py --color --namespace kube-system

# Adjust polling interval
python src/main.py --interval 10 --verbose
```

## Using the Makefile

```bash
git clone https://github.com/michaelcolletti/sonify-k8s.git
cd sonify-k8s
make install
make test
make run
```


---

## 🛠️ How It Works

1. **Connects to your Kubernetes cluster** using kubeconfig or in-cluster configuration
2. **Polls cluster metrics** at regular intervals (configurable)
3. **Maps metrics to musical notes** based on their values
4. **Generates and plays tones** programmatically using numpy and simpleaudio
5. **Displays colored output** (optional) for visual feedback

### Monitored Metrics

- **CPU Usage**: CPU utilization across pods (%)
- **Memory Usage**: Memory utilization across pods (%)
- **Pod Status**: Current pod states (Running, Pending, Failed, etc.)
- **HTTP Latency**: Estimated request latency (ms)
- **Errors/Second**: Estimated error rate
- **Replica Count**: Average deployment replica count
- **Node Pressure**: Node resource pressure indicators

Each metric value is mapped to a specific musical note frequency and color, creating an audible and visual representation of cluster health.

---

## 🎛️ Configuration

### Command Line Options

```bash
python src/main.py [OPTIONS]

Options:
  -c, --color              Show ANSI colors in output
  -m, --midi               Use MIDI for sound output if available
  -i, --interval INTEGER   Polling interval in seconds (default: 5)
  -n, --namespace TEXT     Kubernetes namespace to monitor (default: "default")
  -v, --verbose            Enable verbose logging
  --help                   Show this message and exit
```

### Configuration File

Edit `config.yaml` to customize monitoring settings:

```yaml
kubernetes:
  namespace: "default"
  use_kubeconfig: true

monitoring:
  poll_interval: 5
  verbose: false
  use_color: true

audio:
  use_midi: false
  note_duration: 0.5
  enabled: true
```

### Environment Variables

- `K8S_NAMESPACE`: Kubernetes namespace to monitor (default: "default")
- `USE_KUBE_CONFIG`: Use kubeconfig from ~/.kube/config (default: "true")
- `POLL_INTERVAL`: Polling interval in seconds (default: 5)
- `LOG_LEVEL`: Logging level (default: "INFO")
- `TEST_MODE`: Run without audio playback (default: "false")

---

## 📦 Requirements

- Python 3.7+
- `kubernetes` Python client (>=28.0.0)
- `simpleaudio` (>=1.0.4) for audio playback
- `numpy` (>=1.20.0) for sound generation
- `click` (>=8.0.0) for CLI interface
- `PyYAML` (>=6.0.0) for configuration files
- Access to a Kubernetes cluster (via kubeconfig or in-cluster config)

### System Requirements

- Linux, macOS, or Windows
- Audio output device
- Valid Kubernetes cluster credentials

### Setting Up Kubernetes Access

**Using kubeconfig (recommended for local development):**
```bash
export USE_KUBE_CONFIG=true
# Make sure ~/.kube/config exists and is configured
kubectl cluster-info
```

**In-cluster configuration (for running inside K8s):**
```bash
export USE_KUBE_CONFIG=false
# Application will use in-cluster service account
```

---

## 🔧 Troubleshooting

### Connection Issues

If you see "Failed to connect to Kubernetes cluster":
1. Verify `kubectl` is configured: `kubectl cluster-info`
2. Check your kubeconfig: `cat ~/.kube/config`
3. Set environment variable: `export USE_KUBE_CONFIG=true`
4. Ensure you have appropriate RBAC permissions

### Audio Issues

If audio doesn't play:
1. Check system audio is working
2. Install system audio libraries:
   - **Linux**: `sudo apt-get install -y python3-dev libasound2-dev`
   - **macOS**: Audio should work out of the box
   - **Windows**: Requires Visual C++ redistributable
3. Run in test mode to verify logic: `export TEST_MODE=true`

### No Metrics Available

If metrics show 0 or "Unknown":
1. Check namespace exists: `kubectl get namespaces`
2. Verify pods are running: `kubectl get pods -n <namespace>`
3. Ensure you have read permissions in the namespace

---

## 🤝 Contributing

Pull requests welcome! Please open an issue first to discuss proposed changes.

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.

---

## 🧑‍💻 Author

Made with ❤️ by [Michael Colletti](https://github.com/michaelcolletti)

---

## 🎯 Future Enhancements

- [ ] Metrics-server integration for real CPU/memory data
- [ ] Prometheus metrics support
- [ ] Custom metric plugins
- [ ] Web dashboard for visualization
- [ ] Recording and playback functionality
- [ ] Multi-cluster support
- [ ] Alert thresholds with distinct sounds
