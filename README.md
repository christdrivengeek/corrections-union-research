# 50-State Corrections Officer Compensation & Union Benefits Study

> **Objective:** Authoritative, evidence-based research project comparing state correctional officer compensation, pensions, step progression, and workplace protections across Union vs. Non-Union states. Built specifically for **New Staff Onboarding & Orientation Presentations**.

---

## 🛡️ Anti-Hallucination & Reference Verification Guarantee

Every state profile in this repository includes a dedicated **Check Reference & Verification Audit** section featuring:
1. **Direct Primary Sources:** Official State Civil Service Commissions, State Departments of Corrections (DOC), State Retirement Systems (PERS/ERS), and Union Collective Bargaining Agreements (CBAs).
2. **Verbatim Evidence Quotes:** Exact sentences extracted from public records justifying every salary figure, pension multiplier, and union representation claim.

---

## 📁 Repository Structure

```
corrections-union-research/
├── README.md               <-- Methodology and project overview
├── PROGRESS.md             <-- Live status of all 50 states
├── PRESENTATION_DATA.md    <-- Compiled slides & key talking points for orientation
├── master_data.csv         <-- Master 50-state comparison spreadsheet
├── agent.py                <-- Autonomous local researcher engine
└── states/                 <-- Deep-dive dossiers with verification quotes
    ├── MN_minnesota.md
    ├── TX_texas.md
    ├── CA_california.md
    └── ... (50 states)
```

---

## 🚀 Running the Autonomous Research Agent

The research agent runs on the local VPS CPU using **Ollama (`hermes3:8b`)** with zero cloud API costs.

### 1. Process Single State:
```bash
./venv/bin/python agent.py --state MN
```

### 2. Process 5-State Pilot Batch (MN, CA, TX, NY, FL):
```bash
./venv/bin/python agent.py --pilot
```

### 3. Run All 50 States Headless in Background (PM2):
```bash
pm2 start agent.py --name "corrections-researcher" --interpreter ./venv/bin/python -- --all
```
