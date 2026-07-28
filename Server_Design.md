# Kung-Fu Chess — Scalable Server Architecture Proposal

**Scope:** Evolve the current single-process `AppServer` (asyncio + `websockets`, in-process `Matchmaker` / `RoomManager` / `GameSession`, SQLite `users.db`) into a horizontally scalable cloud architecture supporting **100M registered users** and **10M concurrent players**, aligned with the reviewed KamaTech reference architecture.

---

## 1. System Architecture Diagram

```
                                   ┌─────────────────────────┐
                                   │        Clients            │
                                   └────┬────────────────┬─────┘
                                        │ REST/HTTP       │ WebSocket
                              (login, rooms, history)  (live moves, state)
                                        │                │
                          ┌─────────────▼───┐   ┌────────▼──────────┐
                          │   API Gateway     │   │   WS Gateway       │
                          │   (REST/HTTP)     │   │  (async I/O, no    │
                          │                   │   │  thread-per-client)│
                          └───┬───────────┬───┘   └─────────┬──────────┘
                              │           │                  │
                     ┌────────▼──┐  ┌─────▼─────┐            │
                     │   Auth    │  │ Rooms API │            │
                     │  Service  │  │(CRUD/hist)│            │
                     └────┬──────┘  └─────┬─────┘            │
                          │               │                  │
                          └───────┬───────┴──────────┬───────┘
                                  │                  │
                     ┌────────────▼──────────────────▼───────────┐
                     │              NATS Event Bus                 │
                     │  (internal control-plane messages only:     │
                     │   "matched", "allocate room", "room ready")  │
                     └───┬─────────────┬─────────────┬────────────┘
                         │             │             │
                ┌────────▼───┐  ┌──────▼──────┐  ┌────▼──────────────┐
                │ Matchmaker │─►│Game Allocator│─►│  (writes mapping   │
                │(ELO queue) │  │(picks shard) │  │   into Redis)      │
                └────────────┘  └──────┬───────┘  └────────────────────┘
                                        │
                     ┌──────────────────▼───────────────────────┐
                     │           Redis Cluster (single store)      │
                     │  • room_id → {shard_ip:port, worker_pid}     │
                     │    (this IS the "registry" — not a service) │
                     │  • sessions, presence, matchmaking queue,    │
                     │    reconnect state, room command queues      │
                     └───┬──────────────────────────────┬──────────┘
                         │                              │
             ┌───────────▼────────┐          ┌──────────▼─────────┐
             │  Game Server Shard A│   ...    │ Game Server Shard N │
             │  (Docker, K8s Deploy│          │                      │
             │   or Agones-managed)│          │                      │
             │  N worker processes │          │  N worker processes  │
             │  (multiprocessing), │          │                      │
             │  authoritative       │          │                      │
             │  GameEngine per room │          │                      │
             └───────────┬─────────┘          └──────────┬───────────┘
                         │                                │
         ┌───────────────┴────────────────┬───────────────┴─────────┐
         │                                │                          │
┌────────▼─────────┐           ┌──────────▼─────────┐     ┌──────────▼─────────┐
│   PostgreSQL       │           │  (same Redis        │     │    Observability     │
│ users, games,       │           │   cluster above,     │     │ logs, metrics,       │
│ results, move       │           │   used for hot state)│     │ alerts, traces,      │
│ history             │           │                      │     │ load tests           │
└────────────────────┘           └──────────────────────┘     └──────────────────────┘

  One Region = one Kubernetes / K3s cluster. Everything above is containerized
  and runs on it. Dashed control paths (heartbeats, allocation decisions) are
  logically separate from the solid data paths (moves, state updates).
  For very large scale, this whole region is replicated across multiple
  regions with geographic client routing in front of the API/WS Gateways.

  GATEWAY ROLE, EXPLICITLY: neither Gateway ever decides game rules — the
  client doesn't, and the Gateway doesn't either. The GameEngine inside each
  Game Server Shard remains the single source of truth. Both Gateways are
  stateless connection edges: API Gateway handles short request/response
  calls, WS Gateway holds long-lived connections and relays live traffic —
  neither stores room or game state itself.
```

---

## 2. Services and Responsibilities

