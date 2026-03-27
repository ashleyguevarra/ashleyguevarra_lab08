# Trace — diagrammes Mermaid (rapport Lab 8)

Sources des figures exportées en PNG pour `ashley_guevarra_lab-report.md`. Fichiers `.mmd` canoniques : `docs/mermaid-source/`.

---

## Q1 — Lab 6 vs lab 8 (`q1-lab6-lab8.mmd` → `Images/Lab8_Q1_flowchart_lab6_lab8.png`)

```mermaid
flowchart LR
  subgraph lab6 ["Labo 6 - orchestré"]
    O[Orchestrateur] -->|HTTP sync| A[Service A]
    O -->|HTTP sync| B[Service B]
  end
  subgraph lab8 ["Labo 8 - chorégraphié"]
    SM[Store Manager] -->|publish| K[(Kafka)]
    K -->|OrderEventConsumer| H[Handlers SM]
    H -->|publish| K
    PA[Payments API lab05] -->|consume + publish| K
  end
```

---

## Q3 — Outbox (`q3-outbox.mmd` → `Images/Lab8_Q3_Outbox_sequence.png`)

```mermaid
sequenceDiagram
  participant App as Application
  participant DB as Base de données
  participant Outbox as Table Outbox
  participant Ext as API externe / broker
  App->>DB: Transaction : métier + ligne Outbox
  App->>DB: commit
  App->>Outbox: OutboxProcessor / worker
  Outbox->>Ext: HTTP ou publish (après persistance)
```

---

## Q4 — Fenêtre de crash (`q4-crash.mmd` → `Images/Lab8_Q4_risk_window.png`)

```mermaid
stateDiagram-v2
  [*] --> StockDecreased
  StockDecreased --> OutboxCommitted : commit Outbox OK
  StockDecreased --> Crash : kill -9 avant commit
  Crash --> Incomplet : pas de ligne Outbox
  OutboxCommitted --> OutboxProcessor
```

---

## Régénérer les PNG

```bash
cd ashleyguevarra_lab08
npx @mermaid-js/mermaid-cli -i docs/mermaid-source/q1-lab6-lab8.mmd -o Images/Lab8_Q1_flowchart_lab6_lab8.png -b white
npx @mermaid-js/mermaid-cli -i docs/mermaid-source/q3-outbox.mmd -o Images/Lab8_Q3_Outbox_sequence.png -b white
npx @mermaid-js/mermaid-cli -i docs/mermaid-source/q4-crash.mmd -o Images/Lab8_Q4_risk_window.png -b white
```
