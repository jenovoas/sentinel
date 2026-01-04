use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug, Clone, PartialEq)]
pub enum BiologicalRole {
    Sovereign,    // jnovoas - TOTAL
    Monitored,    // Familia - WATCHED  
    Unauthorized, // * - BLOCKED
}

#[derive(Debug, Clone)]
pub enum Permission {
    All,
    Read,
    Watch,
    None
}

impl BiologicalRole {
    pub fn from_soul_hash(hash: &str) -> Self {
        // En producción, estos serían Hashes SHA3-512 reales derivados de la rPPG.
        // Para el MVP actual, mapeamos el user_id autenticado via challenge.
        match hash {
            "jnovoas" => Self::Sovereign,
            "madre" | "cristian" | "diego" | "madelin" | 
            "juan_francisco" | "vicente" | "florencia" | "tomas" => Self::Monitored,
            _ => Self::Unauthorized,
        }
    }
    
    pub fn has_permission(&self, perm: Permission) -> bool {
        match (self, perm) {
            (Self::Sovereign, _) => true,
            (Self::Monitored, Permission::Read) => true,
            (Self::Monitored, Permission::Watch) => true,
            (Self::Monitored, Permission::None) => false,
            (Self::Monitored, Permission::All) => false,
            (Self::Unauthorized, Permission::None) => true,
            (Self::Unauthorized, _) => false,
        }
    }

    pub fn label(&self) -> &str {
        match self {
            Self::Sovereign => "👑 SOVEREIGN (Full Access)",
            Self::Monitored => "👁️ MONITORED (Restricted Access)",
            Self::Unauthorized => "⛔ UNAUTHORIZED (Blocked)",
        }
    }
}
