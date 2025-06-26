### Production Deployment — Step-by-Step Playbook

*(Adapt or adjust names/paths to match your own stack and tooling.)*

---

#### 0 . Preparation (T-1 day or earlier)

1. **Confirm release candidate**

   * Verify the commit/tag (e.g., `v2.3.0-prod`) is merged and has passed all CI pipelines.
   * Freeze further merges to the `main`/`release` branch until deployment completes.

2. **Schedule a window**

   * Agree on a start time with stakeholders; post it in the #deployments channel.
   * Block calendars for the **Deploy Lead**, **DBA on call**, and **QA**.

3. **Verify capacity for backups**

   * Check that backup storage (S3 bucket `prod-backups/`) has ≥ 15 % free space.

---

#### 1 . System Backup (T-0 h – 15 min)

1. **Application files & assets**

   ```bash
   ssh prod-app-01 "tar czf /backups/app_$(date +%F).tgz /var/www/app"
   ```
2. **Databases**

   ```bash
   # PostgreSQL example
   pg_dump -Fc --no-acl --no-owner \
           -h prod-db -U backup_user prod_db \
           > /backups/db_$(date +%F).dump
   ```
3. **Validate backups**

   * Ensure files are > 0 bytes.
   * Run `pg_restore --list` on the dump to confirm it’s readable.
4. **Replicate off-site**

   * Copy both archives to S3: `aws s3 cp /backups/*.tgz s3://prod-backups/2025-06-26/`.

> **Gate #1:** *Deploy Lead signs off once backup hashes match.*

---

#### 2 . Begin Deployment (T-0 h)

1. **Announce start**

   * Post: “Deploying v2.3.0 to production — starting now. Expect <10 min read-only period.”
2. **Enable maintenance / read-only mode**

   ```bash
   ansible-playbook enable_maintenance.yml --limit prod
   ```

---

#### 3 . Database Migration

1. **Dry-run migration in staging database one last time**

   ```bash
   rails db:migrate:status --environment=staging
   ```
2. **Execute migration on production**

   ```bash
   rails db:migrate --environment=production
   ```
3. **Verify**

   * Check schema version: `select version from schema_migrations order by version desc limit 1;`
   * Run critical read queries to ensure key tables still resolve.

> **Gate #2:** *DBA confirms migration succeeded and no blocking locks remain.*

---

#### 4 . Deploy Application Code

1. **Pull release artefacts to servers**

   ```bash
   ansible-playbook deploy_release.yml -e "git_ref=v2.3.0-prod" --limit prod
   ```
2. **Update configuration files**

   * Replace `.env` values via *Ansible/Vault* for any new vars (`PAYMENT_WEBHOOK_URL`, etc.).
   * Reload service: `systemctl restart app`.
3. **Rotate one instance at a time** to maintain uptime (blue-green or rolling strategy).

---

#### 5 . Post-Deploy Verification

1. **Automated smoke tests**

   ```bash
   pytest tests/smoke --base-url=https://prod.example.com
   ```
2. **Manual spot checks**

   * Log-in, place a test order, view dashboard.
   * Confirm background jobs processing via Sidekiq/Resque UI.
3. **Monitor telemetry for 15 min**

   * Dashboards: p95 latency, 5xx error rate, queue depth.
   * Logs: grep for “ERROR”, “Exception”, or migration warnings.

> **Gate #3:** *QA/On-call verifies KPIs are within normal bands.*

---

#### 6 . Rollback Plan (only if any Gate fails)

1. **Code rollback**

   ```bash
   ansible-playbook deploy_release.yml -e "git_ref=prev-stable-tag" --limit prod
   ```
2. **Database rollback**

   * If no destructive migrations: `rails db:rollback STEP=n`.
   * **Else:** restore dump

     ```bash
     dropdb prod_db_old && createdb prod_db
     pg_restore -j4 -d prod_db /backups/db_2025-06-26.dump
     ```
3. **Disable maintenance mode** and re-run smoke tests.
4. **Incident note** in #incidents with root cause draft.

---

#### 7 . Completion & Communication

1. **Disable maintenance mode**

   ```bash
   ansible-playbook disable_maintenance.yml --limit prod
   ```
2. **Notify team**

   * “✅ v2.3.0 successfully deployed; all checks green. See changelog below.”
3. **Update artefacts**

   * Merge `CHANGELOG.md` entry into `main`.
   * Update internal **Run-book** and **API docs** (Confluence page *Production Release v2.3.0*).
   * Create Jira ticket “Release notes v2.3.0” → *Done*.

---

#### 8 . Post-Deployment Review (Next working day)

1. **Retro 15 min** with Deploy Lead, Dev, Ops, QA: what went well / to improve.
2. **Close the release** in the Deployment Tracker spreadsheet.

---

### Summary Checklist

| Phase                        | Command / Action          | Owner   | Done (✔/✖) |
| ---------------------------- | ------------------------- | ------- | ---------- |
| Backups complete & validated | `tar`, `pg_dump`, S3 sync | Ops     |            |
| Maintenance mode ON          | playbook                  | Ops     |            |
| DB migrated                  | `rails db:migrate`        | DBA     |            |
| App code deployed            | playbook                  | DevOps  |            |
| Smoke tests pass             | CI + QA script            | QA      |            |
| Metrics healthy 15 min       | Grafana                   | On-call |            |
| Maintenance mode OFF         | playbook                  | Ops     |            |
| Team notified                | Slack                     | Lead    |            |
| Docs updated                 | Confluence / Git          | Dev     |            |

Stick to the gates: **no step continues until the previous gate is green**.
Following this playbook ensures backups exist, migrations run safely, rollback is defined, and every team member stays informed.
