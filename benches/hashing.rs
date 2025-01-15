use criterion::{black_box, criterion_group, criterion_main, Criterion};

use md5::{Digest, Md5};

fn md5(text: &String) -> String {
    let hash = Md5::digest(text);
    return format!("{:x}", hash);
}

fn md5_bytes(text: &Vec<u8>) -> Vec<u8> {
    let hash = openssl::hash::hash(openssl::hash::MessageDigest::md5(), text).unwrap();
    return hash.to_vec();
}

fn md5_benchmark(c: &mut Criterion) {
    c.bench_function("md5", |b| {
        b.iter(|| md5(black_box(&"Some text that is not very long...".to_string())))
    });
}

criterion_group!(benches, md5_benchmark);
criterion_main!(benches);
