use crate::utils;
use anyhow::{Context, Result};
use dpc_pariter::IteratorExt as _;
use itertools::Itertools;
use std::path::PathBuf;
use std::time::UNIX_EPOCH;

fn md5(text: &String) -> String {
    let bytes = text.as_bytes().to_vec();
    let bytes_hash = md5_bytes(&bytes);
    return hex::encode(bytes_hash);
    // let hash = Md5::digest(text);
    // return format!("{:x}", hash);
}

fn md5_bytes(text: &Vec<u8>) -> Vec<u8> {
    let hash = openssl::hash::hash(openssl::hash::MessageDigest::md5(), text).unwrap();
    return hash.to_vec();
}

fn hash_file(file_path: &PathBuf) -> Result<String> {
    let data = std::fs::read(file_path)
        .with_context(|| format!("Could not read file '{}'", file_path.display()))?;
    return Ok(hex::encode(&md5_bytes(&data)));
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

pub fn hash_string(text: &String) -> String {
    return md5(text);
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

#[cfg(test)]
mod tests {
    use super::*;
    use assert_fs::prelude::*;
    use predicates::prelude::*;

    #[test]
    fn test_file_hashing() {
        let tmpdir = tempfile::tempdir().unwrap();
        let curdir = std::env::current_dir().unwrap();
        std::env::set_current_dir(&tmpdir).unwrap();

        _ = std::fs::create_dir("dir");
        _ = std::fs::create_dir("dir2");
        _ = std::fs::write("dep1.txt", "HI");
        _ = std::fs::write("dir/dep2.txt", "HI");
        _ = std::fs::write("dir/dep3.txt", "HI");
        _ = std::fs::write("dir2/dep2.txt", "HI");
        _ = std::fs::write("dir2/dep3.txt", "HI");

        let mut hash;
        hash = hash_path(&PathBuf::from("dep1.txt")).unwrap();
        assert_eq!(hash, "bf8c144140b15befb8ce662632a7b76e");

        hash = hash_path(&PathBuf::from("dir/dep2.txt")).unwrap();
        assert_eq!(hash, "bf8c144140b15befb8ce662632a7b76e");

        hash = hash_path(&PathBuf::from("dir/dep3.txt")).unwrap();
        assert_eq!(hash, "bf8c144140b15befb8ce662632a7b76e");

        hash = hash_path(&PathBuf::from("dir")).unwrap();
        // this test seems like it might be brittle, it depends on the
        // order that the files get hashed in...
        // assert_eq!(hash, "56ddaf5e5ea0eea796430252073306a6");
        assert_eq!(hash, "30861a1b224cc7e5dfbc755ffd582178");

        hash = hash_path(&PathBuf::from("dir2")).unwrap();
        assert_ne!(hash, "30861a1b224cc7e5dfbc755ffd582178");

        // empty directories _do_ change the hash.
        _ = std::fs::create_dir("dir2/dir21");
        let hash2 = hash_path(&PathBuf::from("dir2")).unwrap();
        assert_ne!(hash, hash2);

        _ = std::fs::create_dir("dir2/dir21");
        _ = std::fs::write("dir2/dir21/dep1.txt", "HI");
        let hash2 = hash_path(&PathBuf::from("dir2")).unwrap();
        assert_ne!(hash, hash2);

        // hidden directories don't change the hash either,
        // even if they have files. they are ignored.
        _ = std::fs::create_dir("dir2/.hidden");
        _ = std::fs::write("dir2/.hidden/dep1.txt", "HI");
        let hash = hash_path(&PathBuf::from("dir2")).unwrap();
        assert_eq!(hash, hash2);
        std::env::set_current_dir(&curdir).unwrap();
    }

    #[test]
    fn string_hashing() {
        let text = "HI".to_string();
        let hash = hash_string(&text);

        assert_eq!(hash, "bf8c144140b15befb8ce662632a7b76e");
    }

    #[test]
    fn mtime() {
        let file = assert_fs::NamedTempFile::new("dep1.txt").unwrap();
        _ = file.write_str("hi");
        let time = get_mtime(&PathBuf::from(file.path().as_os_str())).unwrap();
        assert_eq!(true, predicate::gt(0).eval(&time));
    }
}
