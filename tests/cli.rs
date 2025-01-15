use anyhow::Result;
use assert_cmd::prelude::*;
use assert_fs::prelude::*;
use predicates::prelude::*;
use std::process::Command;

#[test]
fn missing_target_only() -> Result<()> {
    let mut cmd = Command::cargo_bin("run-if")?;
    cmd.arg("-t").arg("missing").arg("echo").arg("RUNNING");

    cmd.assert()
        .success()
        .stdout(predicate::str::contains("RUNNING"));

    Ok(())
}

#[test]
fn single_file_dependency() -> Result<()> {
    let file = assert_fs::NamedTempFile::new("dep1.txt")?;
    file.write_str("hi")?;
    let mut cmd = Command::cargo_bin("run-if")?;
    cmd.arg("-d").arg(file.path()).arg("echo").arg("RUNNING");

    cmd.assert()
        .success()
        .stdout(predicate::str::contains("RUNNING"));
    cmd.assert()
        .success()
        .stdout(predicate::str::contains("RUNNING").not());
    file.write_str("bye")?;
    cmd.assert()
        .success()
        .stdout(predicate::str::contains("RUNNING"));
    cmd.assert()
        .success()
        .stdout(predicate::str::contains("RUNNING").not());

    Ok(())
}
