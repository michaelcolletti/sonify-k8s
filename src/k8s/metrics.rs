/// Metric fetching logic
use crate::error::Result;
use crate::k8s::client::K8sClient;
use std::collections::HashMap;

/// Get Kubernetes data for a specific metric
pub async fn get_k8s_data(
    metric: &str,
    client: &K8sClient,
) -> Result<Option<(f64, HashMap<String, String>)>> {
    match metric {
        "cpu_usage" => {
            let (cpu, _) = client.get_resource_usage().await?;
            let mut extra = HashMap::new();
            extra.insert("type".to_string(), "cpu".to_string());
            Ok(Some((cpu, extra)))
        }

        "memory_usage" => {
            let (_, memory) = client.get_resource_usage().await?;
            let mut extra = HashMap::new();
            extra.insert("type".to_string(), "memory".to_string());
            Ok(Some((memory, extra)))
        }

        "pod_status" => {
            let result = client.get_pods_status().await?;
            Ok(Some(result))
        }

        "http_latency" => {
            // Estimate based on pod health
            let (status_idx, _) = client.get_pods_status().await?;
            let latency = 50.0 + (3.0 - status_idx) * 100.0;
            let mut extra = HashMap::new();
            extra.insert("estimated".to_string(), "true".to_string());
            Ok(Some((latency, extra)))
        }

        "errors_per_second" => {
            // Estimate based on pod failures
            let (_status_idx, data) = client.get_pods_status().await?;
            let status = data.get("status").map(|s| s.as_str()).unwrap_or("Unknown");
            let errors = if status == "Running" || status == "Succeeded" {
                0.0
            } else {
                5.0
            };
            let mut extra = HashMap::new();
            extra.insert("estimated".to_string(), "true".to_string());
            Ok(Some((errors, extra)))
        }

        "replicas" => {
            let result = client.get_deployment_replicas().await?;
            Ok(Some(result))
        }

        "node_pressure" => {
            let result = client.get_node_pressure().await?;
            Ok(Some(result))
        }

        _ => {
            tracing::warn!("Unknown metric: {}", metric);
            Ok(None)
        }
    }
}
