# 05 Kloud Kompass User Flows

This document maps Kloud Kompass features to user experience journeys.

---

## 🏗️ 1. The Cloud Engineer (Daily Ops)
*Power user who needs quick terminal access to cloud resources.*

### Discovery & Setup
1. Engineer installs Kloud Kompass: `pip install -e .`
2. Runs `kloudkompass doctor` - system checks CLI installations and credentials.
3. If AWS CLI missing → Doctor shows install instructions. If credentials invalid → prompts `aws configure`.
4. Sets defaults: `kloudkompass config --set-default-provider aws --set-default-region us-east-1`

### Daily Cost Check
1. Launches `kloudkompass` → Main Menu renders with 10 options.
2. Selects "1. Cost Query" → CostWizardScreen launches.
3. Provider already defaulted to AWS → skips to date input.
4. Types `2025-02-01` to `2025-02-27` → selects "Service breakdown".
5. Sets threshold to `$1.00` → confirms query execution.
6. Results rendered as Rich table: S3 $12.34, EC2 $89.50, Lambda $2.10...
7. Option to "Run another query" or "Return to main menu".

### Resource Check (Phase 3+)
1. From Main Menu → "2. Compute" → lists EC2 instances.
2. Filters by state: "running" → sees 3 instances in us-east-1.
3. Selects instance `i-0abc123` → sees details (type, launch time, tags, IP).
4. Returns to menu → "3. Networking" → lists VPCs → drills into subnet details.

---

## 🔐 2. The Security Auditor
*Compliance officer scanning for misconfigurations.*

### Security Scan (Phase 5+)
1. Launches `kloudkompass` → selects "5. Security Audit".
2. Selects "Run all checks" → scans public S3 buckets, open SGs, IAM users without MFA.
3. Results grouped by severity: 🔴 CRITICAL (2) | 🟠 HIGH (5) | 🟡 MEDIUM (12).
4. Each finding shows: resource ID, description, recommendation.
5. Exports report: `kloudkompass security --export /reports/audit-2025-02.csv`

---

## 📊 3. The DevOps Lead (Dashboard)
*Wants a persistent overview without running individual commands.*

### Dashboard Usage
1. Runs `kloudkompass dashboard` → Textual app launches.
2. Sidebar: Cost | Inventory | Security | Doctor.
3. Cost view shows tabular data with keyboard shortcuts (E=Export, R=Refresh, ?=Help).
4. Switches between views using sidebar buttons or keyboard shortcuts (C, I, S, D).
5. Quits with Q → confirmation modal appears → confirms exit.

---

## 🛠️ 4. The CLI Power User
*Prefers flags over menus. Scripts Kloud Kompass into CI/CD pipelines.*

### Scripted Usage
```bash
# Daily cost report in CI/CD
kloudkompass cost -p aws -s $(date -d '-7 days' +%Y-%m-%d) -e $(date +%Y-%m-%d) \
  --breakdown service --threshold 1 --output json --export /tmp/weekly-cost.json

# Health check in monitoring script
kloudkompass check --provider aws || alert "AWS credentials expired"

# Doctor in pre-deploy validation
kloudkompass doctor || exit 1
```

---

## 🔄 5. The Multi-Cloud User (Phase 7-8)
*Manages resources across AWS, Azure, and GCP.*

### Cross-Cloud Cost Comparison
1. Runs `kloudkompass cost -p aws --start 2025-01-01 --end 2025-02-01`
2. Runs `kloudkompass cost -p azure --start 2025-01-01 --end 2025-02-01`
3. (Future) Runs `kloudkompass cost -p all` → unified cross-cloud cost table.