| Service | Responsibility | Current codebase equivalent |
|---|---|---|
| **API Gateway** | Handles non-real-time HTTP/REST traffic: login, room CRUD, match history queries. Stateless, scales on request rate. | New split-out of `AppServer._on_connect` (today merges everything) |
| **WS Gateway** | Terminates the client's live WebSocket, checks the session with Auth, and relays moves/state updates in both directions. Async I/O, no thread-per-client. Holds no room/game state. | `AppServer._on_connect` (live-connection half) |
| **Auth Service** | Validates credentials/tokens, issues session tokens, reads/writes user identity + rating in PostgreSQL. | `server/auth/auth_service.py`, `auth_handler.py` |
| **Rooms API** | Non-real-time room operations: create/list/inspect rooms, fetch history — a REST resource sitting behind the API Gateway, distinct from live allocation. | `server/room_manager.py` (CRUD half) |
| **Matchmaker** | Maintains the ELO-based search queue, pairs players, emits a "matched" event over NATS. | `server/matchmaker.py` |
| **Game Allocator** | Receives "matched" events, decides which Game Server Shard a new room runs on (least-loaded / consistent hashing), writes the `room_id → shard` mapping into Redis. A focused service — allocation only, no CRUD, no history. | `server/room_manager.py` (allocation half) |
| **Game Server Shards** | Run the authoritative `GameEngine`/`GameSession` per active room, with room command queues; one worker process per CPU core, each owning a shard of rooms in memory. | `server/session/game_session.py`, `server/session/room.py` |
| **Rating Service** | Computes ELO updates at game end, persists to PostgreSQL. | `server/rating/rating_service.py`, `elo.py` |
| **Redis** | All hot, short-lived state: room→shard mapping (the "registry"), sessions, presence, reconnect state, matchmaking queue, room command queues. | New (today implicit — single process) |
| **PostgreSQL** | Durable storage: users, games, results, move history. | `server/db/database.py` (SQLite today) |
| **NATS Event Bus** | Internal control-plane messaging between backend services (Gateway↔Matchmaker↔Allocator↔Shards): "matched," "allocate room," "room ready." Not used for high-volume live gameplay traffic — that's a direct WS Gateway → Shard path via the Redis-resolved address. | New |
| **Observability** | Logs, metrics, health checks, alerting, traces, and load testing across every service. | New |

**Why split Room Manager into Rooms API + Game Allocator:** CRUD/history is a request/response, low-frequency, easily-cached workload; allocation is a latency-sensitive decision made once per match, triggered by an event, not a client request. Splitting them means each can be scaled and reasoned about independently, and a spike in one (e.g., players browsing history) can't affect the other (a burst of new matches needing shards).

---

## 3. Client Connection Flow

1. **Non-real-time calls** (login, room browsing, history) go over REST/HTTP straight to the **API Gateway**, which forwards to Auth Service or Rooms API and returns a normal response. No persistent connection involved.
2. **Live gameplay** opens a WebSocket to the **WS Gateway** (via a public LB, not directly to any Game Server Shard).
3. WS Gateway checks the session with Auth Service, then keeps the socket open as a thin relay: client messages are forwarded to whichever backend currently owns the player's state (Matchmaker while searching, the assigned Game Server Shard while playing); server-originated messages are relayed back down the same socket.
4. Neither Gateway ever holds game logic or game state — this is what makes both stateless and trivially scalable.

**What each Gateway does / does not do**

| | API Gateway | WS Gateway |
|---|---|---|
| Does | Login, room CRUD, history queries | Terminate WebSocket, relay moves/state |
| Does | Forward to Auth / Rooms API | Look up `room_id → shard` in Redis |
| Does NOT | Hold a live connection | Validate a move against chess rules |
| Does NOT | Decide matchmaking or allocation | Store `GameSession` or room state |

Because neither Gateway carries state, a client can reconnect through a *different* WS Gateway pod mid-game (e.g., after a network blip) and resume seamlessly — the new pod just re-resolves the same `room_id` in Redis and reconnects to the same Game Server worker.

---

## 4. Inter-Service Communication

