#![no_std]

use aya_ebpf::{
    bindings::xdp_action,
    macros::{map, xdp},
    maps::HashMap,
    programs::XdpContext,
};
use aya_log_ebpf::info;
use core::mem;

// Define the Blacklist Map: source IP (u32) -> u8 (dummy value, existence implies block)
#[map]
static BLACKLIST: HashMap<u32, u8> = HashMap::with_max_entries(1024, 0);

const ETH_P_IP: u16 = 0x0800;
const ETH_HDR_LEN: usize = 14;

#[xdp]
pub fn xdp_firewall(ctx: XdpContext) -> u32 {
    match try_xdp_firewall(ctx) {
        Ok(ret) => ret,
        Err(_) => xdp_action::XDP_ABORTED,
    }
}

#[inline(always)]
fn try_xdp_firewall(ctx: XdpContext) -> Result<u32, ()> {
    let data_start = ctx.data();
    let data_end = ctx.data_end();

    // 1. Check Ethernet Header
    if data_start + ETH_HDR_LEN > data_end {
        return Ok(xdp_action::XDP_PASS);
    }

    let eth_proto = unsafe {
        let eth_hdr = data_start as *const EthHdr;
        u16::from_be((*eth_hdr).h_proto)
    };

    if eth_proto != ETH_P_IP {
        return Ok(xdp_action::XDP_PASS);
    }

    // 2. Check IPv4 Header
    let ip_hdr_start = data_start + ETH_HDR_LEN;
    let ip_hdr_len = mem::size_of::<IpHdr>();

    if ip_hdr_start + ip_hdr_len > data_end {
        return Ok(xdp_action::XDP_PASS);
    }

    let src_ip = unsafe {
        let ip_hdr = ip_hdr_start as *const IpHdr;
        u32::from_be((*ip_hdr).saddr)
    };

    // 3. Consult Blacklist
    if unsafe { BLACKLIST.get(&src_ip) }.is_some() {
        info!(&ctx, "DROPPED packet from blocked IP: {:x}", src_ip);
        return Ok(xdp_action::XDP_DROP);
    }

    Ok(xdp_action::XDP_PASS)
}

// Minimal Struct Definitions for Parsing
#[repr(C)]
struct EthHdr {
    h_dest: [u8; 6],
    h_source: [u8; 6],
    h_proto: u16,
}

#[repr(C)]
struct IpHdr {
    ihl_v: u8,
    tos: u8,
    tot_len: u16,
    id: u16,
    frag_off: u16,
    ttl: u8,
    protocol: u8,
    check: u16,
    saddr: u32,
    daddr: u32,
}
