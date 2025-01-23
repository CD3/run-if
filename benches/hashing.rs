use criterion::{black_box, criterion_group, criterion_main, Criterion};

use md5::{Digest, Md5};

fn md5(text: &String) -> String {
    let hash = Md5::digest(text);
    return format!("{:x}", hash);
}
fn blake3(text: &String) -> String {
    let bytes = text.as_bytes();
    let bytes_hash = blake3::hash(bytes).as_bytes().to_vec();
    return hex::encode(bytes_hash);
}

fn md5_openssl(text: &String) -> String {
    let bytes = text.as_bytes().to_vec();
    let bytes_hash = md5_bytes(&bytes);
    return hex::encode(bytes_hash);
}

fn md5_bytes(text: &Vec<u8>) -> Vec<u8> {
    let hash = openssl::hash::hash(openssl::hash::MessageDigest::md5(), text).unwrap();
    return hash.to_vec();
}

//////////////

fn md5_small_string_benchmark(c: &mut Criterion) {
    c.bench_function("md5 small", |b| {
        b.iter(|| md5(black_box(&"Some text that is not very long...".to_string())))
    });
}

fn md5_openssl_small_string_benchmark(c: &mut Criterion) {
    c.bench_function("md5 (openssl) small", |b| {
        b.iter(|| md5_openssl(black_box(&"Some text that is not very long...".to_string())))
    });
}

fn blake3_small_string_benchmark(c: &mut Criterion) {
    c.bench_function("blake3 small", |b| {
        b.iter(|| blake3(black_box(&"Some text that is not very long...".to_string())))
    });
}

fn md5_large_string_benchmark(c: &mut Criterion) {
    c.bench_function("md5 large", |b| {
        b.iter(|| {
            md5(black_box(
                &std::iter::repeat("A").take(100000000).collect::<String>(),
            ))
        })
    });
}

fn md5_openssl_large_string_benchmark(c: &mut Criterion) {
    c.bench_function("md5 (openssl) large", |b| {
        b.iter(|| {
            md5_openssl(black_box(
                &std::iter::repeat("A").take(100000000).collect::<String>(),
            ))
        })
    });
}

fn blake3_large_string_benchmark(c: &mut Criterion) {
    c.bench_function("blake3 large", |b| {
        b.iter(|| {
            blake3(black_box(
                &std::iter::repeat("A").take(100000000).collect::<String>(),
            ))
        })
    });
}

criterion_group!(
    small_string_bencharmks,
    md5_small_string_benchmark,
    md5_openssl_small_string_benchmark,
    blake3_small_string_benchmark,
);
criterion_group!(
    large_string_bencharmks,
    md5_large_string_benchmark,
    md5_openssl_large_string_benchmark,
    blake3_large_string_benchmark
);
criterion_main!(small_string_bencharmks, large_string_bencharmks);
