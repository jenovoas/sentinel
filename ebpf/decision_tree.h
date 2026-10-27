/* SPDX-License-Identifier: GPL-2.0 */
/*
 * ME-60OS Decision Tree Classifier for eBPF (Ring 0)
 *
 * Implements bounded decision-tree evaluation inside eBPF hooks.
 * Allows kernel-level classification (benign / suspect / malicious)
 * without waiting for userspace roundtrip.
 *
 * Max tree depth: 4 (maximum 32 nodes).
 * Features:
 *   0: DT_FEAT_ENTROPY    (S60 raw value, scaled by S60_SCALE_0)
 *   1: DT_FEAT_SEVERITY   (SEVERITY_LOW..CRITICAL)
 *   2: DT_FEAT_EVENT_TYPE (EVENT_*)
 *   3: DT_FEAT_PID_HASH   (pid)
 *
 * Classes:
 *   0: DT_CLASS_BENIGN
 *   1: DT_CLASS_SUSPECT
 *   2: DT_CLASS_MALICIOUS
 *
 * Copyright (c) 2026 ME-60OS Development Team
 */

#ifndef __DECISION_TREE_H__
#define __DECISION_TREE_H__

#define DT_MAX_DEPTH          4
#define DT_MAX_NODES          32
#define DT_LEAF_INDEX         0xFFFF

#define DT_FEAT_ENTROPY       0
#define DT_FEAT_SEVERITY      1
#define DT_FEAT_EVENT_TYPE    2
#define DT_FEAT_PID_HASH      3

#define DT_CLASS_BENIGN       0
#define DT_CLASS_SUSPECT      1
#define DT_CLASS_MALICIOUS    2

struct dt_node {
    __u64 threshold;   /* Valor umbral (S60 raw o valor escalar) */
    __u16 left;        /* Índice hijo izq (DT_LEAF_INDEX = leaf) */
    __u16 right;       /* Índice hijo der (DT_LEAF_INDEX = leaf) */
    __u8  feature;     /* DT_FEAT_* */
    __u8  class;       /* DT_CLASS_* (relevante cuando es leaf) */
    __u8  _reserved[2];/* Alineación a 16 bytes exactos */
};

#ifndef __BPF__
_Static_assert(sizeof(struct dt_node) == 16,
    "dt_node debe ser exactamente 16 bytes");
#endif

#endif /* __DECISION_TREE_H__ */