| From → To | Transport | Purpose |
|---|---|---|
| Client → API Gateway | REST/HTTP | Login, room CRUD, history |
| Client → WS Gateway | WebSocket | Live moves, state updates |
| API Gateway → Auth Service | Sync RPC | Login/session validation |
| API Gateway → Rooms API | Sync RPC | Room CRUD, history queries |
| WS Gateway → Auth Service | Sync RPC | Validate session on connect |
| WS Gateway → Matchmaker | NATS request/event | Submit `PlayRequest`, receive match-found event |
| Matchmaker → Game Allocator | NATS event | "players X,Y matched" → allocate room |
| Game Allocator → Redis | Redis `SET` | Register `room_id → shard` |
| WS Gateway → Redis | Redis `GET` | Resolve `room_id → shard` on every join/reconnect |
| WS Gateway → Game Server Shard | Direct routed connection (address resolved via Redis) | Forward gameplay moves, receive state updates |
| Game Server Shard → Rating Service | Sync RPC / NATS event | Report match result for ELO update |
| Game Server Shard → Redis | Room command queues, presence | Buffer/relay per-room commands, track active rooms |
| All services → Observability | Metrics/log/trace export | Health checks, dashboards, alerting |

NATS carries **control-plane** messages only (low volume, short-lived events like "matched" or "allocate room"). Live gameplay traffic (moves, state broadcasts) flows on the direct WS Gateway ↔ Game Server Shard path, resolved via Redis — not through NATS — to avoid adding a hop to the highest-frequency traffic in the system.

---

## 5. Assigning Players to Game Servers

- Game Server Shards **do not** self-select; the **Game Allocator** owns the assignment decision.
- Each shard periodically reports its load (active rooms, CPU) into Redis as a lightweight heartbeat key per worker.
- On a "matched" event from the Matchmaker (via NATS), the Game Allocator reads those heartbeat keys and picks the least-loaded shard (consistent hashing is an alternative if session affinity is preferred).
- The chosen shard/worker address is written to Redis, keyed by the new `room_id`.
- Both players' WS Gateways are told which shard to route to for that `room_id`.

---

## 6. Joining Any Room

- Rooms are **global**, not tied to any single Gateway pod. A `room_id` is a cluster-wide identifier.
- When a client sends `RoomJoin(room_id)`, its WS Gateway does a single Redis `GET room:{room_id}` to resolve the owning shard — there's no separate "registry service" to call; Redis *is* the registry.
- The WS Gateway opens (or reuses) an internal connection to that shard and relays the join request.
- Because Redis is shared cluster-wide, it doesn't matter which Gateway pod, zone, or shard originally created the room — any client connecting through any WS Gateway can reach it.

---

## 7. Room ID → Game Server Mapping

- Storage: a single **Redis hash/key-value** entry, `room:{room_id} -> {shard_ip, port, worker_pid}`. This *is* the "registry" referenced elsewhere in this document — deliberately not its own microservice, since that would just add a network hop in front of a lookup Redis already serves in sub-millisecond time.
- Written once at room creation by the Game Allocator; deleted by the Game Server Shard on game termination (Section 15).
- TTL as a safety net (e.g. 2 hours) to auto-evict orphaned entries if a shard crashes without cleanup.
- Redis is chosen over PostgreSQL for this mapping because lookups happen on every join/reconnect and need sub-millisecond latency at 10M-concurrent scale; PostgreSQL is reserved for durable, less latency-sensitive data.

---

## 8. Docker Container Organization

| Container image | Contains | Scaling unit |
|---|---|---|
| `api-gateway` | REST/HTTP handling, thin routing | Deployment, N replicas, stateless |
| `ws-gateway` | WebSocket terminator, async I/O relay | Deployment, N replicas, stateless |
| `auth-service` | `auth_service.py`, `auth_handler.py`, PostgreSQL client | Deployment, N replicas, stateless |
| `rooms-api` | Room CRUD/history logic | Deployment, N replicas, stateless |
| `matchmaker` | `matchmaker.py` logic against Redis queue, NATS producer | Deployment, N replicas, stateless |
| `game-allocator` | Shard-selection logic, Redis writer, NATS consumer | Deployment, N replicas, stateless |
| `game-server-shard` | `game_session.py`, `player_connection.py`, authoritative GameEngine | Deployment (or Agones-managed fleet); each pod runs **one process per CPU core** internally |
| `rating-service` | `rating_service.py`, `elo.py` | Deployment, N replicas, stateless |
| `redis` | Room registry, presence, matchmaking/command queues | Managed cluster (e.g. Redis Cluster / cloud-managed) |
| `postgres` | Users, games, results, move history | Managed cluster with read replicas |
| `nats` | Internal control-plane event bus | Clustered NATS deployment |
| `observability` (Prometheus/Grafana/ELK-style stack) | Metrics, logs, traces, alerting, load-test tooling | Deployed alongside, scraping/collecting from every pod |

