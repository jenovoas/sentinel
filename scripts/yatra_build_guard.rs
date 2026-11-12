use proc_macro2::{Span, TokenTree};
use std::collections::BTreeSet;
use std::fs;
use std::path::{Path, PathBuf};
use syn::visit::Visit;
use syn::{ExprLit, ExprPath, Lit, Macro, PathSegment, TypePath};

/// Falla la compilación del workspace si un archivo Rust contiene floats o literales decimales.
pub fn enforce_workspace(crate_manifest_dir: &Path) {
    let workspace_root = find_workspace_root(crate_manifest_dir);
    let manifest_path = workspace_root.join("Cargo.toml");
    println!("cargo:rerun-if-changed={}", manifest_path.display());
    let guard_path = workspace_root.join("scripts/yatra_build_guard.rs");
    println!("cargo:rerun-if-changed={}", guard_path.display());

    let manifest_text = fs::read_to_string(&manifest_path).unwrap_or_else(|error| {
        panic!(
            "YATRA: no se pudo leer {}: {error}",
            manifest_path.display()
        )
    });
    let manifest: toml::Value = manifest_text.parse().unwrap_or_else(|error| {
        panic!(
            "YATRA: no se pudo analizar {}: {error}",
            manifest_path.display()
        )
    });
    let members = manifest
        .get("workspace")
        .and_then(|workspace| workspace.get("members"))
        .and_then(toml::Value::as_array)
        .unwrap_or_else(|| {
            panic!(
                "YATRA: {} no declara workspace.members",
                manifest_path.display()
            )
        });

    let mut package_roots = Vec::new();
    for member in members {
        let pattern = member
            .as_str()
            .unwrap_or_else(|| panic!("YATRA: miembro no textual en {}", manifest_path.display()));
        package_roots.extend(expand_member(&workspace_root, pattern));
    }

    let mut files = BTreeSet::new();
    let mut directories = BTreeSet::new();
    for package_root in package_roots {
        collect_rust_files(&package_root, &mut files, &mut directories);
    }

    for directory in directories {
        println!("cargo:rerun-if-changed={}", directory.display());
    }

    let mut violations = Vec::new();
    for file in files {
        println!("cargo:rerun-if-changed={}", file.display());
        let source = fs::read_to_string(&file)
            .unwrap_or_else(|error| panic!("YATRA: no se pudo leer {}: {error}", file.display()));
        let syntax = syn::parse_file(&source)
            .unwrap_or_else(|error| panic!("YATRA: Rust inválido en {}: {error}", file.display()));
        let mut scanner = FloatScanner {
            file: file.clone(),
            violations: Vec::new(),
        };
        scanner.visit_file(&syntax);
        violations.extend(scanner.violations);
    }

    if !violations.is_empty() {
        violations.sort();
        panic!(
            "YATRA: compilación bloqueada; usa SPA, S60 o SPAMath en vez de floats:\n{}",
            violations.join("\n")
        );
    }
}

fn find_workspace_root(start: &Path) -> PathBuf {
    start
        .ancestors()
        .find(|candidate| {
            let manifest = candidate.join("Cargo.toml");
            fs::read_to_string(manifest)
                .map(|text| text.contains("[workspace]"))
                .unwrap_or(false)
        })
        .unwrap_or_else(|| {
            panic!(
                "YATRA: no se encontró el workspace desde {}",
                start.display()
            )
        })
        .to_path_buf()
}

fn expand_member(root: &Path, pattern: &str) -> Vec<PathBuf> {
    if let Some((parent, child_pattern)) = pattern.split_once("/*") {
        let parent = root.join(parent);
        let entries = fs::read_dir(&parent).unwrap_or_else(|error| {
            panic!(
                "YATRA: no se pudo leer el patrón {}: {error}",
                parent.display()
            )
        });
        return entries
            .map(|entry| {
                entry.unwrap_or_else(|error| {
                    panic!("YATRA: no se pudo enumerar {}: {error}", parent.display())
                })
            })
            .map(|entry| entry.path())
            .filter(|path| path.is_dir())
            .filter(|path| {
                child_pattern.is_empty()
                    || path
                        .file_name()
                        .and_then(|name| name.to_str())
                        .is_some_and(|name| name == child_pattern.trim_start_matches('/'))
            })
            .filter(|path| path.join("Cargo.toml").is_file())
            .collect();
    }

    let package = root.join(pattern);
    if !package.join("Cargo.toml").is_file() {
        panic!(
            "YATRA: el miembro {} no existe o no tiene Cargo.toml",
            package.display()
        );
    }
    vec![package]
}

