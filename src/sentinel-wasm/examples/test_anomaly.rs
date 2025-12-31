use sentinel_wasm::calculate_anomaly_score;

fn main() {
    let values = vec![10.0, 12.0, 11.0, 13.0, 100.0];
    
    // Calculate stats manually
    let mean = values.iter().sum::<f64>() / values.len() as f64;
    println!("Mean: {}", mean);
    
    let variance = values.iter()
        .map(|v| (v - mean).powi(2))
        .sum::<f64>() / values.len() as f64;
    let std_dev = variance.sqrt();
    println!("Std Dev: {}", std_dev);
    
    let last_value = values.last().unwrap();
    let z_score = (last_value - mean) / std_dev;
    println!("Z-score: {}", z_score);
    
    // Test different thresholds
    for threshold in [1.0, 1.5, 2.0, 2.5] {
        let score = calculate_anomaly_score(values.clone(), threshold);
        println!("Threshold {}: Score = {}", threshold, score);
    }
}
