use serde::{Deserialize, Serialize};
use std::process::{Child, Command, Stdio};
use std::sync::Mutex;
use tauri::{Manager, State};

// ── Types ──────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NodeStatus {
    pub running: bool,
    pub peer_count: u32,
    pub uptime_seconds: u64,
    pub version: String,
    pub backend: String,
    pub model: Option<String>,
    #[serde(default)]
    pub llama_cli_available: bool,
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

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StartNodeResult {
    pub status: String,
    pub backend: String,
    pub port: u16,
    pub pid: u32,
    pub models_available: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BackendInfo {
    pub python_found: bool,
    pub python_path: String,
    pub python_version: String,
    pub aria_installed: bool,
    pub aria_version: String,
    pub llama_cli_found: bool,
    pub models_found: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EnergySavings {
    pub energy_saved_kwh: f64,
    pub reduction_percent: f64,
    pub co2_saved_kg: f64,
    pub cost_saved_usd: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EnergyStats {
    pub total_inferences: u64,
    pub total_tokens_generated: u64,
    pub total_energy_kwh: f64,
    pub avg_energy_per_token_mj: f64,
    pub session_uptime_seconds: f64,
    pub savings: EnergySavings,
}

// ── State ──────────────────────────────────────────────────────────

pub struct AriaState {
    pub node_running: Mutex<bool>,
    pub api_base: Mutex<String>,
    pub api_port: Mutex<u16>,
    pub python_process: Mutex<Option<Child>>,
    pub start_time: Mutex<Option<std::time::Instant>>,
}

impl Default for AriaState {
    fn default() -> Self {
        Self {
            node_running: Mutex::new(false),
            api_base: Mutex::new("http://127.0.0.1:3000".to_string()),
            api_port: Mutex::new(3000),
            python_process: Mutex::new(None),
            start_time: Mutex::new(None),
        }
    }
}

// ── Python Detection ──────────────────────────────────────────────

/// Try multiple Python executable names and return the first one found.
fn find_python() -> Option<String> {
    let candidates = ["python", "python3", "python3.14", "python3.13", "python3.12"];

    for candidate in &candidates {
        let result = Command::new(candidate)
            .args(["--version"])
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .creation_flags(CREATE_NO_WINDOW)
            .output();

        if let Ok(output) = result {
            if output.status.success() {
                let version_str = String::from_utf8_lossy(&output.stdout);
                let version_stderr = String::from_utf8_lossy(&output.stderr);
                // Python --version outputs to stdout (3.x) or stderr (2.x)
                let version = if version_str.contains("Python") {
                    version_str.trim().to_string()
                } else {
                    version_stderr.trim().to_string()
                };
                if version.starts_with("Python 3") {
                    return Some(candidate.to_string());
                }
            }
        }
    }
    None
}

/// Get the Python version string for a given executable.
fn get_python_version(python: &str) -> String {
    Command::new(python)
        .args(["--version"])
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .creation_flags(CREATE_NO_WINDOW)
        .output()
        .ok()
        .map(|o| {
            let s = String::from_utf8_lossy(&o.stdout).trim().to_string();
            if s.contains("Python") {
                s
            } else {
                String::from_utf8_lossy(&o.stderr).trim().to_string()
            }
        })
        .unwrap_or_default()
}

/// Check if the `aria` package is installed and return its version.
fn check_aria_installed(python: &str) -> (bool, String) {
    let result = Command::new(python)
        .args(["-c", "import aria; print(aria.__version__)"])
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .creation_flags(CREATE_NO_WINDOW)
        .output();

    match result {
        Ok(output) if output.status.success() => {
            let version = String::from_utf8_lossy(&output.stdout).trim().to_string();
            (true, version)
        }
        _ => (false, String::new()),
    }
}

/// Windows-specific flag to prevent console windows from flashing.
#[cfg(target_os = "windows")]
const CREATE_NO_WINDOW: u32 = 0x08000000;

#[cfg(not(target_os = "windows"))]
const CREATE_NO_WINDOW: u32 = 0;

/// Extension trait to add creation_flags portably.
trait CommandExt {
    fn creation_flags(&mut self, flags: u32) -> &mut Self;
}

impl CommandExt for Command {
    #[cfg(target_os = "windows")]
    fn creation_flags(&mut self, flags: u32) -> &mut Self {
        use std::os::windows::process::CommandExt as WinCommandExt;
        WinCommandExt::creation_flags(self, flags);
        self
    }

    #[cfg(not(target_os = "windows"))]
    fn creation_flags(&mut self, _flags: u32) -> &mut Self {
        self
    }
}

// ── Commands ───────────────────────────────────────────────────────

#[tauri::command]
fn get_system_info() -> serde_json::Value {
    serde_json::json!({
        "os": std::env::consts::OS,
        "arch": std::env::consts::ARCH,
        "version": env!("CARGO_PKG_VERSION"),
    })
}

#[tauri::command]
fn get_app_version() -> String {
    env!("CARGO_PKG_VERSION").to_string()
}

#[tauri::command]
async fn get_backend_info() -> Result<BackendInfo, String> {
    // Run detection on a blocking thread to avoid blocking the async runtime
    tokio::task::spawn_blocking(|| {
        let python_path = find_python().unwrap_or_default();
        let python_found = !python_path.is_empty();
        let python_version = if python_found {
            get_python_version(&python_path)
        } else {
            String::new()
        };

        let (aria_installed, aria_version) = if python_found {
            check_aria_installed(&python_path)
        } else {
            (false, String::new())
        };

        // Check llama-cli + models by running a quick Python snippet
        let (llama_cli_found, models_found) = if python_found && aria_installed {
            let result = Command::new(&python_path)
                .args([
                    "-c",
                    "from aria.bitnet_subprocess import _get_default_backend; b = _get_default_backend(); print(b.is_available); print(len(b.list_available_models()))",
                ])
                .stdout(Stdio::piped())
                .stderr(Stdio::piped())
                .creation_flags(CREATE_NO_WINDOW)
                .output();

            match result {
                Ok(output) if output.status.success() => {
                    let stdout = String::from_utf8_lossy(&output.stdout);
                    let lines: Vec<&str> = stdout.trim().lines().collect();
                    let cli_found = lines.first().map(|s| *s == "True").unwrap_or(false);
                    let models: usize =
                        lines.get(1).and_then(|s| s.parse().ok()).unwrap_or(0);
                    (cli_found, models)
                }
                _ => (false, 0),
            }
        } else {
            (false, 0)
        };

        Ok(BackendInfo {
            python_found,
            python_path,
            python_version,
            aria_installed,
            aria_version,
            llama_cli_found,
            models_found,
        })
    })
    .await
    .map_err(|e| format!("Backend info task failed: {}", e))?
}

#[tauri::command]
async fn get_node_status(state: State<'_, AriaState>) -> Result<NodeStatus, String> {
    let running = *state.node_running.lock().map_err(|e| e.to_string())?;
    let api_base = state.api_base.lock().map_err(|e| e.to_string())?.clone();

    // Calculate uptime
    let uptime = state
        .start_time
        .lock()
        .map_err(|e| e.to_string())?
        .map(|t| t.elapsed().as_secs())
        .unwrap_or(0);

    if !running {
        return Ok(NodeStatus {
            running: false,
            peer_count: 0,
            uptime_seconds: 0,
            version: env!("CARGO_PKG_VERSION").to_string(),
            backend: "none".to_string(),
            model: None,
            llama_cli_available: false,
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
        Ok(resp) if resp.status().is_success() => {
            let body: serde_json::Value = resp.json().await.map_err(|e| e.to_string())?;
            Ok(NodeStatus {
                running: true,
                peer_count: 0,
                uptime_seconds: uptime,
                version: body["version"]
                    .as_str()
                    .unwrap_or(env!("CARGO_PKG_VERSION"))
                    .to_string(),
                backend: body["backend"]
                    .as_str()
                    .unwrap_or("unknown")
                    .to_string(),
                model: None,
                llama_cli_available: body["llama_cli_available"].as_bool().unwrap_or(false),
            })
        }
        _ => Ok(NodeStatus {
            running,
            peer_count: 0,
            uptime_seconds: uptime,
            version: env!("CARGO_PKG_VERSION").to_string(),
            backend: "offline".to_string(),
            model: None,
            llama_cli_available: false,
        }),
    }
}

#[tauri::command]
async fn start_node(state: State<'_, AriaState>) -> Result<StartNodeResult, String> {
    // Check if already running
    {
        let running = state.node_running.lock().map_err(|e| e.to_string())?;
        if *running {
            return Err("Node is already running".to_string());
        }
    }

    let port = *state.api_port.lock().map_err(|e| e.to_string())?;

    // Detect Python (on a blocking thread)
    let python_path = tokio::task::spawn_blocking(find_python)
        .await
        .map_err(|e| format!("Detection task failed: {}", e))?
        .ok_or_else(|| {
            "Python 3 not found in PATH. Install Python 3.10+ and ensure it is in your system PATH.".to_string()
        })?;

    // Verify aria package is installed
    let python_for_check = python_path.clone();
    let (aria_ok, _aria_ver) = tokio::task::spawn_blocking(move || {
        check_aria_installed(&python_for_check)
    })
    .await
    .map_err(|e| format!("Check task failed: {}", e))?;

    if !aria_ok {
        return Err(
            "ARIA package not found. Run: pip install -e \".[dev]\" from the aria-protocol directory."
                .to_string(),
        );
    }

    // Launch the Python API server as a subprocess
    let python_for_spawn = python_path.clone();
    let child = tokio::task::spawn_blocking(move || {
        Command::new(&python_for_spawn)
            .args(["-m", "aria.api"])
            .env("PYTHONUNBUFFERED", "1")
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .creation_flags(CREATE_NO_WINDOW)
            .spawn()
            .map_err(|e| format!("Failed to start ARIA backend: {}", e))
    })
    .await
    .map_err(|e| format!("Spawn task failed: {}", e))??;

    let pid = child.id();

    // Store the child process
    {
        let mut proc_lock = state.python_process.lock().map_err(|e| e.to_string())?;
        *proc_lock = Some(child);
    }

    // Poll /v1/status until the server is ready (max 30 seconds)
    let api_base = format!("http://127.0.0.1:{}", port);
    let client = reqwest::Client::new();
    let mut ready = false;
    let mut backend_name = "simulation".to_string();
    let mut models_count: usize = 0;

    for _attempt in 0..60 {
        tokio::time::sleep(std::time::Duration::from_millis(500)).await;

        // Check if the process died
        {
            let mut proc_lock = state.python_process.lock().map_err(|e| e.to_string())?;
            if let Some(ref mut child) = *proc_lock {
                match child.try_wait() {
                    Ok(Some(exit_status)) => {
                        *proc_lock = None;
                        return Err(format!(
                            "Python API server exited prematurely with status: {}",
                            exit_status
                        ));
                    }
                    Ok(None) => {} // Still running, good
                    Err(e) => {
                        return Err(format!("Failed to check process status: {}", e));
                    }
                }
            }
        }

        // Try to reach the status endpoint
        let resp = client
            .get(format!("{}/v1/status", api_base))
            .timeout(std::time::Duration::from_secs(2))
            .send()
            .await;

        if let Ok(r) = resp {
            if r.status().is_success() {
                if let Ok(body) = r.json::<serde_json::Value>().await {
                    backend_name = body["backend"]
                        .as_str()
                        .unwrap_or("simulation")
                        .to_string();
                    models_count = body["models_count"].as_u64().unwrap_or(0) as usize;
                }
                ready = true;
                break;
            }
        }
    }

    if !ready {
        // Kill the process if it never became ready
        kill_python_process(&state)?;
        return Err("ARIA API server failed to start within 30 seconds. Check that port 3000 is available.".to_string());
    }

    // Mark as running
    *state.node_running.lock().map_err(|e| e.to_string())? = true;
    *state.api_base.lock().map_err(|e| e.to_string())? = api_base;
    *state.start_time.lock().map_err(|e| e.to_string())? = Some(std::time::Instant::now());

    Ok(StartNodeResult {
        status: "running".to_string(),
        backend: backend_name,
        port,
        pid,
        models_available: models_count,
    })
}

#[tauri::command]
async fn stop_node(state: State<'_, AriaState>) -> Result<String, String> {
    let running = *state.node_running.lock().map_err(|e| e.to_string())?;
    if !running {
        return Err("Node is not running".to_string());
    }

    kill_python_process(&state)?;

    *state.node_running.lock().map_err(|e| e.to_string())? = false;
    *state.start_time.lock().map_err(|e| e.to_string())? = None;

    Ok("Node stopped".to_string())
}

/// Kill the Python subprocess, trying graceful first then forced.
fn kill_python_process(state: &State<'_, AriaState>) -> Result<(), String> {
    let mut proc_lock = state.python_process.lock().map_err(|e| e.to_string())?;
    if let Some(ref mut child) = *proc_lock {
        // On Windows, child.kill() sends TerminateProcess which is immediate.
        // On Unix, we could send SIGTERM first, but kill() is sufficient here.
        let _ = child.kill();
        // Wait for process to fully exit to avoid zombies
        let _ = child.wait();
    }
    *proc_lock = None;
    Ok(())
}

#[tauri::command]
async fn get_models(state: State<'_, AriaState>) -> Result<Vec<ModelInfo>, String> {
    let running = *state.node_running.lock().map_err(|e| e.to_string())?;

    // If the node is running, try the API first
    if running {
        let api_base = state.api_base.lock().map_err(|e| e.to_string())?.clone();
        let client = reqwest::Client::new();

        match client
            .get(format!("{}/v1/models", api_base))
            .timeout(std::time::Duration::from_secs(5))
            .send()
            .await
        {
            Ok(resp) if resp.status().is_success() => {
                if let Ok(body) = resp.json::<serde_json::Value>().await {
                    let models = body["data"]
                        .as_array()
                        .map(|arr| {
                            arr.iter()
                                .map(|m| {
                                    let id = m["id"].as_str().unwrap_or("unknown");
                                    let meta = &m["meta"];
                                    let display = meta["display_name"]
                                        .as_str()
                                        .unwrap_or(id);
                                    let params = meta["params"].as_str().unwrap_or("?");
                                    let ready = m["ready"].as_bool().unwrap_or(false);

                                    ModelInfo {
                                        name: display.to_string(),
                                        params: params.to_string(),
                                        size: format!("{} params", params),
                                        downloaded: ready,
                                        description: format!(
                                            "{} — {} quantization",
                                            id,
                                            meta["quantization"].as_str().unwrap_or("1.58-bit")
                                        ),
                                    }
                                })
                                .collect()
                        })
                        .unwrap_or_else(|| default_models());

                    return Ok(models);
                }
            }
            _ => {
                eprintln!("[get_models] API unavailable, falling back to filesystem check");
            }
        }
    }

    // Fallback: check filesystem for downloaded models
    let models_dir = dirs::home_dir()
        .unwrap_or_default()
        .join(".aria")
        .join("models");

    let model_defs = vec![
        ("BitNet-b1.58-large", "0.7B", "400 MB", "bitnet_b1_58-large/ggml-model-i2_s.gguf"),
        ("BitNet-b1.58-2B-4T", "2.4B", "1.3 GB", "BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf"),
        ("Llama3-8B-1.58", "8.0B", "4.2 GB", "Llama3-8B-1.58-100B-tokens/ggml-model-i2_s.gguf"),
    ];

    Ok(model_defs
        .iter()
        .map(|(name, params, size, path)| {
            let downloaded = models_dir.join(path).exists();
            ModelInfo {
                name: name.to_string(),
                params: params.to_string(),
                size: size.to_string(),
                downloaded,
                description: format!("{} — 1.58-bit quantization", name),
            }
        })
        .collect())
}

#[tauri::command]
async fn download_model(
    name: String,
    state: State<'_, AriaState>,
) -> Result<DownloadProgress, String> {
    let running = *state.node_running.lock().map_err(|e| e.to_string())?;
    if !running {
        return Err("Backend is not running. Start the node first.".to_string());
    }

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
async fn get_energy_stats(state: State<'_, AriaState>) -> Result<EnergyStats, String> {
    let running = *state.node_running.lock().map_err(|e| e.to_string())?;
    if !running {
        return Ok(EnergyStats {
            total_inferences: 0,
            total_tokens_generated: 0,
            total_energy_kwh: 0.0,
            avg_energy_per_token_mj: 0.0,
            session_uptime_seconds: 0.0,
            savings: EnergySavings {
                energy_saved_kwh: 0.0,
                reduction_percent: 0.0,
                co2_saved_kg: 0.0,
                cost_saved_usd: 0.0,
            },
        });
    }

    let api_base = state.api_base.lock().map_err(|e| e.to_string())?.clone();
    let client = reqwest::Client::new();

    match client
        .get(format!("{}/v1/energy", api_base))
        .timeout(std::time::Duration::from_secs(5))
        .send()
        .await
    {
        Ok(resp) if resp.status().is_success() => {
            let body: serde_json::Value = resp.json().await.map_err(|e| e.to_string())?;
            Ok(EnergyStats {
                total_inferences: body["total_inferences"].as_u64().unwrap_or(0),
                total_tokens_generated: body["total_tokens_generated"].as_u64().unwrap_or(0),
                total_energy_kwh: body["total_energy_kwh"].as_f64().unwrap_or(0.0),
                avg_energy_per_token_mj: body["avg_energy_per_token_mj"].as_f64().unwrap_or(0.0),
                session_uptime_seconds: body["session_uptime_seconds"].as_f64().unwrap_or(0.0),
                savings: EnergySavings {
                    energy_saved_kwh: body["savings"]["vs_gpu"]["energy_saved_kwh"]
                        .as_f64()
                        .unwrap_or(0.0),
                    reduction_percent: body["savings"]["vs_gpu"]["reduction_percent"]
                        .as_f64()
                        .unwrap_or(0.0),
                    co2_saved_kg: body["savings"]["co2_saved_kg"].as_f64().unwrap_or(0.0),
                    cost_saved_usd: body["savings"]["cost_saved_usd"]
                        .as_f64()
                        .unwrap_or(0.0),
                },
            })
        }
        _ => Ok(EnergyStats {
            total_inferences: 0,
            total_tokens_generated: 0,
            total_energy_kwh: 0.0,
            avg_energy_per_token_mj: 0.0,
            session_uptime_seconds: 0.0,
            savings: EnergySavings {
                energy_saved_kwh: 0.0,
                reduction_percent: 0.0,
                co2_saved_kg: 0.0,
                cost_saved_usd: 0.0,
            },
        }),
    }
}

#[tauri::command]
async fn send_inference(
    prompt: String,
    model: String,
    state: State<'_, AriaState>,
) -> Result<InferenceResponse, String> {
    let running = *state.node_running.lock().map_err(|e| e.to_string())?;
    if !running {
        return Err("Backend is not running. Start the node first to send inference requests.".to_string());
    }

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

// ── App Entry ─────────────────────────────────────────────────────

pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_notification::init())
        .plugin(tauri_plugin_updater::Builder::new().build())
        .plugin(tauri_plugin_deep_link::init())
        .manage(AriaState::default())
        .invoke_handler(tauri::generate_handler![
            get_system_info,
            get_app_version,
            get_backend_info,
            get_node_status,
            start_node,
            stop_node,
            get_models,
            download_model,
            get_energy_stats,
            send_inference,
        ])
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::Destroyed = event {
                // Kill the Python subprocess when the app window is destroyed
                let app = window.app_handle();
                if let Some(state) = app.try_state::<AriaState>() {
                    let mut proc_lock = state.python_process.lock().unwrap_or_else(|e: std::sync::PoisonError<_>| e.into_inner());
                    if let Some(ref mut child) = *proc_lock {
                        let _ = child.kill();
                        let _ = child.wait();
                    }
                    *proc_lock = None;
                }
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running ARIA Desktop");
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