fn collect_rust_files(
    package: &Path,
    files: &mut BTreeSet<PathBuf>,
    directories: &mut BTreeSet<PathBuf>,
) {
    if !package.is_dir() {
        return;
    }
    let mut pending = vec![package.to_path_buf()];
    while let Some(directory) = pending.pop() {
        directories.insert(directory.clone());
        let entries = fs::read_dir(&directory).unwrap_or_else(|error| {
            panic!(
                "YATRA: no se pudo recorrer {}: {error}",
                directory.display()
            )
        });
        for entry in entries {
            let entry = entry.unwrap_or_else(|error| {
                panic!(
                    "YATRA: no se pudo enumerar {}: {error}",
                    directory.display()
                )
            });
            let path = entry.path();
            let file_type = entry.file_type().unwrap_or_else(|error| {
                panic!("YATRA: no se pudo inspeccionar {}: {error}", path.display())
            });
            if file_type.is_symlink() {
                continue;
            }
            if file_type.is_dir() {
                let name = path
                    .file_name()
                    .and_then(|name| name.to_str())
                    .unwrap_or_default();
                if name != "target" && name != ".git" && !name.starts_with('.') {
                    pending.push(path);
                }
            } else if path.extension().and_then(|extension| extension.to_str()) == Some("rs") {
                files.insert(path);
            }
        }
    }
}

struct FloatScanner {
    file: PathBuf,
    violations: Vec<String>,
}

impl FloatScanner {
    fn reject_type_segment(&mut self, segment: &PathSegment) {
        let name = segment.ident.to_string();
        if name == "f32" || name == "f64" {
            self.reject(segment.ident.span(), format!("tipo {name}"));
        }
    }

    fn scan_macro_tokens(&mut self, stream: proc_macro2::TokenStream) {
        for token in stream {
            match token {
                TokenTree::Ident(ident) if ident == "f32" || ident == "f64" => {
                    let name = ident.to_string();
                    self.reject(ident.span(), format!("tipo {name} dentro de macro"));
                }
                TokenTree::Literal(literal) => {
                    let text = literal.to_string();
                    if syn::parse_str::<syn::LitFloat>(&text).is_ok() {
                        self.reject(literal.span(), format!("literal decimal {text}"));
                    }
                }
                TokenTree::Group(group) => self.scan_macro_tokens(group.stream()),
                _ => {}
            }
        }
    }

    fn reject(&mut self, span: Span, kind: String) {
        let line = span.start().line;
        self.violations
            .push(format!("{}:{}: {kind}", self.file.display(), line.max(1)));
    }
}

impl<'ast> Visit<'ast> for FloatScanner {
    fn visit_expr_path(&mut self, node: &'ast ExprPath) {
        for segment in &node.path.segments {
            self.reject_type_segment(segment);
        }
        syn::visit::visit_expr_path(self, node);
    }

    fn visit_type_path(&mut self, node: &'ast TypePath) {
        for segment in &node.path.segments {
            self.reject_type_segment(segment);
        }
        syn::visit::visit_type_path(self, node);
    }

    fn visit_expr_lit(&mut self, node: &'ast ExprLit) {
        if let Lit::Float(literal) = &node.lit {
            self.reject(
                literal.span(),
                format!("literal decimal {}", literal.token()),
            );
        }
        syn::visit::visit_expr_lit(self, node);
    }

    fn visit_macro(&mut self, node: &'ast Macro) {
        self.scan_macro_tokens(node.tokens.clone());
        syn::visit::visit_macro(self, node);
    }
}
