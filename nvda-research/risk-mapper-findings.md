# NVDA Research — Risk Mapper Findings
**Owner:** risk-mapper | **Task:** 60f722eb | **Confidence:** 0.85

> **BLOCKER NOTE:** exec and message tools are inaccessible from this session. Cannot run clawteam commands to send findings or update task status. Please relay findings to decision-editor and mark task completed manually.

---

## EXECUTION RISKS

### 1. Aggressive Architecture Cadence — Slip Risk
Annual new architectures (Blackwell → Blackwell Ultra → Rubin → Rubin Ultra) leaves zero margin for delay. Rubin (3nm N3P + chiplets + HBM4) is a multi-step process change simultaneously — yield hiccups anywhere cascade into 6+ month delays.
- **Mitigation:** Blackwell Ultra serves as hedge if Rubin slips; monitor TSMC N3P yield reports.

### 2. Chiplet / Advanced Packaging Yield
Rubin's dual-die design + CoWoS-L packaging hits reticle limits; yields on multi-die packages are structurally lower. This is a known technical risk flagged in semiconductor analysis, not hypothetical.
- **Mitigation:** Dual-die (vs 4-die) is the conservative choice but still unproven at scale.

### 3. HBM4 Supply & Validation
HBM4 (288 GB, 13 TB/s bandwidth) is new silicon; SK Hynix/Samsung still ramping mass production. HBM4 validation delays directly delay Rubin's production start.
- **Mitigation:** Secure HBM4 supply agreements; validation can parallelize with chip bring-up.

### 4. Power & Infrastructure Constraints
Gigawatt-scale data centers are real physical constraints; power grid capacity limits hyperscaler expansion in some regions.
- **Mitigation:** NVIDIA's NVL rack-scale efficiency narrative depends on customers having power; monitor data center land acquisitions.

---

## DEPENDENCY RISKS

### 5. TSMC Concentration (Critical)
NVIDIA depends 100% on TSMC for leading-edge silicon. TSMC 3nm allocation is already 36% AI by 2026 — crowding out other programs. Any TSMC disruption (earthquake, geopolitical, capacity reallocation) = direct NVIDIA supply shock.
- **Mitigation:** None internally; NVIDIA has locked in long-term TSMC capacity reservations (Jensen Huang personally visited TSMC to secure wafer supply).

### 6. HBM Single-Supplier Concentration
HBM4 supply is concentrated with SK Hynix (primary) and Samsung; Micron is behind. Memory suppliers can demand pricing/payment terms that pressure NVIDIA margins.
- **Mitigation:** Multi-source qualification in progress but not yet dual-sourced.

### 7. Hyperscaler CapEx Concentration
~85-90% of NVIDIA datacenter revenue comes from 4 customers: Microsoft, Alphabet, Meta, Amazon. Amazon FCF going negative in 2026 is a yellow flag; any one customer pulling back materially impacts NVIDIA.
- **Mitigation:** Distributed across 4 roughly equal customers; diversification into sovereign/enterprise AI is the strategic answer.

### 8. US-China Export Policy Cycles
China market access is subject to 15-25% revenue-sharing with US government for permitted chips (H200, H20). Policy reversibility is high given political volatility; Trump administration can tighten or loosen on any trade negotiation.
- **Mitigation:** China-specific H20 chip is a bridge product; strategic hedge is Rubin-era domestic Chinese competition (Huawei Ascend 910C) which erodes share regardless of policy.

---

## HIDDEN ASSUMPTIONS

### 9. AI Spending Curve Assumed Linear — May Plateau
Consensus assumes $1T data center spend by 2028; this assumes AI monetization delivers ROI, compute demand stays bandwidth-bound, and hyperscaler FCF holds.
- **Hidden risk:** If LLM scaling laws hit diminishing returns or enterprises fail to monetize AI, capEx cycles break earlier than expected.
- **Credibility: moderate.**

