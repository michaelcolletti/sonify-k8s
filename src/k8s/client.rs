/// Kubernetes client for fetching cluster metrics
use crate::error::{Result, SonifyError};
use k8s_openapi::api::apps::v1::Deployment;
use k8s_openapi::api::core::v1::{Node, Pod};
use kube::{Api, Client, Config};
use std::collections::HashMap;

pub struct K8sClient {
    client: Option<Client>,
    namespace: String,
}

impl K8sClient {
    /// Create a new uninitialized K8s client
    pub fn new(namespace: String) -> Self {
        Self {
            client: None,
            namespace,
        }
    }

    /// Initialize the Kubernetes client
    pub async fn initialize(&mut self, use_kubeconfig: bool) -> Result<()> {
        let config = if use_kubeconfig {
            tracing::info!("Loading kubeconfig from ~/.kube/config");
            Config::infer().await
                .map_err(|e| SonifyError::KubeConfigError(e.to_string()))?
        } else {
            tracing::info!("Loading in-cluster configuration");
            Config::incluster()
                .map_err(|e| SonifyError::KubeConfigError(e.to_string()))?
        };

        let client = Client::try_from(config)?;

        // Test connection
        let pods: Api<Pod> = Api::namespaced(client.clone(), &self.namespace);
        pods.list(&Default::default()).await?;

        tracing::info!("Successfully connected to Kubernetes cluster");
        self.client = Some(client);
        Ok(())
    }

    fn client(&self) -> Result<&Client> {
        self.client
            .as_ref()
            .ok_or(SonifyError::ClientNotInitialized)
    }

    /// Get pod status from the cluster
    pub async fn get_pods_status(&self) -> Result<(f64, HashMap<String, String>)> {
        let client = self.client()?;
        let pods: Api<Pod> = Api::namespaced(client.clone(), &self.namespace);

        let pod_list = pods.list(&Default::default()).await?;

        if pod_list.items.is_empty() {
            let mut extra = HashMap::new();
            extra.insert("status".to_string(), "Unknown".to_string());
            extra.insert("count".to_string(), "0".to_string());
            return Ok((0.0, extra));
        }

        // Get the first pod's status as representative
        let pod = &pod_list.items[0];
        let status = pod
            .status
            .as_ref()
            .and_then(|s| s.phase.clone())
            .unwrap_or_else(|| "Unknown".to_string());

        // Map status to index
        let status_index = match status.as_str() {
            "Running" => 3.0,
            "Succeeded" => 3.0,
            "Pending" => 1.0,
            "Failed" => 0.0,
            _ => 0.0,
        };

        let mut extra = HashMap::new();
        extra.insert("status".to_string(), status);
        extra.insert("count".to_string(), pod_list.items.len().to_string());

        Ok((status_index, extra))
    }

    /// Get deployment replicas
    pub async fn get_deployment_replicas(&self) -> Result<(f64, HashMap<String, String>)> {
        let client = self.client()?;
        let deployments: Api<Deployment> = Api::namespaced(client.clone(), &self.namespace);

        let deployment_list = deployments.list(&Default::default()).await?;

        if deployment_list.items.is_empty() {
            let mut extra = HashMap::new();
            extra.insert("replicas".to_string(), "1".to_string());
            extra.insert("deployments".to_string(), "0".to_string());
            return Ok((1.0, extra));
        }

        // Calculate average replica count
        let total_replicas: i32 = deployment_list
            .items
            .iter()
            .filter_map(|d| d.spec.as_ref())
            .filter_map(|spec| spec.replicas)
            .sum();

        let avg_replicas = if deployment_list.items.is_empty() {
            1.0
        } else {
            total_replicas as f64 / deployment_list.items.len() as f64
        };

        let mut extra = HashMap::new();
        extra.insert("replicas".to_string(), avg_replicas.to_string());
        extra.insert(
            "deployments".to_string(),
            deployment_list.items.len().to_string(),
        );

        Ok((avg_replicas, extra))
    }

