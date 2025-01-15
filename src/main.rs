use anyhow::{Context, Result};
use clap::Parser;
use log::{debug, info, warn};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::PathBuf;
// use crate::change_detection;

mod change_detection;
mod utils;

#[derive(Parser)]
#[command(version)]
/// Conditionally run a command, similar to make and checkexec.
///
/// run-if runs a given command based on the status of dependencies, targets, and sentinals.
///
/// A _dependency_ must be a file or directory. The run-if will run the command if any dependency
/// has changed since the last time it was ran. Changes are not based on modification time, they
/// are based on a hash of the contents.
///
/// A _target_ is a file or directory that will be checked to exisit.
/// If a target **does not** exist, the command will be ran even if the dependencies have not changed.
/// Typically this would be a file or directory that the command will create, but it does not have
/// to be. Specifying a dummy name for a target (i.e. a name that is not a file or directory
/// created by the command) will cause the command to run every time (unless some other process
/// creates a file with the same name).
///
/// A _sentinal_ is a file or directory that will be checked to exists.
/// If a sential **does** exist, the command will be ran even if the dependencies have not changed.
/// This can be used to cause a command to run only if some file that woudl be produced by another
/// processes is present. Can be useful for running command that do some cleanup.
struct Cli {
    /// Specify a dependency. Must be a file or directly. Can be given multiple times.
    #[arg(short, long)]
    dependency: Vec<PathBuf>,
    /// Specify a target. Can be given multiple times.
    #[arg(short, long)]
    target: Vec<PathBuf>,
    /// Specify a sentinal. Can be given multiple times.
    #[arg(short, long)]
    sentinal: Vec<PathBuf>,
    /// Specify the database file to use.
    #[arg(long, default_value = ".run-if.json")]
    database: PathBuf,
    /// Run command no matter what. Result of running command will be saved to database.
    #[arg(short, long)]
    force: bool,
    /// Run command if last run did not exist with status 0.
    #[arg(short = 'u', long)]
    try_until_success: bool,

    command: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize)]
struct DependencyStatus {
    content_hash: String,
    mtime: u128,
}
#[derive(Debug, Serialize, Deserialize)]
struct CommandStatus {
    exit_code: Option<i32>,
    dependencies: HashMap<String, DependencyStatus>,
}
#[derive(Debug, Serialize, Deserialize)]
struct Cache {
    commands: HashMap<String, CommandStatus>,
}

fn main() -> Result<()> {
    env_logger::init();
    let cli = Cli::parse();
    if cli.command.len() == 0 {
        println!("No command given.");
        std::process::exit(0);
    }

    let mut cache = Cache {
        commands: HashMap::new(),
    };
    // Check if cache file exists, if so, load it.
    if cli.database.exists() {
        // todo: lock the file
        info!(
            "Found database file '{}', attempting to read",
            cli.database.display()
        );
        let data = std::fs::read_to_string(&cli.database)
            .with_context(|| format!("Could not read file '{}'", cli.database.display()))?;
        if let Ok(ret) = serde_json::from_str(&data[..]) {
            cache = ret
        } else {
            warn!(
                "Database file '{}' seems corrupt. Disregarding",
                cli.database.display()
            );
        }
    }

    let cmd_hash = change_detection::hash_string(&cli.command.join(" "));
    // We assume that the command should not be run
    // because it is _obviously_ expensive
    // (if it wasn't you would not need us).
    let mut run_command = false;

    if !cache.commands.contains_key(&cmd_hash) {
        run_command = true;
        cache.commands.insert(
            cmd_hash.clone(),
            CommandStatus {
                dependencies: HashMap::new(),
                exit_code: None,
            },
        );
    }
    let cmd_status = cache.commands.get_mut(&cmd_hash).unwrap();

    // check to see if any dependencies have changed
    for dep in cli.dependency.iter() {
        debug!("Checking if dependency '{}' has changed...", dep.display());
        if !dep.exists() {
            eprintln!("Error: dependency '{}' does not exist.", dep.display());
            std::process::exit(1);
        }
        let dep_name = dep.to_string_lossy().into_owned();
        let dep_mtime = change_detection::get_mtime(&dep)?;
        // we don't want to consider mtime.
        if !cmd_status.dependencies.contains_key(&dep_name) {
            // is dependency in the cache?
            debug!(
                "  '{}' not in cache. Will execute command and update the cache.",
                dep.display(),
            );

            run_command = true;
            let dep_hash = change_detection::hash_path(dep)?;
            cmd_status.dependencies.insert(
                dep_name.clone(),
                DependencyStatus {
                    content_hash: dep_hash,
                    mtime: dep_mtime,
                },
            );
        } else {
            debug!("  Found '{}' in cache.", dep.display(),);
            debug!(
                "  Checking if '{}' has been modified...",
                dep.display(),
            );
            // check if file has been "modified" (saved) since last time
            if cmd_status.dependencies.get(&dep_name).unwrap().mtime != dep_mtime {
                debug!(
                    "  '{}' has been modified: mtime: {}, cached mtime: {}",
                    dep.display(),
                    dep_mtime,
                    cmd_status.dependencies.get(&dep_name).unwrap().mtime
                );
                cmd_status.dependencies.get_mut(&dep_name).unwrap().mtime = dep_mtime;
                debug!(
                    "  Checking if contents of '{}' have changed...",
                    dep.display(),
                );
                // check if file has _actually_ been modified
                let dep_hash = change_detection::hash_path(dep)?;
                if cmd_status.dependencies.get(&dep_name).unwrap().content_hash != dep_hash {
                    debug!(
                        "  '{}' contents have changed. Command will be executed.",
                        dep.display(),
                    );
                    run_command = true;
                    cmd_status
                        .dependencies
                        .get_mut(&dep_name)
                        .unwrap()
                        .content_hash = dep_hash;
                } else {
                    debug!(
                        "  '{}' contents have NOT changed.",
                        dep.display(),
                    );
                }
            }
        }
    }

    // check to see if any targets are missing
    for tar in cli.target.iter() {
        if !tar.exists() {
            debug!(
                "target '{}' does not exist. Command will be executed.",
                tar.display()
            );
            run_command = true;
            break;
        }
    }
    // check to see if any sentinals exist
    for sen in cli.sentinal.iter() {
        debug!("sentinal '{}' exists. Command will be executed.", sen.display());
        if sen.exists() {
            run_command = true;
            break;
        }
    }

    if cli.force {
        run_command = true
    }

    if !run_command {
        if cli.try_until_success {
            if cmd_status.exit_code.unwrap() != 0 {
                debug!("Command returned non-zero exit code last time and --try-until-success was given. Command will be executed.");
                run_command = true;
            }
        }
    }

    if run_command {
        debug!("Executing command `{}`.", &cli.command[0]);
        let status = std::process::Command::new(&cli.command[0])
            .args(&cli.command[1..])
            .status()
            .expect(&format!("Error executing the command. Command parts: {:?}", cli.command));
        cmd_status.exit_code = status.code();
    }
    // write the cache file even if we didn't run the command
    // because some things like file modification time, command exist status, etc, may have
    // changed.
    // TODO: lock file
    let fout = std::fs::File::create(&cli.database).with_context(|| {
        format!(
            "Could not open database file '{}' for writing.",
            cli.database.display()
        )
    })?;
    serde_json::to_writer(fout, &cache)?;

    return Ok(());
}
