use truthsync_core::ClaimExtractor;

fn main() {
    let extractor = ClaimExtractor::new();
    
    let text = "The unemployment rate is 3.5%. \
                I think the economy is doing well. \
                Tesla announced a new car. \
                This is probably good news. \
                The stock market was up 2% today.";
    
    let claims = extractor.extract(text);
    
    println!("Extracted {} claims:", claims.len());
    for claim in claims {
        println!("  - {}", claim);
    }
}