### 10. Rubin's 5x Cost-Per-Token Improvement Is Spec-Driven, Not Silicon-Proven
Promises of 10x lower cost-per-token and 50 PFLOPS FP4 are marketing architecture specs, not validated silicon benchmarks. Real-world performance depends on software optimization and memory bandwidth utilization.
- **Credibility: plausible but unproven until qualification silicon ships Q2 2026.**

### 11. Automotive <1% Revenue — Assumed Negligible Until 2027+
Q4 2025 automotive: $592M = ~1% of total. Robotaxi volume production starts 2027-2028.
- **Hidden risk:** If AV adoption is slower than expected (regulation, liability law, consumer trust), DRIVE stack investment yields little near-term ROI.
- **Credibility: reasonable given current mix.**

### 12. CUDA Moat Assumed Durable Through 2026+
Despite ROCm maturation, OpenAI Triton, and AMD's $5.8B R&D, switching costs remain 6-12 months + 10-20% performance regression.
- **Hidden risk:** The abstraction layer threat (Triton) is real and growing; by 2027-2028 the moat erodes more meaningfully.
- **Credibility: high for 2026, medium-term concern beyond.**

### 13. No Viable Unified Competitor in System Software in 2025-2026
AMD ROCm has 9 years of investment; still far fewer Stack Overflow questions, fewer optimized libraries. Google's TPUs, Amazon's Trainium are workload-specific and don't threaten general CUDA dominance.
- **Credibility: high through 2026.**

---

## FAILURE MODES

### 14. Supply Chain Black Swan → 12-18 Month Revenue Gap
TSMC earthquake or Taiwan geopolitical event → global AI chip shortage. Not within NVIDIA's control; industry-wide scenario.

### 15. Chinese Domestic Chip Erosion of Export-Restricted Market
Huawei Ascend 910C gaining traction in China; US restrictions inadvertently funding Chinese AI semiconductor independence. Once Chinese labs train on domestic silicon, switching back to NVIDIA becomes harder (Chinese-specific software stack network effects).

### 16. Hyperscaler Custom Silicon Migration
Google TPUs, Microsoft Maia, Amazon Trainium — each generation closes the gap with NVIDIA in specific workloads. If hyperscalers achieve 70%+ of their inference on custom silicon, NVIDIA's volume growth narrative breaks.

### 17. Data Center Networking Mix Shift Not Captured
Networking grew 97.7% in Q2 — suggests customers buying more InfiniBand/Ethernet from NVIDIA. Risk: if this is budget displacement from compute (buying networking instead of GPUs due to cluster bottleneck), revenue mix is less GPU-driven than assumed.

---

## WHAT SHOULD STOP OR DELAY EXECUTION

| Trigger | Threshold | Impact if Breached |
|---------|-----------|-------------------|
| TSMC N3P yields | <60% at mass production | Rubin slips to 2027; AMD MI400 competitive window opens |
| Amazon capex | >30% pullback H1 2026 | NVIDIA datacenter guidance misses; R&D cycle slows |
| H200/H20 license | Revocation | China revenue → zero; Huawei benefits |
| DRIVE Thor OEM integration | >6 month slip | Robotaxi 2027 timeline delayed; automotive stays <1% through 2028 |

---

## SUMMARY TABLE

| Category | Top Risk | Severity |
|----------|----------|----------|
| Execution | Rubin yield / packaging | HIGH |
| Dependency | TSMC single-source | HIGH |
| Dependency | Hyperscaler concentration | MEDIUM-HIGH |
| Assumption | AI spending curve linearity | MEDIUM |
| Assumption | Rubin's 5x performance specs | MEDIUM |
| Assumption | CUDA moat durability 2027+ | MEDIUM |
| Failure mode | China domestic chip erosion | HIGH (long fuse) |
| Failure mode | TSMC Taiwan geopolitical | HIGH (low probability) |
| Failure mode | Custom silicon migration | MEDIUM (long fuse) |

---

*Research based on: Perplexity web searches on NVDA architecture roadmap, Blackwell/Rubin specs, AI chip competition, US-China export controls, automotive/robotaxi market, CUDA moat analysis, datacenter capex trends, TSMC supply chain.*
