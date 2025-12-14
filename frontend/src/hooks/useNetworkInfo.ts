/**
 * useNetworkInfo Hook
 * Detects WiFi network information from the browser using experimental APIs
 * 
 * Note: Limited browser support (mainly Chrome/Edge on desktop/Android)
 */

import { useEffect, useState } from "react";

export interface ClientNetworkInfo {
  wifi?: {
    ssid?: string;
    frequency?: number; // MHz
    signalStrength?: number; // dBm
    signal?: number; // Percentage 0-100
    connected: boolean;
  };
  type?: string; // "4g", "5g", "wifi", etc.
  effectiveType?: "slow-2g" | "2g" | "3g" | "4g";
  downlink?: number; // Mbps
  rtt?: number; // Round trip time in ms
  saveData?: boolean;
}

export const useNetworkInfo = () => {
  const [networkInfo, setNetworkInfo] = useState<ClientNetworkInfo>({
    wifi: { connected: false },
  });

  useEffect(() => {
    const detectNetworkInfo = async () => {
      try {
        // Modern Chromium: NetworkInformation API
        if ("connection" in navigator) {
          const connection = (navigator as any).connection;
          const info: ClientNetworkInfo = {
            type: connection.type,
            effectiveType: connection.effectiveType,
            downlink: connection.downlink,
            rtt: connection.rtt,
            saveData: connection.saveData,
            wifi: { connected: connection.type === "wifi" },
          };

          // Try to get WiFi details from experimental API
          if ("getNetworkList" in connection) {
            try {
              const networks = await (connection as any).getNetworkList();
              if (networks && networks.length > 0) {
                const wifiNet = networks.find(
                  (n: any) => n.type === "wifi"
                );
                if (wifiNet) {
                  info.wifi = {
                    ssid: wifiNet.name || "Connected WiFi",
                    frequency: wifiNet.frequency,
                    signalStrength: wifiNet.signalStrength, // dBm (-100 to 0)
                    // Convert dBm to percentage
                    signal: Math.max(
                      0,
                      Math.min(100, 2 * (wifiNet.signalStrength + 100))
                    ),
                    connected: true,
                  };
                }
              }
            } catch (e) {
              // getNetworkList not supported
            }
          }

          // Infer WiFi connection from type
          if (connection.type === "wifi") {
            info.wifi = {
              ...info.wifi,
              connected: true,
              ssid: info.wifi?.ssid || "Connected WiFi",
            };
          }

          setNetworkInfo(info);
        }

        // Fallback: Web Bluetooth/WiFi API (very limited)
        // Note: This requires user permission and is rarely available
      } catch (error) {
        console.debug("Network info detection failed:", error);
      }
    };

    detectNetworkInfo();

    // Listen for connection changes
    if ("connection" in navigator) {
      const connection = (navigator as any).connection;
      const handleChange = () => detectNetworkInfo();

      connection.addEventListener?.("change", handleChange);
      return () => {
        connection.removeEventListener?.("change", handleChange);
      };
    }
  }, []);

  return networkInfo;
};

/**
 * Enhanced WiFi detection with fallbacks:
 * 1. NetworkInformation API (modern browsers)
 * 2. getNetworkList (Chrome experimental)
 * 3. Connection type inference
 * 4. Device API probing (future)
 *
 * Security: All APIs require user permission or are read-only
 */
