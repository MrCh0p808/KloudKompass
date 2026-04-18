# Integration Test Checklist
# ==========================
# Manual verification steps for Kloud Kompass TUI + Dashboard.
# Run each step with valid AWS credentials configured.

## Prerequisites
- [ ] `kloudkompass --help` runs without error
- [ ] `kloudkompass dashboard` launches the Textual UI
- [ ] AWS CLI installed: `aws --version`
- [ ] AWS credentials configured: `aws sts get-caller-identity`

## TUI Integration Tests

### Session
- [ ] First launch auto-loads provider/region/profile from `~/.kloudkompass/config.toml`
- [ ] Session defaults to AWS if no config found
- [ ] Settings menu: change provider → persists across menus

### Region Gate
- [ ] Enter Compute without region → prompted to select one
- [ ] Select a region → saved to session + config
- [ ] Re-enter Compute → region already set, no prompt
- [ ] Same behavior in Network, Storage, Database menus

### Compute Menu
- [ ] Option 1: Lists all instances with row numbers
- [ ] Type a row number → drill-down shows full instance detail
- [ ] Option 2: Lists only running instances
- [ ] Option 3: Lists only stopped instances
- [ ] Option 4: Enter instance ID → shows detail view
- [ ] Option 5: Enter tag → filters instances

### Network Menu
- [ ] Option 1: Lists VPCs with row numbers
- [ ] Type a row number → drill-down shows subnets in that VPC
- [ ] Option 2: Lists all subnets
- [ ] Option 3: Lists security groups with row numbers
- [ ] Type a row number → drill-down shows inbound/outbound rules
- [ ] Option 4: Enter SG ID → shows rules
- [ ] Option 5: Tag filter works for VPCs, Subnets, SGs

### Storage Menu
- [ ] Option 1: Lists S3 buckets
- [ ] Option 2: Lists EBS volumes with row numbers
- [ ] Type a row number → drill-down shows volume detail (encryption, tags)
- [ ] Option 3: Find unattached volumes → shows waste report

### Database Menu
- [ ] Option 1: Lists RDS instances
- [ ] Option 2: Lists DynamoDB tables
- [ ] Option 3: Finds publicly accessible DBs

## Dashboard Integration Tests
- [ ] `kloudkompass dashboard` launches without crash
- [ ] Sidebar shows all 8 nav buttons + Settings
- [ ] Click each sidebar button → view switches
- [ ] Press keys 1-8 → views switch correctly
- [ ] Press Q → quit confirmation modal appears
- [ ] Press E → export modal appears
- [ ] Press ? → help modal appears
- [ ] Settings modal → change provider/region → saves to config
