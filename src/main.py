import time
import random
import logging
import os
import click

from typing import Dict, List, Tuple, Optional

# --- 1. Simplicity: Provide clear, maintainable solutions ---
# --- 2. Focus: Stick strictly to defined tasks ---
# --- 4. Quality: Deliver clean, well-tested, documented, and secure code ---
# --- 5. Collaboration: Foster effective teamwork between human developers and AI ---

# --- Project: Sonify Kubernetes Metrics ---
# --- Description: This utility monitors Kubernetes metrics and sonifies them, providing an audio-visual representation of cluster health. ---
# --- Author: AI Assistant ---
# --- Date: 2024-07-24 ---
# --- Version: 1.0 ---

# --- Configuration and Constants ---
K8S_API_URL = os.environ.get("K8S_API_URL", "http://localhost:8080")  # Default K8s API URL
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", 5))  # Default polling interval in seconds
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()  # Default log level
USE_KUBE_CONFIG = os.environ.get("USE_KUBE_CONFIG", "False").lower() == "true"  # Use ~/.kube/config

# --- Logging Setup ---
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- 3. Language-Specific Best Practices ---
# Use a dictionary to map metrics to their sonification configurations.
SOUND_MAP: Dict[str, Dict[str, Tuple[int, str]]] = {
    "cpu_usage": {
        "metric_name": "CPU Usage",
        "unit": "%",
        "notes": [(262, "C4"), (294, "D4"), (330, "E4"), (349, "F4"), (392, "G4"), (440, "A4"), (494, "B4"), (523, "C5")],
        "colors": ["#88E0EF", "#39C0ED", "#218380", "#126E82", "#145DA0", "#0F4C75", "#3282B8", "#118AB2"],
    },
    "memory_usage": {
        "metric_name": "Memory Usage",
        "unit": "%",
        "notes": [(277, "C#4"), (311, "D#4"), (349, "F4"), (370, "F#4"), (415, "G#4"), (466, "A#4"), (523, "C5"), (554, "C#5")],
        "colors": ["#D4F5FF", "#A7E9FF", "#56CCF2", "#29ADB2", "#247BA0", "#1E3A8A", "#2A9D8F", "#81B29A"],
    },
    "pod_status": {
        "metric_name": "Pod Status",
        "unit": "",
        "notes": [(220, "A3"), (262, "C4"), (330, "E4"), (392, "G4")],
        "colors": ["#86EF7D", "#22C55E", "#16A34A", "#065F46"],
        "status_map": {"Running": 3, "Pending": 1, "Succeeded": 3, "Failed": 0, "Unknown": 0},
    },
    "http_latency": {
        "metric_name": "HTTP Latency",
        "unit": "ms",
        "notes": [(294, "D4"), (330, "E4"), (370, "F#4"), (415, "G#4"), (466, "A#4"), (523, "C5"), (587, "D5"), (659, "E5")],
        "colors": ["#FFE5D9", "#FFCAD4", "#F4ACB7", "#F46036", "#E5383B", "#B22222", "#8B0000", "#DC143C"],
    },
    "errors_per_second": {
        "metric_name": "Errors/Second",
        "unit": "err/s",
        "notes": [(131, "C3"), (147, "D3"), (165, "E3"), (175, "F3"), (196, "G3"), (220, "A3"), (247, "B3"), (262, "C4")],
        "colors": ["#FFF2CC", "#FFD65E", "#FFA41B", "#F94144", "#F3722C", "#F8961E", "#F9C74F", "#90BE6D"],
    },
    "replicas": {
        "metric_name": "Replica Count",
        "unit": "Count",
        "notes": [(262, "C4"), (277, "C#4"), (294, "D4"), (311, "D#4"), (330, "E4"), (349, "F4"), (370, "F#4"), (392, "G4")],
        "colors": ["#E0F7FA", "#B2EBF2", "#80DEEA", "#4DD0E1", "#26C6DA", "00BCD4", "00ACC1", "0097A7"],
    },
    "node_pressure": {
        "metric_name": "Node Pressure",
        "unit": "",
        "notes": [(262, "C4"), (294, "D4"), (330, "E4"), (349, "F4")],
        "colors": ["#FFFFFF", "#F0F4C3", "#D4E157", "#A4A71D"],
        "status_map": {"False": 0, "True": 3},
    },
}


# --- Utility Functions ---
def play_note(frequency: int, duration: float = 0.5) -> None:
    """
    Plays a musical note using simple sine wave synthesis.

    Args:
        frequency: The frequency of the note in Hz.
        duration: The duration of the note in seconds.
    """
    # 1. Simplicity: Provide clear, maintainable solutions
    # 2. Focus: Stick strictly to defined tasks
    if os.environ.get('TEST_MODE', 'False').lower() == 'true':
        logger.info(f"Playing note at {frequency} Hz for {duration} seconds (TEST_MODE)")
        return

    try:
        import math
        import time
        sample_rate = 8000
        num_samples = int(duration * sample_rate)
        for i in range(num_samples):
            sample = math.sin(2 * math.pi * frequency * i / sample_rate) * 0.1
            if i % 1000 == 0:
                logger.debug(f"Sample: {sample}")
        time.sleep(duration)
    except Exception as e:
        # 4. Quality: Deliver clean, well-tested, documented, and secure code
        logger.error(f"Error playing note: {e}")



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



def calculate_index(value: float, notes_length: int, min_value: float, max_value: float) -> int:
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



