//! Convenience macros for creating S60 values

/// Create an S60 value from components.
/// 
/// # Syntax
/// 
/// ```
/// use sentinel_base60::s60;
/// 
/// let val = s60![10; 30, 45];  // 10 degrees, 30 minutes, 45 seconds
/// let simple = s60![42];        // 42 degrees, 0 minutes
/// ```
#[macro_export]
macro_rules! s60 {
    // Pattern: s60![degrees; min, sec, third, ...]
    ($deg:expr; $($rest:expr),+ $(,)?) => {
        $crate::S60::new(&[$deg, $($rest),+])
    };
    
    // Pattern: s60![degrees] (just degrees, no minutes/seconds)
    ($deg:expr) => {
        $crate::S60::from_degrees($deg)
    };
}

#[cfg(test)]
mod tests {
    use crate::S60;

    #[test]
    fn test_s60_macro_full() {
        let val = s60![10; 30, 45];
        assert_eq!(val, S60::new(&[10, 30, 45]));
    }

    #[test]
    fn test_s60_macro_degrees_only() {
        let val = s60![42];
        assert_eq!(val, S60::from_degrees(42));
    }

    #[test]
    fn test_s60_macro_with_trailing_comma() {
        let val = s60![5; 15, 30,];
        assert_eq!(val, S60::new(&[5, 15, 30]));
    }
}
