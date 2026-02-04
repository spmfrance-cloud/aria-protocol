#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod lib;

use lib::AriaState;

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_notification::init())
        .plugin(tauri_plugin_updater::Builder::new().build())
        .plugin(tauri_plugin_deep_link::init())
        .manage(AriaState::default())
        .invoke_handler(tauri::generate_handler![
            lib::get_system_info,
            lib::get_app_version,
            lib::get_node_status,
            lib::start_node,
            lib::stop_node,
            lib::get_models,
            lib::download_model,
            lib::send_inference,
        ])
        .run(tauri::generate_context!())
        .expect("error while running ARIA Desktop");
}
