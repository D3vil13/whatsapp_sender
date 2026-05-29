# Graph Report - bsp  (2026-05-28)

## Corpus Check
- 104 files · ~9,692 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 398 nodes · 649 edges · 82 communities (72 shown, 10 thin omitted)
- Extraction: 73% EXTRACTED · 27% INFERRED · 0% AMBIGUOUS · INFERRED: 173 edges (avg confidence: 0.56)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `577d778a`
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
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 32|Community 32]]

## God Nodes (most connected - your core abstractions)
1. `InternalServiceAuthentication` - 39 edges
2. `DisclaimerRequiredMixin` - 36 edges
3. `EvolutionAPIClient` - 29 edges
4. `JWTService` - 19 edges
5. `TokenPayload` - 17 edges
6. `ServiceClient` - 13 edges
7. `User` - 13 edges
8. `BulkPingAPI` - 11 edges
9. `SignupSerializer` - 11 edges
10. `str` - 10 edges

## Surprising Connections (you probably didn't know these)
- `EvolutionAPIClient` --uses--> `EvolutionAPIClient`  [INFERRED]
  services/instance/whatsapp/services.py → packages/bulkping-common/bulkping_common/evolution.py
- `WAInstance` --uses--> `EvolutionAPIClient`  [INFERRED]
  services/instance/whatsapp/services.py → packages/bulkping-common/bulkping_common/evolution.py
- `ServiceClient` --uses--> `ServiceClient`  [INFERRED]
  services/webhook/webhook_app/handlers.py → packages/bulkping-common/bulkping_common/http.py
- `DisclaimerRequiredMixin` --uses--> `TokenPayload`  [INFERRED]
  services/_base/core/authentication.py → packages/bulkping-common/bulkping_common/auth.py
- `InternalServiceAuthentication` --uses--> `TokenPayload`  [INFERRED]
  services/_base/core/authentication.py → packages/bulkping-common/bulkping_common/auth.py

## Communities (82 total, 10 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.09
Nodes (34): APIView, Campaign, _campaign_analytics(), CampaignAnalyticsView, CampaignExportView, CampaignListCreateView, CampaignStatsView, CampaignStopView (+26 more)

### Community 1 - "Community 1"
Cohesion: 0.10
Nodes (28): AbstractBaseUser, JWTService, TokenPayload, AuthenticatedUser, InternalServiceUser, JWTAuthentication, Lightweight user object from JWT — no cross-service User FK., JWTService (+20 more)

### Community 2 - "Community 2"
Cohesion: 0.11
Nodes (17): Campaign, CampaignStatus, MessageLog, MessageStatus, Meta, CampaignCreateSerializer, CampaignListSerializer, MessageLogSerializer (+9 more)

### Community 3 - "Community 3"
Cohesion: 0.11
Nodes (10): ContactCreateSerializer, ContactSerializer, GroupCreateSerializer, GroupMembersSerializer, GroupSerializer, Meta, normalize_phone(), parse_contacts_csv() (+2 more)

### Community 4 - "Community 4"
Cohesion: 0.19
Nodes (12): EvolutionAPIClient, extract_qr_base64(), Thin HTTP client for Evolution API v2.3.7., Create instance. Webhook is configured via Evolution env (WEBHOOK_GLOBAL_URL)., Extract QR image base64 from Evolution API create/connect responses., float, Any, str (+4 more)

### Community 5 - "Community 5"
Cohesion: 0.23
Nodes (11): ServiceClient, broadcast_hours_warning(), contacts_client(), fetch_group_contacts(), datetime, Any, str, UUID (+3 more)

### Community 6 - "Community 6"
Cohesion: 0.22
Nodes (7): Any, bool, str, str, bytes, BulkPingAPI, decode_qr()

### Community 7 - "Community 7"
Cohesion: 0.15
Nodes (13): str, WAInstance, EvolutionAPIClient, str, UUID, WAInstance, InstanceStatusSerializer, Meta (+5 more)

### Community 8 - "Community 8"
Cohesion: 0.14
Nodes (13): Anti-ban (PRD §4), API (via gateway), Architecture (microservices), BulkPing, code:bash (cp .env.example .env), code:bash (docker compose run --rm auth-service python manage.py makemi), code:block3 (├── apps/streamlit-ui/     # Testing UI), Data policy (+5 more)

### Community 9 - "Community 9"
Cohesion: 0.15
Nodes (7): AppConfig, CampaignsAppConfig, ChatbotAppConfig, ContactsAppConfig, UsersConfig, WebhookAppConfig, WhatsappConfig

### Community 10 - "Community 10"
Cohesion: 0.49
Nodes (9): Any, ServiceClient, str, _client(), handle_connection_update(), handle_messages_update(), handle_messages_upsert(), handle_qrcode_updated() (+1 more)

### Community 11 - "Community 11"
Cohesion: 0.20
Nodes (5): daily_cap_for_warmup_day(), int, HealthCheckView, IncrementWarmupView, ResetDailyCountsView

### Community 12 - "Community 12"
Cohesion: 0.53
Nodes (9): str, _cfg(), check_instance_health(), _headers(), increment_warmup_day(), _patch_log(), reset_daily_sent_counts(), send_broadcast_message() (+1 more)

### Community 13 - "Community 13"
Cohesion: 0.28
Nodes (3): ChatbotRuleCreateSerializer, ChatbotRuleSerializer, Meta

### Community 14 - "Community 14"
Cohesion: 0.28
Nodes (7): build_settings(), Factory for Django settings shared across BulkPing microservices., load_service_config(), ServiceConfig, _split_hosts(), str, str

### Community 15 - "Community 15"
Cohesion: 0.40
Nodes (4): ChatbotMatchLog, ChatbotRule, Meta, Metadata only — no message content stored.

### Community 17 - "Community 17"
Cohesion: 0.50
Nodes (3): Contact, ContactGroup, Meta

### Community 18 - "Community 18"
Cohesion: 0.50
Nodes (3): InstanceStatus, Meta, WAInstance

## Knowledge Gaps
- **44 isolated node(s):** `bool`, `int`, `Any`, `str`, `float` (+39 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `EvolutionAPIClient` connect `Community 4` to `Community 0`, `Community 11`, `Community 12`, `Community 7`?**
  _High betweenness centrality (0.131) - this node is a cross-community bridge._
- **Why does `InternalServiceAuthentication` connect `Community 0` to `Community 11`, `Community 1`, `Community 3`, `Community 4`?**
  _High betweenness centrality (0.095) - this node is a cross-community bridge._
- **Why does `DisclaimerRequiredMixin` connect `Community 0` to `Community 1`, `Community 3`, `Community 4`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Are the 36 inferred relationships involving `InternalServiceAuthentication` (e.g. with `Campaign` and `CampaignAnalyticsView`) actually correct?**
  _`InternalServiceAuthentication` has 36 INFERRED edges - model-reasoned connections that need verification._
- **Are the 33 inferred relationships involving `DisclaimerRequiredMixin` (e.g. with `Campaign` and `CampaignAnalyticsView`) actually correct?**
  _`DisclaimerRequiredMixin` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `EvolutionAPIClient` (e.g. with `EvolutionAPIClient` and `str`) actually correct?**
  _`EvolutionAPIClient` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `JWTService` (e.g. with `AuthenticatedUser` and `DisclaimerRequiredMixin`) actually correct?**
  _`JWTService` has 13 INFERRED edges - model-reasoned connections that need verification._