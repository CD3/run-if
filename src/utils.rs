use anyhow:: Result;
use std::path::PathBuf;

#[derive(Debug, Clone)]
pub struct FileSearch {
    pub include_hidden: bool,
    pub include_dirs: bool,
    pub include_files: bool,
}

impl FileSearch {
    pub fn new() -> FileSearch {
        return FileSearch {
            include_hidden: false,
            include_dirs: true,
            include_files: true,
        };
    }

    pub fn get_all_paths_under(&self, path: &PathBuf) -> Result<Vec<PathBuf>> {
        if !path.is_dir() {
            return Ok(vec![]);
        }
        let mut all_paths: Vec<PathBuf> = Vec::new();

        let paths = std::fs::read_dir(path)?.map(|p| p.unwrap().path());
        for p in paths {
            let filename = p.file_name().unwrap().to_str().unwrap();
            if filename.starts_with(".") && !self.include_hidden {
                continue;
            }
            if p.is_dir() {
                all_paths.extend(self.get_all_paths_under(&p)?);
                if self.include_dirs {
                    all_paths.push(p);
                }
            } else {
                if self.include_files {
                    all_paths.push(p);
                }
            }
        }

        return Ok(all_paths);
    }
    pub fn get_all_files_under(&self, path: &PathBuf) -> Result<Vec<PathBuf>> {
        let mut clone = self.clone();
        clone.include_dirs = false;
        clone.include_files = true;
        return clone.get_all_paths_under(path);
    }
    pub fn get_all_dirs_under(&self, path: &PathBuf) -> Result<Vec<PathBuf>> {
        let mut clone = self.clone();
        clone.include_dirs = true;
        clone.include_files = false;
        return clone.get_all_paths_under(path);
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    use assert_fs::prelude::*;
    // use predicates::prelude::*;

    #[test]
    fn test_file_finding() -> Result<()> {
        let tmp_dir = assert_fs::TempDir::new().unwrap();
        let f1 = tmp_dir.child("dir1/dir21/file.txt");
        _ = f1.write_str("HI");
        let f2 = tmp_dir.child("dir1/dir22/file.txt");
        _ = f2.write_str("HI");
        let f3 = tmp_dir.child("dir1/dir21/dir31/file.txt");
        _ = f3.write_str("HI");

            let fs = FileSearch::new();
            let mut paths = fs.get_all_paths_under(&PathBuf::from(tmp_dir.child("dir1").path()))?;
            assert_eq!(paths.len(), 6);
            assert!(paths.contains(&PathBuf::from(tmp_dir.child("dir1/dir21/dir31/file.txt").path())));
            assert!(paths.contains(&PathBuf::from(tmp_dir.child("dir1/dir21/file.txt").path())));
            assert!(paths.contains(&PathBuf::from(tmp_dir.child("dir1/dir22/file.txt").path())));
            assert!(paths.contains(&PathBuf::from(tmp_dir.child("dir1/dir21/dir31").path())));
            assert!(paths.contains(&PathBuf::from(tmp_dir.child("dir1/dir21/").path())));
            assert!(paths.contains(&PathBuf::from(tmp_dir.child("dir1/dir22").path())));
            paths = fs.get_all_files_under(&PathBuf::from(tmp_dir.child("dir1").path()))?;
            assert_eq!(paths.len(), 3);
            assert!(paths.contains(&PathBuf::from(tmp_dir.child("dir1/dir21/dir31/file.txt").path())));
            assert!(paths.contains(&PathBuf::from(tmp_dir.child("dir1/dir21/file.txt").path())));
            assert!(paths.contains(&PathBuf::from(tmp_dir.child("dir1/dir22/file.txt").path())));

            paths = fs.get_all_dirs_under(&PathBuf::from(tmp_dir.child("dir1").path()))?;
            assert_eq!(paths.len(), 3);
            assert!(paths.contains(&PathBuf::from(tmp_dir.child("dir1/dir21/dir31").path())));
            assert!(paths.contains(&PathBuf::from(tmp_dir.child("dir1/dir21/").path())));
            assert!(paths.contains(&PathBuf::from(tmp_dir.child("dir1/dir22").path())));
        return Ok(());
    }
}
