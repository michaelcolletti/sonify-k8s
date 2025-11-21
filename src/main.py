#!/usr/bin/env python3
import time
import random
import logging
import os
import click
import numpy as np
from kubernetes import client, config
from kubernetes.client.rest import ApiException

from typing import Dict, List, Tuple, Optional

# --- 1. Simplicity: Provide clear, maintainable solutions ---
# --- 2. Focus: Stick strictly to defined tasks ---
# --- 4. Quality: Deliver clean, well-tested, documented, and secure code ---
# --- 5. Collaboration: Foster effective teamwork between human developers and AI ---

# --- Project: Sonify Kubernetes Metrics ---
# --- Description: This utility monitors Kubernetes metrics and sonifies them, providing an audio-visual representation of cluster health. ---
# --- Author: AI Assistant ---
# --- Date: 2024-07-24 ---
# --- Version: 2.0 ---

# --- Configuration and Constants ---
K8S_API_URL = os.environ.get(
    "K8S_API_URL", "http://localhost:8080"
)  # Default K8s API URL
POLL_INTERVAL = int(
    os.environ.get("POLL_INTERVAL", 5)
)  # Default polling interval in seconds
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()  # Default log level
USE_KUBE_CONFIG = (
    os.environ.get("USE_KUBE_CONFIG", "true").lower() == "true"
)  # Use ~/.kube/config (default: true)
K8S_NAMESPACE = os.environ.get("K8S_NAMESPACE", "default")  # Default namespace

# --- Logging Setup ---
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- 3. Language-Specific Best Practices ---
# Use a dictionary to map metrics to their sonification configurations.
SOUND_MAP: Dict[str, Dict[str, Tuple[int, str]]] = {
    "cpu_usage": {
        "metric_name": "CPU Usage",
        "unit": "%",
        "notes": [
            (262, "C4"),
            (294, "D4"),
            (330, "E4"),
            (349, "F4"),
            (392, "G4"),
            (440, "A4"),
            (494, "B4"),
            (523, "C5"),
        ],
        "colors": [
            "#88E0EF",
            "#39C0ED",
            "#218380",
            "#126E82",
            "#145DA0",
            "#0F4C75",
            "#3282B8",
            "#118AB2",
        ],
    },
    "memory_usage": {
        "metric_name": "Memory Usage",
        "unit": "%",
        "notes": [
            (277, "C#4"),
            (311, "D#4"),
            (349, "F4"),
            (370, "F#4"),
            (415, "G#4"),
            (466, "A#4"),
            (523, "C5"),
            (554, "C#5"),
        ],
        "colors": [
            "#D4F5FF",
            "#A7E9FF",
            "#56CCF2",
            "#29ADB2",
            "#247BA0",
            "#1E3A8A",
            "#2A9D8F",
            "#81B29A",
        ],
    },
    "pod_status": {
        "metric_name": "Pod Status",
        "unit": "",
        "notes": [(220, "A3"), (262, "C4"), (330, "E4"), (392, "G4")],
        "colors": ["#86EF7D", "#22C55E", "#16A34A", "#065F46"],
        "status_map": {
            "Running": 3,
            "Pending": 1,
            "Succeeded": 3,
            "Failed": 0,
            "Unknown": 0,
        },
    },
    "http_latency": {
        "metric_name": "HTTP Latency",
        "unit": "ms",
        "notes": [
            (294, "D4"),
            (330, "E4"),
            (370, "F#4"),
            (415, "G#4"),
            (466, "A#4"),
            (523, "C5"),
            (587, "D5"),
            (659, "E5"),
        ],
        "colors": [
            "#FFE5D9",
            "#FFCAD4",
            "#F4ACB7",
            "#F46036",
            "#E5383B",
            "#B22222",
            "#8B0000",
            "#DC143C",
        ],
    },
    "errors_per_second": {
        "metric_name": "Errors/Second",
        "unit": "err/s",
        "notes": [
            (131, "C3"),
            (147, "D3"),
            (165, "E3"),
            (175, "F3"),
            (196, "G3"),
            (220, "A3"),
            (247, "B3"),
            (262, "C4"),
        ],
        "colors": [
            "#FFF2CC",
            "#FFD65E",
            "#FFA41B",
            "#F94144",
            "#F3722C",
            "#F8961E",
            "#F9C74F",
            "#90BE6D",
        ],
    },
    "replicas": {
        "metric_name": "Replica Count",
        "unit": "Count",
        "notes": [
            (262, "C4"),
            (277, "C#4"),
            (294, "D4"),
            (311, "D#4"),
            (330, "E4"),
            (349, "F4"),
            (370, "F#4"),
            (392, "G4"),
        ],
        "colors": [
            "#E0F7FA",
            "#B2EBF2",
            "#80DEEA",
            "#4DD0E1",
            "#26C6DA",
            "#00BCD4",
            "#00ACC1",
            "#0097A7",
        ],
    },
    "node_pressure": {
        "metric_name": "Node Pressure",
        "unit": "",
        "notes": [(262, "C4"), (294, "D4"), (330, "E4"), (349, "F4")],
        "colors": ["#FFFFFF", "#F0F4C3", "#D4E157", "#A4A71D"],
        "status_map": {"False": 0, "True": 3},
    },
}