Every service ships as its own image with its own `Dockerfile`; no shared "mega-container." This lets each layer scale, deploy, and roll back independently.

---

## 9. Local Development: Docker Compose

Before any Kubernetes/K3s work, a minimal `docker-compose.yml` should bring up just enough to prove the service split actually works end-to-end on a single machine:

```
services:
  api-gateway, ws-gateway        (1 replica each)
  auth-service, rooms-api        (1 replica each)
  matchmaker, game-allocator     (1 replica each)
  game-server-shard              (1 replica, multiple worker processes)
  redis                          (single instance)
  postgres                       (single instance)
  nats                           (single instance)
```

No HPA, no multi-region, no managed-cloud Redis/Postgres — just enough wiring to validate that a client can log in, get matched, get allocated to a shard, play a full game, and see the result persisted. This is the "small thing that works" milestone before touching K8s at all; Kubernetes/K3s manifests are a later step that mirror this same service list with scaling and self-healing added on top.

---

## 10. Where Multiprocessing Is Used, and Why

```
                       Game Server Shard  (container, e.g. 4 vCPUs)
        ┌───────────────────────────────────────────────────────────┐
        │                     Supervisor (main process)              │
        │        heartbeats load to Redis, spawns/monitors workers   │
        └───────┬───────────────┬───────────────┬───────────────┬────┘
                │               │               │               │
        ┌───────▼──────┐┌───────▼──────┐┌───────▼──────┐┌───────▼──────┐
        │  Worker proc 0 ││  Worker proc 1 ││  Worker proc 2 ││  Worker proc 3 │
        │  (own asyncio  ││  (own asyncio  ││  (own asyncio  ││  (own asyncio  │
        │   event loop)  ││   event loop)  ││   event loop)  ││   event loop)  │
        │                ││                ││                ││                │
        │  Rooms:        ││  Rooms:        ││  Rooms:        ││  Rooms:        │
        │  R101, R104,   ││  R102, R107,   ││  R103, R109,   ││  R105, R110,   │
        │  R108 ...      ││  R111 ...      ││  R112 ...      ││  R113 ...      │
        └───────────────┘└───────────────┘└───────────────┘└───────────────┘
                │               │               │               │
                └───────────────┴───────┬───────┴───────────────┘
                                        │
                          Redis: room:{id} → worker_pid (port)
                          so WS Gateways reach the exact process,
                          bypassing the supervisor on the hot path
```

