use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn blake3(text: &String) -> String {
    let bytes = text.as_bytes();
    let bytes_hash = blake3::hash(bytes).as_bytes().to_vec();
    return hex::encode(bytes_hash);
}

//////////////

fn blake3_small_string_benchmark(c: &mut Criterion) {
    c.bench_function("blake3 small", |b| {
        b.iter(|| blake3(black_box(&"Some text that is not very long...".to_string())))
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
    blake3_small_string_benchmark,
);
criterion_group!(
    large_string_bencharmks,
    blake3_large_string_benchmark
);
criterion_main!(small_string_bencharmks, large_string_bencharmks);