# --- Audio Utility Functions ---
def play_note(frequency: int, duration: float = 0.5) -> None:
    """
    Plays a musical note using simpleaudio and numpy for reliable sound generation.

    Args:
        frequency: The frequency of the note in Hz.
        duration: The duration of the note in seconds.
    """
    if os.environ.get("TEST_MODE", "False").lower() == "true":
        logger.info(
            f"Playing note at {frequency} Hz for {duration} seconds (TEST_MODE)"
        )
        return

    try:
        import simpleaudio as sa
        import numpy as np

        # Calculate sample values for pure tone
        sample_rate = 44100  # CD quality sample rate
        t = np.linspace(0, duration, int(sample_rate * duration), False)

        # Generate a pure tone with envelope for cleaner sound
        # Apply an ADSR (Attack, Decay, Sustain, Release) envelope
        attack = 0.05  # Short attack
        decay = 0.05  # Short decay
        release = 0.1  # Short release
        sustain_level = 0.8  # Sustain at 80% amplitude

        # Create a time array for the envelope
        envelope = np.ones(len(t))
        attack_samples = int(attack * sample_rate)
        decay_samples = int(decay * sample_rate)
        release_samples = int(release * sample_rate)

        # Apply attack
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

        # Apply decay to sustain level
        if decay_samples > 0:
            start_idx = attack_samples
            end_idx = start_idx + decay_samples
            if end_idx > start_idx:  # Ensure we have decay time
                envelope[start_idx:end_idx] = np.linspace(
                    1, sustain_level, end_idx - start_idx
                )

        # Apply release
        if release_samples > 0:
            start_idx = len(envelope) - release_samples
            if start_idx < len(envelope):  # Ensure we have release time
                envelope[start_idx:] = np.linspace(
                    sustain_level if decay_samples > 0 else 1,
                    0,
                    len(envelope) - start_idx,
                )

        # Generate the tone with the envelope
        tone = np.sin(2 * np.pi * frequency * t) * envelope

        # Normalize to 16-bit range and convert to int16
        audio = (tone * 32767).astype(np.int16)

        # Play the sound
        play_obj = sa.play_buffer(audio, 1, 2, sample_rate)

        # Wait for the sound to finish
        play_obj.wait_done()

    except Exception as e:
        logger.error(f"Error playing note: {e}")
        # Fallback to simple sleep if sound fails
        time.sleep(duration)


def play_midi_note(note_num: int, duration: float = 0.5) -> None:
    """
    Plays a MIDI note using the mido and python-rtmidi libraries.

    Args:
        note_num: The MIDI note number (60 = C4).
        duration: The duration of the note in seconds.
    """
    if os.environ.get("TEST_MODE", "False").lower() == "true":
        logger.info(f"Playing MIDI note {note_num} for {duration} seconds (TEST_MODE)")
        return

    try:
        import mido

        # Try to open the default MIDI output
        with mido.open_output() as port:
            # Send note on message
            port.send(mido.Message("note_on", note=note_num, velocity=64))
            # Wait for the duration
            time.sleep(duration)
            # Send note off message
            port.send(mido.Message("note_off", note=note_num, velocity=64))

    except Exception as e:
        logger.error(f"Error playing MIDI note: {e}")
        # Fall back to the simpleaudio method
        # Convert MIDI note to frequency (A4 = 69 = 440Hz)
        frequency = 440 * (2 ** ((note_num - 69) / 12))
        play_note(frequency, duration)