- A single Game Server **shard/container** runs **one OS process per CPU core** (Python's GIL prevents true parallel CPU-bound work inside one process — `asyncio` alone only gives concurrency, not parallelism).
- Each worker process owns an independent shard of active rooms and runs its own `asyncio` event loop internally, exactly like today's `AppServer._match_loop` / per-connection coroutine model, but multiplied by `N cores`.
- Rooms are pinned to a single worker process for their entire lifetime (a game only lasts 30–90s, so no need for mid-game migration).
- The Redis mapping stores not just the shard's address but also the worker's port/PID, so the WS Gateway routes directly to the correct process.
- **Why:** Chess-with-real-time-moves game logic (validation, timers, state broadcast) is short but CPU-touching; multiprocessing lets one shard use all its cores instead of one, multiplying room capacity per container without needing more shards.

---

## 11. Where Kubernetes (and Agones) Fit

- Every service in Section 8 is deployed as a Kubernetes **Deployment** (or equivalent) with its own **HorizontalPodAutoscaler**, scaling on CPU/connection-count metrics.
- The public LB is a Kubernetes `Service` (`LoadBalancer` type) in front of the API/WS Gateway pods.
- **Game Server Shards** scale based on active-room count reported to Redis, not raw CPU alone, since games are short-lived and bursty.
- **Agones (optional fleet manager):** a natural upgrade over a generic Deployment specifically for Game Server Shards — it understands game-session semantics (allocates a *ready* shard for a new room rather than any pod, and supports graceful shutdown that waits for an in-progress game to finish rather than killing it mid-match). Not required for an initial implementation, but the clear next step once the plain-Deployment version works.
- K3s is suitable for development, staging, or edge/regional mini-clusters (lighter control plane); full Kubernetes (EKS/GKE/AKS) is used for the production, multi-region deployment where managed control-plane HA and cloud-integrated LB/storage are needed.
- Namespaces separate environments (`dev`, `staging`, `prod`); each service has its own `Deployment` + `Service` + `HPA` manifest, with Redis/PostgreSQL/NATS as managed or clustered dependencies rather than plain pods.
- **Multi-region:** the entire cluster described in Section 1 is one region's worth of infrastructure. At very large scale, this same stack is repeated per region, with geo-aware routing sending clients to their nearest region's API/WS Gateway; cross-region concerns (e.g., a global leaderboard) would live in PostgreSQL replication or a separate aggregation step, out of scope for this iteration.

---

## 12. Replacing SQLite

**SQLite is not viable** at this scale: it's a single-file, single-writer database with no built-in replication, no network access from multiple hosts, and no horizontal scaling — it cannot be shared safely across dozens of Auth/Rating Service pods.

**Recommendation: PostgreSQL**, deployed as a managed cluster (e.g., Amazon Aurora PostgreSQL / Cloud SQL) with:
- A **primary** for writes (new users, rating updates, match history inserts).
- **Read replicas** for read-heavy queries (profile lookups, leaderboard queries), since reads vastly outnumber writes.
- **Sharding by user ID range** (or a managed distributed-Postgres flavor like Citus) once 100M users exceed a single primary's comfortable capacity.

PostgreSQL is chosen over a NoSQL store because user accounts, ratings, and match history are strongly relational, need transactional integrity (e.g., atomic ELO updates for two players in one game), and the existing `user_repository.py` abstraction maps naturally onto SQL.

---

## 13. Database Usage by Service

| Service | Reads | Writes |
|---|---|---|
| Auth Service | User credentials, profile on login | New user registration |
| Rating Service | Current ELO before a match | Updated ELO after a match ends |
| Matchmaker | Player rating (to bucket search) | — |
| Rooms API / Game Server Shard | Room/match history | Match history record on game end |
| (Everything hot-path) | Room→shard mapping, presence, matchmaking queue | *(via Redis, not PostgreSQL)* |

Redis is the **hot path** store (sub-ms, ephemeral, in-memory): presence, room↔shard mapping, matchmaking queue, room command queues.
PostgreSQL is the **durable path** store (accounts, ELO, match history) — written less frequently, tolerant of a few ms of latency.

---

## 14. Network Traffic Calculation

**Assumptions**
- Concurrent players: **10,000,000**
- Move frequency: 1 move per player every **2 seconds**
- Each move triggers a state update sent to the player(s) in that room (assume 1 outbound message per move received, i.e., roughly symmetric traffic for this estimate)
- Estimated message size: **~200 bytes** (compact JSON: room_id, move, timestamp, piece, position — small structured payload)

**Calculation**

| Metric | Value |
|---|---|
| Messages per player per second | 1 / 2 = 0.5 |
| Total inbound messages/sec (moves) | 10,000,000 × 0.5 = **5,000,000 msg/s** |
| Total outbound messages/sec (broadcasts, ~1:1 for a 2-player room) | ≈ **5,000,000 msg/s** |
| Total messages/sec (in + out) | ≈ **10,000,000 msg/s** |
| Bandwidth per direction | 5,000,000 × 200 bytes = 1,000,000,000 bytes/s = **~1 GB/s (~8 Gbps)** |
| Total bandwidth (both directions) | ≈ **2 GB/s (~16 Gbps)** |

**Is this a lot?** For a single machine/NIC, yes — 16 Gbps sustained would saturate a typical 10 Gbps NIC. But distributed across, say, 200–500 WS Gateway/Game Server Shard pods, this is roughly **30–80 Mbps per pod**, which is entirely manageable for standard cloud networking and exactly why horizontal scaling (many small pods behind a LB) — rather than one large server — is necessary at this scale.

---

## 15. Supporting the Scale Requirements

| Requirement | How the architecture supports it |
|---|---|
| **100M registered users** | PostgreSQL cluster with replicas/sharding stores accounts durably; Auth Service is stateless and scales independently of active-player count. |
| **10M concurrent players** | Load spread across many stateless API/WS Gateway pods and many multiprocess Game Server Shards; Redis handles the high-frequency room-lookup/presence traffic that a relational DB couldn't sustain. |
| **Horizontal scaling** | Every service (API Gateway, WS Gateway, Auth, Rooms API, Matchmaker, Game Allocator, Game Server Shards, Rating) is a separate, independently-scaled Kubernetes Deployment; none holds cluster-wide state in-process — shared state lives in Redis/PostgreSQL. |
| **Fault tolerance** | Stateless services can be killed/restarted freely (K8s reschedules pods). Shard loss only affects the rooms it owned; Redis TTL cleans up stale mappings; Matchmaker/Game Allocator retry logic re-queues affected players. Redis, PostgreSQL, and NATS run as managed/replicated clusters, not single instances. |

---

## 16. Game Lifecycle

1. **Matchmaking** — Player sends `PlayRequest` → WS Gateway → Matchmaker enqueues by ELO bucket → periodic match loop pairs two players → emits a "matched" event over NATS.
2. **Room Creation** — Game Allocator consumes the "matched" event, generates a new `room_id`, selects the least-loaded Game Server Shard, and writes `room_id → shard` into Redis.
3. **Game Execution** — The shard's designated worker process instantiates the authoritative `GameEngine`/`GameSession`; both players' WS Gateways route moves directly to that worker; state broadcasts flow back through the same path; expected duration 30–90 seconds given short game rounds.
4. **Game Termination** — `GameSession` ends on checkmate/timeout/resignation; the shard reports the result to Rating Service (ELO update) and writes match history to PostgreSQL.
5. **Resource Cleanup** — The shard deletes the room's in-memory state and removes the `room_id` entry from Redis (`DEL`); the worker process becomes available for a new room immediately (no restart needed, matching the current in-process `_run_session` cleanup pattern, just generalized across shards/processes).

---

## 17. Failure Flow

Different components fail differently because only some of them hold state. The diagram and table below trace what happens for each failure case.

```
   Client              WS Gateway            Matchmaker /              Game Server
                          Pods                Game Allocator              Shard
     │                     │                        │                        │
     │   WS Gateway dies    │                        │                        │
     │───────X              │                        │                        │
     │   LB detects failed   readiness probe,          │                        │
     │   health check, reconnects client to a          │                        │
     │   different WS Gateway pod ─────────────────────►│                        │
     │   New pod re-resolves room_id in Redis,          │                        │
     │   reconnects to the SAME worker ─────────────────────────────────────────►│
     │                     │                        │                        │
     │                     │   Shard dies             │                        X
     │                     │   (worker + its rooms)   │                        │
     │                     │◄── Redis TTL / missed     │                        │
     │                     │    heartbeat marks shard  │                        │
     │                     │    stale                  │                        │
     │◄── Game Allocator / │                        │                        │
     │    shard detects     │                        │                        │
     │    the orphaned      │                        │                        │
     │    room, sends       │                        │                        │
     │    clients a "game   │                        │                        │
     │    aborted /         │                        │                        │
     │    reconnect" event  │                        │                        │
     │                     │                        │                        │
     │                     │   Redis node dies        │                        │
     │                     │   (replica promoted by    │                        │
     │                     │    Redis Sentinel/Cluster)│                        │
     │                     │   brief lookup failures,   │                        │
     │                     │   client-visible as retry  │                        │
     │                     │   / short reconnect delay  │                        │
     │                     │                        │                        │
     │                     │   PostgreSQL primary dies │                        │
     │                     │   (managed failover to     │                        │
     │                     │    standby, seconds-scale) │                        │
     │                     │   Gameplay unaffected      │                        │
     │                     │   (hot path is Redis, not  │                        │
     │                     │    Postgres); only ELO/    │                        │
     │                     │   history writes queue     │                        │
     │                     │   briefly and then flush   │                        │
```

| Failure | Detection | Blast radius | Recovery |
|---|---|---|---|
| **WS Gateway pod crashes** | K8s liveness/readiness probe fails; LB stops routing to it | Only the clients currently connected to that pod | LB reconnects them to a healthy WS Gateway pod; new pod re-resolves `room_id` in Redis and reattaches to the same shard worker — no game state is lost, since the Gateway never held any |
| **Game Server Shard (or one worker process) crashes** | Missed Redis heartbeat / K8s pod restart event | Only the rooms owned by that shard/worker (bounded, since rooms are sharded, not replicated across the whole fleet) | Affected clients receive a "game aborted" message via their WS Gateway (which still holds the socket) and are routed back into Matchmaker/Game Allocator to start a fresh room; stale `room_id` entries expire via Redis TTL if not cleaned up explicitly |
| **Auth, Matchmaker, or Game Allocator pod crashes** | K8s restarts it; stateless, so any in-flight request simply retries | Only requests in flight to that specific pod instance | LB/service routing sends the next request to a different healthy replica; no persistent state to reconcile |
| **Redis node/shard fails** | Redis Cluster/Sentinel detects and promotes a replica | Brief (sub-second to low-second) latency spike or failed lookups during failover | Clients experience a short retry/reconnect; because the registry, presence, and queues are all in Redis, this is the one component whose failure has cluster-wide (though brief) impact — mitigated by running Redis as a replicated cluster, not a single node |
| **PostgreSQL primary fails** | Managed database failover (cloud-native, seconds-scale) | ELO updates and match-history writes queue or briefly fail; **live gameplay is unaffected**, since the hot path never touches PostgreSQL | Standby promoted automatically; queued writes flush once the new primary is available |

**Design takeaway:** the architecture is built so that the only genuinely cluster-wide single point of failure is Redis, and that risk is addressed by running it as a replicated cluster rather than a single node — every other component's failure is isolated to the slice of players it was directly serving.

### Preserving an in-progress game across a shard crash (not yet implemented, recommended next step)

The lifecycle above returns players to matchmaking on a shard crash — the game itself is lost, not recovered. Given games only last 30–90 seconds, the recommended approach is **periodic checkpointing to Redis**: after every move (or every few moves), the worker writes a compact snapshot of the board/timers to Redis alongside the existing room mapping. On crash, a newly-assigned worker loads the last snapshot, rebuilds the `GameSession`, and both players' WS Gateways are redirected to it — resuming from the last saved move, at the cost of at most the single move made right before the crash. A stronger alternative (full event sourcing of every move via NATS or Kafka, replayed to reconstruct exact state with zero loss) is a viable phase-2 upgrade if a "zero lost moves" guarantee becomes a hard requirement, at the cost of extra infrastructure and slightly higher recovery latency.

---

## 18. Observability

| Concern | What's collected | Where |
|---|---|---|
| **Logs** | Structured logs from every service (request IDs, room IDs, error traces) | Centralized log aggregation (e.g. ELK/Loki-style stack) |
| **Metrics** | Per-service request rate/latency/error rate; Redis/NATS/PostgreSQL throughput; active-room and active-worker counts per shard | Prometheus-style scraping + Grafana dashboards |
| **Health checks** | Liveness/readiness probes per pod, feeding directly into K8s scheduling and LB routing decisions | Kubernetes probes |
| **Alerts** | Threshold- or anomaly-based alerts (e.g. shard heartbeat gaps, Redis failover events, elevated WS reconnect rate) | Routed from the metrics stack to on-call notification |
| **Traces** | Cross-service request traces for slow-path debugging (e.g. a match that took unusually long to allocate) | Distributed tracing (e.g. OpenTelemetry) |
| **Load tests** | Scripted simulations of concurrent players/matches to validate the traffic estimates in Section 14 before relying on them in production | Run against staging, gating any capacity claims |

Observability isn't optional tooling bolted on later — at 10M-concurrent scale, it's the only way to know a shard is silently overloaded, a Redis failover is degrading reconnects, or a region is trending toward saturation before players notice.
