use serde::{Deserialize, Serialize};
use std::sync::Mutex;
use tauri::State;

// ── Types ──────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NodeStatus {
    pub running: bool,
    pub peer_count: u32,
    pub uptime_seconds: u64,
    pub version: String,
    pub backend: String,
    pub model: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ModelInfo {
    pub name: String,
    pub params: String,
    pub size: String,
    pub downloaded: bool,
    pub description: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InferenceRequest {
    pub prompt: String,
    pub model: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InferenceResponse {
    pub text: String,
    pub tokens_per_second: f64,
    pub model: String,
    pub energy_mj: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DownloadProgress {
    pub model: String,
    pub progress: f64,
    pub status: String,
}

// ── State ──────────────────────────────────────────────────────────

pub struct AriaState {
    pub node_running: Mutex<bool>,
    pub api_base: Mutex<String>,
}

impl Default for AriaState {
    fn default() -> Self {
        Self {
            node_running: Mutex::new(false),
            api_base: Mutex::new("http://127.0.0.1:3000".to_string()),
        }
    }
}

// ── Commands ───────────────────────────────────────────────────────

#[tauri::command]
pub fn get_system_info() -> serde_json::Value {
    serde_json::json!({
        "os": std::env::consts::OS,
        "arch": std::env::consts::ARCH,
        "version": env!("CARGO_PKG_VERSION"),
    })
}

#[tauri::command]
pub fn get_app_version() -> String {
    env!("CARGO_PKG_VERSION").to_string()
}

#[tauri::command]
pub async fn get_node_status(state: State<'_, AriaState>) -> Result<NodeStatus, String> {
    let running = *state.node_running.lock().map_err(|e| e.to_string())?;
    let api_base = state.api_base.lock().map_err(|e| e.to_string())?.clone();

    if !running {
        return Ok(NodeStatus {
            running: false,
            peer_count: 0,
            uptime_seconds: 0,
            version: env!("CARGO_PKG_VERSION").to_string(),
            backend: "none".to_string(),
            model: None,
        });
    }

    // Try to reach the ARIA API for live status
    let client = reqwest::Client::new();
    match client
        .get(format!("{}/v1/status", api_base))
        .timeout(std::time::Duration::from_secs(3))
        .send()
        .await
    {
        Ok(resp) => {
            if let Ok(status) = resp.json::<NodeStatus>().await {
                return Ok(status);
            }
            Ok(NodeStatus {
                running: true,
                peer_count: 0,
                uptime_seconds: 0,
                version: env!("CARGO_PKG_VERSION").to_string(),
                backend: "unknown".to_string(),
                model: None,
            })
        }
        Err(_) => Ok(NodeStatus {
            running,
            peer_count: 0,
            uptime_seconds: 0,
            version: env!("CARGO_PKG_VERSION").to_string(),
            backend: "offline".to_string(),
            model: None,
        }),
    }
}

#[tauri::command]
pub async fn start_node(
    state: State<'_, AriaState>,
    app: tauri::AppHandle,
) -> Result<String, String> {
    let already_running = *state.node_running.lock().map_err(|e| e.to_string())?;
    if already_running {
        return Err("Node is already running".to_string());
    }

    // Launch ARIA node as a sidecar / subprocess
    let shell = app
        .shell()
        .sidecar("aria")
        .map_err(|e| format!("Failed to find aria sidecar: {}", e))?
        .args(["node", "start", "--port", "8765", "--api-port", "3000"]);

    let (_rx, _child) = shell
        .spawn()
        .map_err(|e| format!("Failed to start node: {}", e))?;

    *state.node_running.lock().map_err(|e| e.to_string())? = true;

    Ok("Node started successfully".to_string())
}

#[tauri::command]
pub async fn stop_node(state: State<'_, AriaState>) -> Result<String, String> {
    let running = *state.node_running.lock().map_err(|e| e.to_string())?;
    if !running {
        return Err("Node is not running".to_string());
    }

    let api_base = state.api_base.lock().map_err(|e| e.to_string())?.clone();
    let client = reqwest::Client::new();

    // Request graceful shutdown via API
    let _ = client
        .post(format!("{}/v1/shutdown", api_base))
        .timeout(std::time::Duration::from_secs(5))
        .send()
        .await;

    *state.node_running.lock().map_err(|e| e.to_string())? = false;

    Ok("Node stopped".to_string())
}

#[tauri::command]
pub async fn get_models(state: State<'_, AriaState>) -> Result<Vec<ModelInfo>, String> {
    let api_base = state.api_base.lock().map_err(|e| e.to_string())?.clone();
    let client = reqwest::Client::new();

    match client
        .get(format!("{}/v1/models", api_base))
        .timeout(std::time::Duration::from_secs(5))
        .send()
        .await
    {
        Ok(resp) => {
            if let Ok(models) = resp.json::<Vec<ModelInfo>>().await {
                return Ok(models);
            }
            // Return default model list if API is unavailable
            Ok(default_models())
        }
        Err(_) => Ok(default_models()),
    }
}

#[tauri::command]
pub async fn download_model(
    name: String,
    state: State<'_, AriaState>,
) -> Result<DownloadProgress, String> {
    let api_base = state.api_base.lock().map_err(|e| e.to_string())?.clone();
    let client = reqwest::Client::new();

    match client
        .post(format!("{}/v1/models/download", api_base))
        .json(&serde_json::json!({ "name": name }))
        .timeout(std::time::Duration::from_secs(10))
        .send()
        .await
    {
        Ok(resp) => {
            if let Ok(progress) = resp.json::<DownloadProgress>().await {
                return Ok(progress);
            }
            Ok(DownloadProgress {
                model: name,
                progress: 0.0,
                status: "queued".to_string(),
            })
        }
        Err(e) => Err(format!("Failed to start download: {}", e)),
    }
}

#[tauri::command]
pub async fn send_inference(
    prompt: String,
    model: String,
    state: State<'_, AriaState>,
) -> Result<InferenceResponse, String> {
    let api_base = state.api_base.lock().map_err(|e| e.to_string())?.clone();
    let client = reqwest::Client::new();

    let payload = serde_json::json!({
        "model": model,
        "messages": [
            { "role": "user", "content": prompt }
        ],
        "stream": false,
    });

    match client
        .post(format!("{}/v1/chat/completions", api_base))
        .json(&payload)
        .timeout(std::time::Duration::from_secs(120))
        .send()
        .await
    {
        Ok(resp) => {
            let body: serde_json::Value = resp.json().await.map_err(|e| e.to_string())?;

            let text = body["choices"][0]["message"]["content"]
                .as_str()
                .unwrap_or("No response")
                .to_string();

            let tokens_per_second = body["usage"]["tokens_per_second"]
                .as_f64()
                .unwrap_or(0.0);

            let energy_mj = body["usage"]["energy_mj"].as_f64().unwrap_or(0.0);

            Ok(InferenceResponse {
                text,
                tokens_per_second,
                model,
                energy_mj,
            })
        }
        Err(e) => Err(format!("Inference request failed: {}", e)),
    }
}

// ── Helpers ────────────────────────────────────────────────────────

fn default_models() -> Vec<ModelInfo> {
    vec![
        ModelInfo {
            name: "BitNet-b1.58-large".to_string(),
            params: "0.7B".to_string(),
            size: "400 MB".to_string(),
            downloaded: false,
            description: "Fast, lightweight model for quick responses".to_string(),
        },
        ModelInfo {
            name: "BitNet-b1.58-2B-4T".to_string(),
            params: "2.4B".to_string(),
            size: "1.3 GB".to_string(),
            downloaded: false,
            description: "Best balance of speed and quality".to_string(),
        },
        ModelInfo {
            name: "Llama3-8B-1.58".to_string(),
            params: "8.0B".to_string(),
            size: "4.2 GB".to_string(),
            downloaded: false,
            description: "Most capable model, requires more RAM".to_string(),
        },
    ]
}