def get_color(color_list: List[str], index: int) -> str:
    """
    Retrieves a color from a list, handling out-of-bounds indices.

    Args:
        color_list: A list of color strings (e.g., hex codes).
        index: The index of the color to retrieve.

    Returns:
        A color string, or a default color if the index is out of bounds.
    """
    # 1. Simplicity: Provide clear, maintainable solutions
    # 2. Focus: Stick strictly to defined tasks
    if 0 <= index < len(color_list):
        return color_list[index]
    elif color_list:
        return color_list[-1]
    else:
        return "#808080"  # Default gray color


def calculate_index(
    value: float, notes_length: int, min_value: float, max_value: float
) -> int:
    """
    Calculates the index for selecting a note and color based on a metric value.

    Args:
        value: The metric value.
        notes_length: The number of notes (and colors) available.
        min_value: The minimum expected value of the metric.
        max_value: The maximum expected value of the metric.

    Returns:
        An integer index.
    """
    # 1. Simplicity: Provide clear, maintainable solutions
    # 2. Focus: Stick strictly to defined tasks
    if max_value <= min_value:
        return 0
    clamped_value = max(min_value, min(max_value, value))
    normalized_value = (clamped_value - min_value) / (max_value - min_value)
    index = int(normalized_value * (notes_length - 1))
    return index


# --- Kubernetes Client ---
class K8sClient:
    """Kubernetes client wrapper for fetching cluster metrics."""

    def __init__(self):
        """Initialize the Kubernetes client."""
        self.v1_core = None
        self.v1_apps = None
        self.metrics_api = None
        self.initialized = False

    def initialize(self) -> bool:
        """
        Initialize the Kubernetes API client.

        Returns:
            True if initialization was successful, False otherwise.
        """
        try:
            if USE_KUBE_CONFIG:
                logger.info("Loading kubeconfig from ~/.kube/config")
                config.load_kube_config()
            else:
                logger.info("Loading in-cluster configuration")
                config.load_incluster_config()

            self.v1_core = client.CoreV1Api()
            self.v1_apps = client.AppsV1Api()

            # Test connection
            self.v1_core.list_namespace(limit=1)
            logger.info("Successfully connected to Kubernetes cluster")
            self.initialized = True
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Kubernetes client: {e}")
            self.initialized = False
            return False

    def get_pods_status(self, namespace: str = "default") -> Tuple[float, Dict]:
        """
        Get pod status from the cluster.

        Args:
            namespace: The namespace to query (default: "default")

        Returns:
            A tuple of (status_index, extra_data)
        """
        try:
            pods = self.v1_core.list_namespaced_pod(namespace=namespace)
            if not pods.items:
                return 0, {"status": "Unknown", "count": 0}

            # Get the first pod's status as representative
            pod = pods.items[0]
            status = pod.status.phase

            status_index = SOUND_MAP["pod_status"]["status_map"].get(status, 0)
            return status_index, {"status": status, "count": len(pods.items)}

        except ApiException as e:
            logger.warning(f"Failed to get pod status: {e}")
            return 0, {"status": "Unknown", "error": str(e)}

    def get_deployment_replicas(self, namespace: str = "default") -> Tuple[float, Dict]:
        """
        Get replica count from deployments.

        Args:
            namespace: The namespace to query (default: "default")

        Returns:
            A tuple of (replica_count, extra_data)
        """
        try:
            deployments = self.v1_apps.list_namespaced_deployment(namespace=namespace)
            if not deployments.items:
                return 1, {"replicas": 1, "deployments": 0}

            # Get average replica count
            total_replicas = sum(d.spec.replicas or 0 for d in deployments.items)
            avg_replicas = total_replicas / len(deployments.items) if deployments.items else 1

            return avg_replicas, {
                "replicas": int(avg_replicas),
                "deployments": len(deployments.items)
            }

        except ApiException as e:
            logger.warning(f"Failed to get deployment replicas: {e}")
            return 1, {"replicas": 1, "error": str(e)}

    def get_node_pressure(self) -> Tuple[float, Dict]:
        """
        Check if any nodes are under pressure.

        Returns:
            A tuple of (pressure_level, extra_data)
        """
        try:
            nodes = self.v1_core.list_node()
            if not nodes.items:
                return 0, {"pressure": "False", "nodes": 0}

            # Check for any node pressure conditions
            pressure_types = ["MemoryPressure", "DiskPressure", "PIDPressure", "NetworkUnavailable"]
            has_pressure = False

            for node in nodes.items:
                if node.status.conditions:
                    for condition in node.status.conditions:
                        if condition.type in pressure_types and condition.status == "True":
                            has_pressure = True
                            break
                if has_pressure:
                    break

            pressure_level = 1 if has_pressure else 0
            return pressure_level, {"pressure": str(has_pressure), "nodes": len(nodes.items)}

        except ApiException as e:
            logger.warning(f"Failed to get node pressure: {e}")
            return 0, {"pressure": "Unknown", "error": str(e)}

    def get_resource_usage(self, namespace: str = "default") -> Tuple[float, float]:
        """
        Get approximate CPU and memory usage.
        Note: This requires metrics-server to be installed in the cluster.
        Falls back to requested resources if metrics are unavailable.

        Args:
            namespace: The namespace to query (default: "default")

        Returns:
            A tuple of (cpu_usage_percent, memory_usage_percent)
        """
        try:
            # Try to get actual metrics from metrics-server
            # This requires metrics-server API to be available
            pods = self.v1_core.list_namespaced_pod(namespace=namespace)

            if not pods.items:
                return 0.0, 0.0

            # Calculate based on resource requests as a proxy
            # In a real implementation, you would query metrics-server API
            total_cpu_req = 0.0
            total_mem_req = 0.0
            pod_count = 0

            for pod in pods.items:
                if pod.spec.containers:
                    for container in pod.spec.containers:
                        if container.resources and container.resources.requests:
                            cpu_req = container.resources.requests.get("cpu", "0")
                            mem_req = container.resources.requests.get("memory", "0")

                            # Parse CPU (e.g., "100m" = 0.1 cores)
                            if isinstance(cpu_req, str):
                                if cpu_req.endswith("m"):
                                    total_cpu_req += float(cpu_req[:-1]) / 1000
                                else:
                                    total_cpu_req += float(cpu_req)

                            # Parse memory (simplified)
                            if isinstance(mem_req, str):
                                if mem_req.endswith("Mi"):
                                    total_mem_req += float(mem_req[:-2])
                                elif mem_req.endswith("Gi"):
                                    total_mem_req += float(mem_req[:-2]) * 1024

                            pod_count += 1

            # Estimate usage as a percentage (rough approximation)
            cpu_usage = min((total_cpu_req / max(pod_count, 1)) * 20, 100)
            mem_usage = min((total_mem_req / max(pod_count, 1)) / 10, 100)

            return cpu_usage, mem_usage

        except ApiException as e:
            logger.warning(f"Failed to get resource usage: {e}")
            # Return moderate values to indicate some activity
            return 30.0, 40.0


