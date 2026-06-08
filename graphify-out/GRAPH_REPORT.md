# Graph Report - bsp  (2026-06-08)

## Corpus Check
- 111 files · ~15,133 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 741 nodes · 1096 edges · 131 communities (115 shown, 16 thin omitted)
- Extraction: 84% EXTRACTED · 16% INFERRED · 0% AMBIGUOUS · INFERRED: 173 edges (avg confidence: 0.56)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `115d412d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 82|Community 82]]
- [[_COMMUNITY_Community 83|Community 83]]
- [[_COMMUNITY_Community 84|Community 84]]
- [[_COMMUNITY_Community 85|Community 85]]
- [[_COMMUNITY_Community 86|Community 86]]
- [[_COMMUNITY_Community 87|Community 87]]
- [[_COMMUNITY_Community 88|Community 88]]
- [[_COMMUNITY_Community 89|Community 89]]
- [[_COMMUNITY_Community 90|Community 90]]
- [[_COMMUNITY_Community 91|Community 91]]
- [[_COMMUNITY_Community 92|Community 92]]
- [[_COMMUNITY_Community 93|Community 93]]
- [[_COMMUNITY_Community 94|Community 94]]
- [[_COMMUNITY_Community 95|Community 95]]
- [[_COMMUNITY_Community 96|Community 96]]
- [[_COMMUNITY_Community 97|Community 97]]
- [[_COMMUNITY_Community 98|Community 98]]
- [[_COMMUNITY_Community 99|Community 99]]
- [[_COMMUNITY_Community 100|Community 100]]

## God Nodes (most connected - your core abstractions)
1. `InternalServiceAuthentication` - 40 edges
2. `DisclaimerRequiredMixin` - 37 edges
3. `EvolutionAPIClient` - 31 edges
4. `JWTService` - 20 edges
5. `TokenPayload` - 18 edges
6. `ServiceClient` - 14 edges
7. `User` - 14 edges
8. `time` - 13 edges
9. `BulkPingAPI` - 12 edges
10. `SignupSerializer` - 12 edges

## Surprising Connections (you probably didn't know these)
- `DisclaimerRequiredMixin` --uses--> `TokenPayload`  [INFERRED]
  services/_base/core/authentication.py → packages/bulkping-common/bulkping_common/auth.py
- `InternalServiceAuthentication` --uses--> `TokenPayload`  [INFERRED]
  services/_base/core/authentication.py → packages/bulkping-common/bulkping_common/auth.py
- `DisclaimerRequiredMixin` --uses--> `JWTService`  [INFERRED]
  services/_base/core/authentication.py → packages/bulkping-common/bulkping_common/auth.py
- `InternalServiceAuthentication` --uses--> `JWTService`  [INFERRED]
  services/_base/core/authentication.py → packages/bulkping-common/bulkping_common/auth.py
- `_fetch_qr()` --calls--> `extract_qr_base64()`  [INFERRED]
  services/instance/whatsapp/views.py → packages/bulkping-common/bulkping_common/evolution.py

## Import Cycles
- 1-file cycle: `services/campaigns/campaigns_app/services.py -> services/campaigns/campaigns_app/services.py`
- 1-file cycle: `services/campaigns/campaigns_app/tasks_client.py -> services/campaigns/campaigns_app/tasks_client.py`

## Communities (131 total, 16 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (42): APIView, Campaign, _campaign_analytics(), CampaignAnalyticsView, CampaignExportView, CampaignListCreateView, CampaignStatsView, CampaignStopView (+34 more)

### Community 1 - "Community 1"
Cohesion: 0.08
Nodes (30): AbstractBaseUser, BaseUserManager, JWTService, TokenPayload, AuthenticatedUser, InternalServiceUser, JWTAuthentication, Lightweight user object from JWT — no cross-service User FK. (+22 more)

### Community 2 - "Community 2"
Cohesion: 0.13
Nodes (17): Campaign, CampaignStatus, MessageLog, MessageStatus, Meta, CampaignCreateSerializer, CampaignListSerializer, MessageLogSerializer (+9 more)

### Community 3 - "Community 3"
Cohesion: 0.11
Nodes (12): Contact, ContactGroup, Meta, ContactCreateSerializer, ContactSerializer, GroupCreateSerializer, GroupMembersSerializer, GroupSerializer (+4 more)

### Community 4 - "Community 4"
Cohesion: 0.11
Nodes (21): EvolutionAPIClient, extract_qr_base64(), Thin HTTP client for Evolution API v2.3.7., Thin HTTP client for Evolution API v2.3.7., Create instance. Webhook is configured via Evolution env (WEBHOOK_GLOBAL_URL)., Create instance. Webhook is configured via Evolution env (WEBHOOK_GLOBAL_URL)., Extract QR image base64 from Evolution API create/connect responses., daily_cap_for_warmup_day() (+13 more)

### Community 5 - "Community 5"
Cohesion: 0.16
Nodes (20): ServiceClient, broadcast_hours_warning(), contacts_client(), fetch_group_contacts(), datetime, Any, str, UUID (+12 more)

### Community 6 - "Community 6"
Cohesion: 0.12
Nodes (7): Any, bool, str, str, bytes, BulkPingAPI, decode_qr()

### Community 7 - "Community 7"
Cohesion: 0.19
Nodes (7): str, WAInstance, InstanceStatus, Meta, WAInstance, InstanceStatusSerializer, Meta

### Community 8 - "Community 8"
Cohesion: 0.14
Nodes (13): Anti-ban (PRD §4), API (via gateway), Architecture (microservices), BulkPing, code:bash (cp .env.example .env), code:bash (docker compose run --rm auth-service python manage.py makemi), code:block3 (├── apps/streamlit-ui/     # Testing UI), Data policy (+5 more)

### Community 9 - "Community 9"
Cohesion: 0.11
Nodes (7): AppConfig, CampaignsAppConfig, ChatbotAppConfig, ContactsAppConfig, UsersConfig, WebhookAppConfig, WhatsappConfig

### Community 10 - "Community 10"
Cohesion: 0.04
Nodes (46): borderRadius, full, lg, md, sm, xl, 2xl, 3xl (+38 more)

### Community 11 - "Community 11"
Cohesion: 0.12
Nodes (16): ArtifactID, ArtifactName, ArtifactType, CreatedAt, Metadata, Author, Branch, Commit (+8 more)

### Community 12 - "Community 12"
Cohesion: 0.58
Nodes (9): str, _cfg(), check_instance_health(), _headers(), increment_warmup_day(), _patch_log(), reset_daily_sent_counts(), send_broadcast_message() (+1 more)

### Community 13 - "Community 13"
Cohesion: 0.15
Nodes (7): ChatbotMatchLog, ChatbotRule, Meta, Metadata only — no message content stored., ChatbotRuleCreateSerializer, ChatbotRuleSerializer, Meta

### Community 14 - "Community 14"
Cohesion: 0.29
Nodes (7): build_settings(), Factory for Django settings shared across BulkPing microservices., load_service_config(), ServiceConfig, _split_hosts(), str, str

### Community 15 - "Community 15"
Cohesion: 0.12
Nodes (16): ArtifactID, ArtifactName, ArtifactType, CreatedAt, Metadata, Author, Branch, Commit (+8 more)

### Community 16 - "Community 16"
Cohesion: 0.14
Nodes (13): Anti-ban (PRD §4), API (via gateway), Architecture (microservices), BulkPing, code:bash (cp .env.example .env), code:bash (docker compose run --rm auth-service python manage.py makemi), code:block3 (├── apps/streamlit-ui/     # Testing UI), Data policy (+5 more)

### Community 17 - "Community 17"
Cohesion: 0.14
Nodes (13): 1. Semgrep Results (SAST — Static Analysis), 2.1 Vulnerability Scan, 2.2 Secret Scanning, 2.3 Dependency Tree, 2.4 Raw Trivy Output (Vulnerability Scan), 2.5 Commands Used, 2. Trivy Results (Dependency & Secret Scanning), 3. Summary (+5 more)

### Community 18 - "Community 18"
Cohesion: 0.20
Nodes (10): danger, dangerHover, dangerText, primary, primaryHover, primaryText, secondary, secondaryHover (+2 more)

### Community 82 - "Community 82"
Cohesion: 0.20
Nodes (10): sidebar, bg, bgActive, bgHover, border, collapsedWidth, icon, text (+2 more)

### Community 83 - "Community 83"
Cohesion: 0.22
Nodes (8): engine_requested, errors, paths, scanned, profiling_results, results, skipped_rules, version

### Community 84 - "Community 84"
Cohesion: 0.32
Nodes (8): very_slow_stats, very_slow_stats, total_time, very_slow_files, very_slow_stats, scanning_time, count_ratio, time_ratio

### Community 85 - "Community 85"
Cohesion: 0.29
Nodes (7): delivered, failed, pending, read, replied, sent, chart

### Community 86 - "Community 86"
Cohesion: 0.29
Nodes (7): main, bg, cardBg, cardBorder, text, textMuted, textSecondary

### Community 87 - "Community 87"
Cohesion: 0.33
Nodes (7): per_file_time, total_time, very_slow_files, mean, std_dev, per_file_time, parsing_time

### Community 88 - "Community 88"
Cohesion: 0.29
Nodes (7): mean, std_dev, per_def_and_rule_time, total_time, very_slow_rules_on_defs, very_slow_stats, tainting_time

### Community 89 - "Community 89"
Cohesion: 0.29
Nodes (7): file_level_time, project_level_time, rules_matched_ratio, rules_selected_ratio, rules_with_file_prefilters_ratio, rules_with_project_prefilters_ratio, prefiltering

### Community 90 - "Community 90"
Cohesion: 0.29
Nodes (7): time, fixpoint_timeouts, max_memory_bytes, rules, rules_parse_time, targets, total_bytes

### Community 91 - "Community 91"
Cohesion: 0.33
Nodes (6): accent, accentHover, primary, primaryHover, colors, brand

### Community 92 - "Community 92"
Cohesion: 0.33
Nodes (6): input, bg, border, focusBorder, placeholder, text

### Community 93 - "Community 93"
Cohesion: 0.33
Nodes (6): messageStatus, delivered, failed, pending, read, sent

### Community 94 - "Community 94"
Cohesion: 0.33
Nodes (5): analytics, app, campaigns, connectPage, contacts

### Community 95 - "Community 95"
Cohesion: 0.33
Nodes (6): per_file_and_rule_time, total_time, very_slow_rules_on_files, mean, std_dev, matching_time

### Community 96 - "Community 96"
Cohesion: 0.40
Nodes (5): footer, bg, border, height, text

### Community 97 - "Community 97"
Cohesion: 0.40
Nodes (5): header, bg, border, height, text

### Community 98 - "Community 98"
Cohesion: 0.40
Nodes (5): status, connected, disconnected, pending, qrPending

### Community 99 - "Community 99"
Cohesion: 0.40
Nodes (5): config_time, core_time, ignores_time, total_time, profiling_times

## Knowledge Gaps
- **201 isolated node(s):** `name`, `version`, `primary`, `primaryHover`, `accent` (+196 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `EvolutionAPIClient` connect `Community 4` to `Community 0`, `Community 12`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Why does `InternalServiceAuthentication` connect `Community 0` to `Community 1`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Why does `DisclaimerRequiredMixin` connect `Community 0` to `Community 1`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Are the 36 inferred relationships involving `InternalServiceAuthentication` (e.g. with `Campaign` and `CampaignAnalyticsView`) actually correct?**
  _`InternalServiceAuthentication` has 36 INFERRED edges - model-reasoned connections that need verification._
- **Are the 33 inferred relationships involving `DisclaimerRequiredMixin` (e.g. with `Campaign` and `CampaignAnalyticsView`) actually correct?**
  _`DisclaimerRequiredMixin` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `EvolutionAPIClient` (e.g. with `EvolutionAPIClient` and `str`) actually correct?**
  _`EvolutionAPIClient` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `JWTService` (e.g. with `AuthenticatedUser` and `DisclaimerRequiredMixin`) actually correct?**
  _`JWTService` has 13 INFERRED edges - model-reasoned connections that need verification._