use tauri::Manager;
use tauri_plugin_shell::ShellExt;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::thread;
use std::time::Duration;

fn wait_for_server(port: u16, timeout_secs: u64) -> bool {
    let url = format!("http://localhost:{}/", port);
    let start = std::time::Instant::now();
    let timeout = Duration::from_secs(timeout_secs);

    while start.elapsed() < timeout {
        if let Ok(response) = reqwest::blocking::get(&url) {
            if response.status().is_success() {
                return true;
            }
        }
        thread::sleep(Duration::from_millis(200));
    }
    false
}

fn shutdown_server(port: u16) {
    let url = format!("http://localhost:{}/shutdown", port);
    let client = reqwest::blocking::Client::new();
    let _ = client.post(&url).send();
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let port: u16 = 8080;
    let server_started = Arc::new(AtomicBool::new(false));
    let server_started_clone = server_started.clone();

    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .setup(move |app| {
            let shell = app.shell();

            // Spawn the Python sidecar
            let sidecar = match shell.sidecar("main") {
                Ok(s) => s,
                Err(e) => {
                    eprintln!("Failed to create sidecar command: {}", e);
                    return Err(e.into());
                }
            };

            match sidecar.spawn() {
                Ok((_rx, _child)) => {
                    server_started_clone.store(true, Ordering::SeqCst);
                    println!("Sidecar spawned successfully");
                }
                Err(e) => {
                    eprintln!("Failed to spawn sidecar: {}", e);
                    return Err(e.into());
                }
            }

            // Get the window handle
            let window = match app.get_webview_window("main") {
                Some(w) => w,
                None => {
                    eprintln!("Failed to get main window");
                    return Ok(());
                }
            };

            // Wait for server in background thread, then navigate
            thread::spawn(move || {
                println!("Waiting for server to start...");
                if wait_for_server(port, 30) {
                    println!("Server is ready, navigating to http://localhost:{}", port);
                    let _ = window.eval(&format!(
                        "window.location.href = 'http://localhost:{}'",
                        port
                    ));
                } else {
                    eprintln!("Server failed to start within timeout");
                }
            });

            Ok(())
        })
        .on_window_event(move |_window, event| {
            if let tauri::WindowEvent::CloseRequested { .. } = event {
                // Shutdown the Python server gracefully
                if server_started.load(Ordering::SeqCst) {
                    println!("Shutting down server...");
                    shutdown_server(port);
                }
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