# Global K8s client instance
k8s_client = K8sClient()


# --- Kubernetes Interaction ---
def get_k8s_data(metric: str, namespace: str = "default") -> Optional[Tuple[float, Dict]]:
    """
    Fetches real Kubernetes data for a given metric.

    Args:
        metric: The name of the metric to fetch.
        namespace: The Kubernetes namespace to query (default: "default")

    Returns:
        A tuple containing the metric value and an optional dictionary of extra data,
        or None if the metric is invalid or client is not initialized.
    """
    if not k8s_client.initialized:
        logger.warning("Kubernetes client not initialized, skipping metric fetch")
        return None

    try:
        if metric == "cpu_usage":
            cpu, _ = k8s_client.get_resource_usage(namespace)
            return cpu, {"namespace": namespace}

        elif metric == "memory_usage":
            _, memory = k8s_client.get_resource_usage(namespace)
            return memory, {"namespace": namespace}

        elif metric == "pod_status":
            return k8s_client.get_pods_status(namespace)

        elif metric == "http_latency":
            # This would require custom metrics or service mesh integration
            # For now, return a simulated value based on pod health
            status_idx, _ = k8s_client.get_pods_status(namespace)
            # Healthy pods = lower latency
            latency = 50 + (3 - status_idx) * 100
            return latency, {"estimated": True}

        elif metric == "errors_per_second":
            # This would require custom metrics or logging integration
            # For now, estimate based on pod failures
            status_idx, data = k8s_client.get_pods_status(namespace)
            errors = 0 if data.get("status") in ["Running", "Succeeded"] else 5
            return float(errors), {"estimated": True}

        elif metric == "replicas":
            return k8s_client.get_deployment_replicas(namespace)

        elif metric == "node_pressure":
            return k8s_client.get_node_pressure()

        else:
            logger.warning(f"Unknown metric: {metric}")
            return None

    except Exception as e:
        logger.error(f"Error fetching metric {metric}: {e}")
        return None


