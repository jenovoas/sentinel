// SPDX-License-Identifier: GPL-2.0
//! ME-60OS Decision Tree (P2 eBPF embedded classifier)
//!
//! Provides data structures and evaluation matching `ebpf/decision_tree.h`.
//! Allows offline training/validation and synchronization with the `dt_model`
//! eBPF array map.

pub const DT_MAX_DEPTH: usize = 4;
pub const DT_MAX_NODES: usize = 32;
pub const DT_LEAF_INDEX: u16 = 0xFFFF;

pub const DT_FEAT_ENTROPY: u8 = 0;
pub const DT_FEAT_SEVERITY: u8 = 1;
pub const DT_FEAT_EVENT_TYPE: u8 = 2;
pub const DT_FEAT_PID_HASH: u8 = 3;

pub const DT_CLASS_BENIGN: u8 = 0;
pub const DT_CLASS_SUSPECT: u8 = 1;
pub const DT_CLASS_MALICIOUS: u8 = 2;

/// eBPF Decision Tree Node (Exact 16-byte C representation)
#[repr(C)]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct DtNode {
    pub threshold: u64,
    pub left: u16,
    pub right: u16,
    pub feature: u8,
    pub class: u8,
    pub _reserved: [u8; 2],
}

impl Default for DtNode {
    fn default() -> Self {
        Self {
            threshold: 0,
            left: 0,
            right: 0,
            feature: 0,
            class: DT_CLASS_BENIGN,
            _reserved: [0; 2],
        }
    }
}

impl DtNode {
    pub const fn new_leaf(class: u8) -> Self {
        Self {
            threshold: 0,
            left: DT_LEAF_INDEX,
            right: DT_LEAF_INDEX,
            feature: 0,
            class,
            _reserved: [0; 2],
        }
    }

    pub const fn new_branch(feature: u8, threshold: u64, left: u16, right: u16) -> Self {
        Self {
            threshold,
            left,
            right,
            feature,
            class: 0,
            _reserved: [0; 2],
        }
    }
}

/// Decision Tree Model containing up to 32 nodes
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct DtModel {
    pub nodes: [DtNode; DT_MAX_NODES],
}

impl Default for DtModel {
    fn default() -> Self {
        Self {
            nodes: [DtNode::default(); DT_MAX_NODES],
        }
    }
}

impl DtModel {
    /// Classifies an event using the exact same bounded logic as the kernel hook.
    pub fn classify(&self, entropy: u64, severity: u8, evt_type: u32, pid: u32) -> u8 {
        let mut idx = 0usize;

        for _depth in 0..=DT_MAX_DEPTH {
            if idx >= DT_MAX_NODES {
                return DT_CLASS_MALICIOUS;
            }

            let node = &self.nodes[idx];

            // Root uninitialized or leaf node
            if node.left == DT_LEAF_INDEX || (node.left == 0 && node.right == 0) {
                return node.class;
            }

            let val = match node.feature {
                DT_FEAT_ENTROPY => entropy,
                DT_FEAT_SEVERITY => severity as u64,
                DT_FEAT_EVENT_TYPE => evt_type as u64,
                _ => pid as u64,
            };

            let next_idx = if val <= node.threshold {
                node.left as usize
            } else {
                node.right as usize
            };

            if next_idx >= DT_MAX_NODES {
                return node.class;
            }

            idx = next_idx;
        }

        DT_CLASS_MALICIOUS
    }

    /// Serializes model nodes to raw bytes for bpftool map update
    pub fn to_bytes(&self) -> Vec<u8> {
        let mut bytes = Vec::with_capacity(DT_MAX_NODES * std::mem::size_of::<DtNode>());
        for node in &self.nodes {
            let slice = unsafe {
                std::slice::from_raw_parts(
                    node as *const DtNode as *const u8,
                    std::mem::size_of::<DtNode>(),
                )
            };
            bytes.extend_from_slice(slice);
        }
        bytes
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_dt_node_size_and_alignment() {
        assert_eq!(std::mem::size_of::<DtNode>(), 16);
        assert_eq!(std::mem::align_of::<DtNode>(), 8);
    }

    #[test]
    fn test_uninitialized_model_defaults_to_benign() {
        let model = DtModel::default();
        let class = model.classify(11_000_000, 2, 1, 1234);
        assert_eq!(class, DT_CLASS_BENIGN);
    }

    #[test]
    fn test_model_branch_evaluation() {
        let mut model = DtModel::default();
        // Node 0: If entropy <= 5_000_000 goto Node 1, else goto Node 2
        model.nodes[0] = DtNode::new_branch(DT_FEAT_ENTROPY, 5_000_000, 1, 2);
        // Node 1: Leaf -> Benign
        model.nodes[1] = DtNode::new_leaf(DT_CLASS_BENIGN);
        // Node 2: If severity <= 1 (LOW/MEDIUM) goto Node 3, else Node 4
        model.nodes[2] = DtNode::new_branch(DT_FEAT_SEVERITY, 1, 3, 4);
        // Node 3: Leaf -> Suspect
        model.nodes[3] = DtNode::new_leaf(DT_CLASS_SUSPECT);
        // Node 4: Leaf -> Malicious
        model.nodes[4] = DtNode::new_leaf(DT_CLASS_MALICIOUS);

        // Low entropy -> Benign
        assert_eq!(model.classify(2_000_000, 0, 3, 100), DT_CLASS_BENIGN);

        // High entropy, medium severity -> Suspect
        assert_eq!(model.classify(8_000_000, 1, 3, 100), DT_CLASS_SUSPECT);

        // High entropy, high severity -> Malicious
        assert_eq!(model.classify(8_000_000, 2, 1, 100), DT_CLASS_MALICIOUS);
    }

    #[test]
    fn test_serialization_roundtrip() {
        let mut model = DtModel::default();
        model.nodes[0] = DtNode::new_branch(DT_FEAT_ENTROPY, 5_000_000, 1, 2);
        model.nodes[1] = DtNode::new_leaf(DT_CLASS_BENIGN);
        model.nodes[2] = DtNode::new_leaf(DT_CLASS_MALICIOUS);

        let bytes = model.to_bytes();
        assert_eq!(bytes.len(), 32 * 16);

        // Verify first node
        let node0: DtNode = unsafe { std::ptr::read_unaligned(bytes.as_ptr() as *const DtNode) };
        assert_eq!(node0.threshold, 5_000_000);
        assert_eq!(node0.left, 1);
        assert_eq!(node0.right, 2);
    }
}