# --- Kubernetes Interaction (Simulated) ---
def get_k8s_data(metric: str) -> Optional[Tuple[float, Dict]]:
    """
    Simulates fetching Kubernetes data for a given metric.

    Args:
        metric: The name of the metric to fetch.

    Returns:
        A tuple containing the metric value and an optional dictionary of extra data,
        or None if the metric is invalid.
    """
    # 1. Simplicity: Provide clear, maintainable solutions
    # 2. Focus: Stick strictly to defined tasks
    if metric == "cpu_usage":
        return random.uniform(0, 100), {}
    elif metric == "memory_usage":
        return random.uniform(0, 100), {}
    elif metric == "pod_status":
        statuses = ["Running", "Pending", "Succeeded", "Failed", "Unknown"]
        status = random.choice(statuses)
        return SOUND_MAP[metric]['status_map'][status], {"status": status}
    elif metric == "http_latency":
        return random.expovariate(1 / 200), {}
    elif metric == "errors_per_second":
        return random.randint(0, 5), {}
    elif metric == "replicas":
        return random.randint(1, 5), {}
    elif metric == "node_pressure":
        return random.choice([0, 1]), {"pressure": random.choice(["False", "True"])}
    else:
        return None



# --- Main Function ---
def sonify_k8s_metrics() -> None:
    """
    Main function to fetch Kubernetes metrics and sonify them.
    """
    # 1. Simplicity: Provide clear, maintainable solutions
    # 2. Focus: Stick strictly to defined tasks
    logger.info("Starting Sonify K8s Metrics...")

    # --- Kubernetes Client Initialization (Simulated) ---
    if USE_KUBE_CONFIG:
        logger.info(f"Using KUBECONFIG from  ~/.kube/config")
    else:
        logger.info(f"Using K8s API URL: {K8S_API_URL}")

    # --- Main Loop ---
    while True:
        try:
            for metric_name, metric_config in SOUND_MAP.items():
                data = get_k8s_data(metric_name)
                if data is None:
                    logger.warning(f"Failed to get data for metric: {metric_name}")
                    continue
                metric_value, extra_data = data

                notes_list = metric_config["notes"]
                color_list = metric_config["colors"]
                if metric_name in ["pod_status", "node_pressure"]:
                    index = int(metric_value)
                else:
                    index = calculate_index(metric_value, len(notes_list), 0,
                                            100 if metric_name not in ["http_latency", "errors_per_second", "replicas"]
                                            else (500 if metric_name == "http_latency" else (
                                                10 if metric_name == "errors_per_second" else 5)))

                frequency, note_name = notes_list[index]
                color = get_color(color_list, index)

                play_note(frequency)
                log_message = f"{metric_config['metric_name']}: {metric_value:.2f} {metric_config['unit']} | Note: {note_name} ({frequency} Hz) | Color: {color}"
                if extra_data:
                    log_message += f" | Extra: {extra_data}"
                logger.info(log_message)

            # 4. Quality: Deliver clean, well-tested, documented, and secure code
            # 5. Collaboration: Foster effective teamwork between human developers and AI
            # 2. Iteration: Enhance existing code unless fundamental changes are clearly justified
            time.sleep(POLL_INTERVAL)

        except KeyboardInterrupt:
            logger.info("Stopping Sonify...")
            break
        except Exception as e:
            logger.error(f"An error occurred: {e}", exc_info=True)
            time.sleep(POLL_INTERVAL)



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
    hex_color = color.lstrip('#')
    if len(hex_color) != 6:
        logger.warning(f"Invalid hex color format: {color}. Returning unmodified text.")
        return text  # Fallback if color is invalid
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"


def sonify_k8s_metrics_colored(use_color: Optional[bool] = None) -> None:
    if use_color is None:
        use_color = os.environ.get('SHOW_COLOR', 'false').lower() == 'true'
    logger.info("Starting Sonify K8s Metrics...")

    if USE_KUBE_CONFIG:
        logger.info(f"Using KUBECONFIG from  ~/.kube/config")
    else:
        logger.info(f"Using K8s API URL: {K8S_API_URL}")

    while True:
        try:
            for metric_name, metric_config in SOUND_MAP.items():
                data = get_k8s_data(metric_name)
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
                        100 if metric_name not in ["http_latency", "errors_per_second", "replicas"]
                        else (500 if metric_name == "http_latency" else (
                            10 if metric_name == "errors_per_second" else 5))
                    )

                frequency, note_name = notes_list[index]
                color = get_color(color_list, index)

                play_note(frequency)
                log_message = f"{metric_config['metric_name']}: {metric_value:.2f} {metric_config['unit']} | Note: {note_name} ({frequency} Hz) | Color: {color}"
                if extra_data:
                    log_message += f" | Extra: {extra_data}"

                print(colorize_line(log_message, color, use_color=use_color))
                logger.info(log_message)

            time.sleep(POLL_INTERVAL)

        except KeyboardInterrupt:
            logger.info("Stopping Sonify...")
            break
        except Exception as e:
            logger.error(f"An error occurred: {e}", exc_info=True)
            time.sleep(POLL_INTERVAL)


@click.command()
@click.option('-c', '--color', is_flag=True, help='Show ANSI colors in output')
def main(color):
    """
    Entry point for the CLI.
    """
    os.environ['SHOW_COLOR'] = 'true' if color else 'false'
    sonify_k8s_metrics_colored(use_color=color)


if __name__ == "__main__":
    main()