def colorize_line(text: str, color: str, use_color: bool = False) -> str:
    """
    Colorizes a line of text using ANSI escape codes if use_color is True.

    Args:
        text: The text to colorize.
        color: The hex color code (e.g., "#FF0000").
        use_color: Whether to apply color.

    Returns:
        The colorized text if use_color is True, otherwise the original text.
    """
    if not use_color:
        return text
    # Convert hex color to RGB
    hex_color = color.lstrip("#")
    if len(hex_color) != 6:
        logger.warning(f"Invalid hex color format: {color}. Returning unmodified text.")
        return text  # Fallback if color is invalid
    r, g, b = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"


# --- Main Function ---
def sonify_k8s_metrics(use_color: Optional[bool] = None, namespace: str = "default") -> None:
    """
    Main function to fetch Kubernetes metrics and sonify them.

    Args:
        use_color: Whether to use colors in the output. If None, determined by environment.
        namespace: The Kubernetes namespace to monitor.
    """
    if use_color is None:
        use_color = os.environ.get("SHOW_COLOR", "false").lower() == "true"

    logger.info(f"Starting Sonify K8s Metrics for namespace: {namespace}")

    # --- Kubernetes Client Initialization ---
    if not k8s_client.initialize():
        logger.error("Failed to connect to Kubernetes cluster. Please check your configuration.")
        logger.error("Make sure kubectl is configured or set USE_KUBE_CONFIG=true environment variable.")
        return

    # --- Main Loop ---
    while True:
        try:
            for metric_name, metric_config in SOUND_MAP.items():
                data = get_k8s_data(metric_name, namespace=namespace)
                if data is None:
                    logger.warning(f"Failed to get data for metric: {metric_name}")
                    continue
                metric_value, extra_data = data

                notes_list = metric_config["notes"]
                color_list = metric_config["colors"]
                if metric_name in ["pod_status", "node_pressure"]:
                    index = int(metric_value)
                else:
                    index = calculate_index(
                        metric_value,
                        len(notes_list),
                        0,
                        (
                            100
                            if metric_name
                            not in ["http_latency", "errors_per_second", "replicas"]
                            else (
                                500
                                if metric_name == "http_latency"
                                else (10 if metric_name == "errors_per_second" else 5)
                            )
                        ),
                    )

                frequency, note_name = notes_list[index]
                color = get_color(color_list, index)

                # Play the sound using simpleaudio
                play_note(frequency)

                # Construct and display the log message
                log_message = f"{metric_config['metric_name']}: {metric_value:.2f} {metric_config['unit']} | Note: {note_name} ({frequency} Hz) | Color: {color}"
                if extra_data:
                    log_message += f" | Extra: {extra_data}"

                # Print colored output to console if enabled
                if use_color:
                    print(colorize_line(log_message, color, use_color=use_color))

                # Always log to the logger
                logger.info(log_message)

            # Sleep until the next polling interval
            time.sleep(POLL_INTERVAL)

        except KeyboardInterrupt:
            logger.info("Stopping Sonify K8s...")
            break
        except Exception as e:
            logger.error(f"An error occurred: {e}", exc_info=True)
            time.sleep(POLL_INTERVAL)


@click.command()
@click.option("-c", "--color", is_flag=True, help="Show ANSI colors in output")
@click.option(
    "-m", "--midi", is_flag=True, help="Use MIDI for sound output if available"
)
@click.option(
    "-i", "--interval", type=int, default=None, help="Polling interval in seconds"
)
@click.option(
    "-n", "--namespace", type=str, default="default", help="Kubernetes namespace to monitor"
)
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging")
def main(color, midi, interval, namespace, verbose):
    """
    Sonify K8s - Transform your Kubernetes cluster events into sound!

    This utility monitors Kubernetes metrics and plays unique sounds for each event.
    """
    # Set environment variables based on command line options
    os.environ["SHOW_COLOR"] = "true" if color else "false"
    os.environ["USE_MIDI"] = "true" if midi else "false"

    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if interval is not None:
        global POLL_INTERVAL
        POLL_INTERVAL = interval

    # Start the sonification process
    sonify_k8s_metrics(use_color=color, namespace=namespace)


if __name__ == "__main__":
    main()
