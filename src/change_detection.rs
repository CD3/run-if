use crate::utils;
use anyhow::{Context, Result};
use dpc_pariter::IteratorExt as _;
use itertools::Itertools;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::PathBuf;
use std::time::UNIX_EPOCH;

#[derive(Debug, Serialize, Deserialize)]
pub struct DependencyStatus {
    pub content_hash: String,
    pub mtime: u128,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CommandStatus {
    pub exit_code: Option<i32>,
    pub dependencies: HashMap<String, DependencyStatus>,
}

impl CommandStatus {
    pub fn new() -> CommandStatus {
        return CommandStatus {
            dependencies: HashMap::new(),
            exit_code: None,
        };
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct StatusCache {
    pub commands: HashMap<String, CommandStatus>,
}

impl StatusCache {
    pub fn new() -> StatusCache {
        return StatusCache {
            commands: HashMap::new(),
        };
    }
}

// we need a function to hash an array of bytes for using
// internally to hash the contents of files, and we need
// a function to hash a string that a user can use.
//
// we have tested several different hash functions and
// are currently using blake3 because it is the fastest
// in our tests/workspace/run-benchmarks.sh tests.
//
// we have commented out the hash functions that were
// used in the past.
//
// fn md_5_bytes(bytes: &[u8]) -> Vec<u8>{
//     // This is the slowest method. Hashing a directory
//     // with many large files is slower than Python even
//     // when we hash in parallel on a 4-core HT CPU
//     use md5::{Md5,Digest};
//     let hash = Md5::digest(bytes);
//     return hash.to_vec();
// }
// fn md5_openssl_bytes(bytes: &[u8]) -> Vec<u8> {
//     // This is as fast as Python since Python's
//     // hash lib links to openssl too. Adding parallelization makes
//     // it even faster. Release builds do not make it any faster though...
//     let hash = openssl::hash::hash(openssl::hash::MessageDigest::md5(), bytes).unwrap();
//     return hash.to_vec();
// }

fn blake3_bytes(bytes: &[u8]) -> Vec<u8> {
    // This is faster than Python, even with _debug_ builds.
    // Release build makes it faster and we can also add parallelization.
    // On a 4-core i5, processing a directory dependencies with 3
    // levels containing 13000 files, each 0.0001 GB, using blake3 finishes
    // in 420 ms while the python version takes 2.7 seconds.
    //
    // Using the OpenSSL md5 runs in 810 ms.
    let hash = blake3::hash(bytes).as_bytes().to_vec();
    return hash.to_vec();
}

////////////////////////////////////////////

fn hash_bytes(text: &[u8]) -> Vec<u8> {
    return blake3_bytes(text);
}

pub fn hash_string(text: &String) -> String {
    return hex::encode(hash_bytes(text.as_bytes()));
}

fn hash_file(file_path: &PathBuf) -> Result<String> {
    let data = std::fs::read(file_path)
        .with_context(|| format!("Could not read file '{}'", file_path.display()))?;
    return Ok(hex::encode(&hash_bytes(&data)));
}
fn hash_dir(dir_path: &PathBuf) -> Result<String> {
    // we can either get all of the files under the directory
    // at once and then hash each, or get only the files
    // in the top level and walk down into sub-directories.
    // getting them all up front will let us hash each in parallel.
    let fs = utils::FileSearch::new();
    let files = fs.get_all_files_under(&dir_path)?;
    let hashes = files
        .into_iter()
        .sorted()
        .parallel_map(|p| -> Result<String> { Ok(hash_path(&p)? + "|" + p.to_str().unwrap()) });

    // we want new directories to trigger a change, even if they are empty.
    // so we need to get the list of all directories that exist into the hash.
    // we'll just get a list of directories and tack it onto the end
    // of our hashes.
    let dirs = fs
        .get_all_dirs_under(&dir_path)?
        .into_iter()
        .sorted()
        .map(|p| -> Result<String> { Ok(p.to_string_lossy().into_owned()) });

    let joined_hash = hashes
        .chain(dirs)
        .reduce(|acc: Result<String>, e| Ok(acc? + "\n" + &e?))
        .unwrap_or(Ok(String::from("null")))?;
    let hash = hash_string(&joined_hash);
    return Ok(hash);
}

pub fn hash_path(path: &PathBuf) -> Result<String> {
    if path.is_file() {
        return hash_file(&path);
    }
    if path.is_dir() {
        return hash_dir(&path);
    }

    return Err(anyhow::anyhow!(
        "Cannot compute hash for '{}'. It is not a file or directory.",
        path.display()
    ));
}

// get modification time of file from UNIX epoc in microseconds.
pub fn get_mtime(path: &PathBuf) -> Result<u128> {
    Ok(std::fs::metadata(path)
        .with_context(|| format!("Could not get metadata of file '{}'", path.display()))?
        .modified()
        .with_context(|| format!("Could not get mtime of file '{}'", path.display()))?
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_micros())
}