    /// Check for node pressure
    pub async fn get_node_pressure(&self) -> Result<(f64, HashMap<String, String>)> {
        let client = self.client()?;
        let nodes: Api<Node> = Api::all(client.clone());

        let node_list = nodes.list(&Default::default()).await?;

        if node_list.items.is_empty() {
            let mut extra = HashMap::new();
            extra.insert("pressure".to_string(), "False".to_string());
            extra.insert("nodes".to_string(), "0".to_string());
            return Ok((0.0, extra));
        }

        // Check for pressure conditions
        let pressure_types = vec![
            "MemoryPressure",
            "DiskPressure",
            "PIDPressure",
            "NetworkUnavailable",
        ];

        let mut has_pressure = false;

        for node in &node_list.items {
            if let Some(status) = &node.status {
                if let Some(conditions) = &status.conditions {
                    for condition in conditions {
                        if pressure_types.contains(&condition.type_.as_str())
                            && condition.status == "True"
                        {
                            has_pressure = true;
                            break;
                        }
                    }
                }
            }
            if has_pressure {
                break;
            }
        }

        let pressure_level = if has_pressure { 1.0 } else { 0.0 };

        let mut extra = HashMap::new();
        extra.insert("pressure".to_string(), has_pressure.to_string());
        extra.insert("nodes".to_string(), node_list.items.len().to_string());

        Ok((pressure_level, extra))
    }

    /// Get resource usage (estimated from requests)
    pub async fn get_resource_usage(&self) -> Result<(f64, f64)> {
        let client = self.client()?;
        let pods: Api<Pod> = Api::namespaced(client.clone(), &self.namespace);

        let pod_list = pods.list(&Default::default()).await?;

        if pod_list.items.is_empty() {
            return Ok((0.0, 0.0));
        }

        let mut total_cpu_req = 0.0;
        let mut total_mem_req = 0.0;
        let mut pod_count = 0;

        for pod in &pod_list.items {
            if let Some(spec) = &pod.spec {
                for container in &spec.containers {
                    if let Some(resources) = &container.resources {
                        if let Some(requests) = &resources.requests {
                            // Parse CPU
                            if let Some(cpu) = requests.get("cpu") {
                                let cpu_str = cpu.0.as_str();
                                total_cpu_req += parse_cpu(cpu_str);
                            }

                            // Parse memory
                            if let Some(mem) = requests.get("memory") {
                                let mem_str = mem.0.as_str();
                                total_mem_req += parse_memory(mem_str);
                            }

                            pod_count += 1;
                        }
                    }
                }
            }
        }

        // Estimate usage as percentage (rough approximation)
        let cpu_usage = if pod_count > 0 {
            ((total_cpu_req / pod_count as f64) * 20.0).min(100.0)
        } else {
            30.0
        };

        let mem_usage = if pod_count > 0 {
            ((total_mem_req / pod_count as f64) / 10.0).min(100.0)
        } else {
            40.0
        };

        Ok((cpu_usage, mem_usage))
    }
}

/// Parse CPU string (e.g., "100m" = 0.1 cores)
fn parse_cpu(cpu_str: &str) -> f64 {
    if cpu_str.ends_with('m') {
        cpu_str
            .trim_end_matches('m')
            .parse::<f64>()
            .unwrap_or(0.0)
            / 1000.0
    } else {
        cpu_str.parse::<f64>().unwrap_or(0.0)
    }
}

/// Parse memory string (e.g., "100Mi" = 100 MiB)
fn parse_memory(mem_str: &str) -> f64 {
    if mem_str.ends_with("Mi") {
        mem_str
            .trim_end_matches("Mi")
            .parse::<f64>()
            .unwrap_or(0.0)
    } else if mem_str.ends_with("Gi") {
        mem_str
            .trim_end_matches("Gi")
            .parse::<f64>()
            .unwrap_or(0.0)
            * 1024.0
    } else {
        0.0
    }
}
