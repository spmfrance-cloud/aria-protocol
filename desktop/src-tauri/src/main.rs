#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::Serialize;

#[derive(Serialize)]
struct SystemInfo {
    os: String,
    arch: String,
    version: String,
}

#[tauri::command]
fn get_system_info() -> SystemInfo {
    SystemInfo {
        os: std::env::consts::OS.to_string(),
        arch: std::env::consts::ARCH.to_string(),
        version: env!("CARGO_PKG_VERSION").to_string(),
    }
}

#[tauri::command]
fn get_app_version() -> String {
    env!("CARGO_PKG_VERSION").to_string()
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![get_system_info, get_app_version])
        .run(tauri::generate_context!())
        .expect("error while running ARIA Desktop");
}
