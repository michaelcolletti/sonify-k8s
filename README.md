# 🎵 Sonify K8s

> **Transform your Kubernetes cluster events into sound!**  
> Sonify K8s listens to your Kubernetes events and plays unique sounds for each event type, making cluster monitoring more intuitive and fun.

---

<details>
<summary>✨ Features</summary>

- 🔔 **Real-time Event Sonification**  
    Instantly hear when pods, deployments, or services change state.

- 🎚️ **Customizable Sound Mapping**  
    Assign your own sounds to different Kubernetes events.

- 🛠️ **Easy Integration**  
    Works with any K8s cluster—just point and play.

- 📦 **Lightweight & Fast**  
    Minimal dependencies, quick to set up.

</details>

---

## 🚀 Quick Start

```bash
git clone https://github.com/michaelcolletti/sonify-k8s.git
cd sonify-k8s
pip install -r requirements.txt
python sonify_k8s.py --kubeconfig ~/.kube/config
```

## Using a Makefile


```bash
git clone https://github.com/michaelcolletti/sonify-k8s.git
cd sonify-k8s
make install;make test;
python sonify_k8s.py --kubeconfig ~/.kube/config
```


---

## 🛠️ How It Works

1. **Connects to your Kubernetes cluster** using your kubeconfig.
2. **Watches for events** (e.g., Pod Created, Pod Deleted, Deployment Updated).
3. **Plays a sound** mapped to each event type.

```python
from kubernetes import client, config, watch
import simpleaudio as sa

config.load_kube_config()
v1 = client.CoreV1Api()
w = watch.Watch()

for event in w.stream(v1.list_pod_for_all_namespaces):
        if event['type'] == 'ADDED':
                sa.WaveObject.from_wave_file('sounds/pod_added.wav').play()
        elif event['type'] == 'DELETED':
                sa.WaveObject.from_wave_file('sounds/pod_deleted.wav').play()
```

---

## 🎛️ Configuration

Edit `config.yaml` to map events to your preferred sound files:

```yaml
events:
    PodAdded: sounds/pod_added.wav
    PodDeleted: sounds/pod_deleted.wav
    DeploymentScaled: sounds/deployment_scaled.wav
```

---

## 📦 Requirements

- Python 3.7+
- `kubernetes` Python client
- `simpleaudio` for sound playback

---

## 🤝 Contributing

Pull requests welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.

---

## 🧑‍💻 Author

Made with ❤️ by [Your Name](https://github.com/yourname)
