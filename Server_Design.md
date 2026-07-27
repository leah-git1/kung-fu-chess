# Kung-Fu Chess — Scalable Server Architecture Proposal

**Scope:** Evolve the current single-process `AppServer` (asyncio + `websockets`, in-process `Matchmaker` / `RoomManager` / `GameSession`, SQLite `users.db`) into a horizontally scalable cloud architecture supporting **100M registered users** and **10M concurrent players**.

---

## 1. System Architecture Diagram

```
                                   ┌─────────────────────────┐
                                   │        Players          │
                                   │  (game client, WS/TLS)  │
                                   └────────────┬────────────┘
                                                │
                                   ┌────────────▼─────────────┐
                                   │    Load Balancer (L4)    │
                                   │  (K8s Service / cloud LB)│
                                   └────────────┬─────────────┘
                                                │
                     ┌──────────────────────────┼──────────────────────────┐
                     │                          │                          │
             ┌───────▼───────┐          ┌───────▼───────┐          ┌───────▼───────┐
             │ Gateway Pod 1 │          │  Gateway Pod 2│   ...    │ Gateway Pod N │
             │(WS terminator)│          │               │          │               │
             └───────┬───────┘          └───────┬───────┘          └───────┬───────┘
                     │                          │                          │
                     └────────────┬─────────────┴──────────────┬───────────┘
                                  │                            │
                     ┌────────────▼───────────┐   ┌────────────▼────────────┐
                     │   Auth Service (pods)  │   │  Matchmaking Service    │
                     │  verify/issue session  │   │  (ELO queue, pods)      │
                     └────────────┬───────────┘   └────────────┬────────────┘
                                  │                            │
                                  │                 ┌──────────▼─────────────┐
                                  │                 │  Room Manager Service  │
                                  │                 │(creates room_id, picks │
                                  │                 │ target Game Server,    │
                                  │                 │ writes mapping below)  │
                                  │                 └───────────┬────────────┘
                                  │                             │
                     ┌────────────▼─────────────────────────────▼───────────┐
                     │            Redis Cluster  (single logical store)     │
                     │  • Game Server Registry: room_id → {server_ip:port,  │
                     │    worker_pid}         ← NOT a separate service,     │
                     │    just a Redis hash, read on every join/reconnect   │
                     │  • Presence, matchmaking queue, pub/sub              │
                     └────────────┬──────────────────────────────┬──────────┘
                                  │                              │
                 ┌────────────────▼───────┐        ┌─────────────▼───────────┐
                 │  Game Server Pod A     │        │    Game Server Pod B    │
                 │(Docker, K8s Deployment)│  ...   │                         │
                 │N worker processes      │        │   N worker processes    │
                 │ (multiprocessing),     │        │                         │
                 │each owns a set of Rooms│        │                         │
                 └────────────┬───────────┘        └─────────────┬───────────┘
                              │                                  │
                              └────────────────┬─────────────────┘
                                               │
                                  ┌────────────▼────────────┐
                                  │  PostgreSQL Cluster     │
                                  │(durable: users, ratings,│
                                  │ match history)          │
                                  └─────────────────────────┘

         All boxes except the Redis/PostgreSQL clusters run as containers on
         a Kubernetes cluster (K3s in dev/edge, full K8s in production),
         each service as its own Deployment, independently scaled.

         GATEWAY ROLE, EXPLICITLY: the Gateway is a stateless connection/
         routing edge only. It terminates the client's WebSocket, checks
         auth, and forwards messages to whichever backend currently owns
         the player's state (Matchmaking, Room Manager, or a Game Server
         worker looked up via Redis). It never runs game logic and never
         stores room state itself — that's what lets it scale by simply
         adding pods, with zero coordination between them.
```

---

## 2. Services and Responsibilities

| Service | Responsibility | Current codebase equivalent |
|---|---|---|
| **Gateway** | **Pure stateless connection edge.** Terminates client WebSocket/TLS, validates the auth token with Auth Service, and *routes* — never processes — every subsequent message to whichever backend currently owns the player's state (Matchmaking during search, Room Manager during room setup, a specific Game Server worker during play). Holds no room/game state itself, so any Gateway pod can serve any client at any moment. | `AppServer._on_connect` (today merges gateway + everything else) |
| **Auth Service** | Validates credentials/tokens, issues session tokens, reads/writes user identity + rating in PostgreSQL. Stateless, horizontally scaled. | `server/auth/auth_service.py`, `auth_handler.py` |
| **Matchmaking Service** | Maintains the ELO-based search queue, pairs players, emits a "match found" event with player IDs. Stateless workers, shared queue in Redis. | `server/matchmaker.py` |
| **Room Manager** | Allocates a `room_id`, selects the least-loaded Game Server for it, writes the `room_id → game_server` mapping into Redis (the Registry — see below), handles join/spectate requests for existing rooms. | `server/room_manager.py` |
| **Game Server Registry** *(not a standalone service — a Redis data structure)* | A single Redis hash/key-space (`room:{room_id} → {server_ip, port, worker_pid}`) that is the source of truth for locating any active room. Deliberately folded into the same Redis cluster used for presence/matchmaking rather than a separate service, since it's one more small, latency-critical key-value workload with no relational needs. | New component (today implicit — single process) |
| **Game Server** | Runs active game sessions (`GameSession`, `PlayerConnection` logic), one process per CPU core, each process owns a shard of rooms in memory. | `server/session/game_session.py`, `server/session/room.py` |
| **Rating Service** | Computes ELO updates at game end, persists to PostgreSQL. | `server/rating/rating_service.py`, `elo.py` |
| **Database Layer** | Durable storage for users, ratings, match history. | `server/db/database.py` (SQLite today) |

---

## 3. Client Connection Flow (Through the Gateway)

1. Client opens a WebSocket to a **public LB endpoint** (not to any Game Server directly).
2. LB round-robins the TCP connection to one of many stateless **Gateway pods**.
3. Gateway authenticates the connection by forwarding the token/credentials to **Auth Service** (gRPC/HTTP call).
4. Once authenticated, the Gateway keeps the socket open and becomes a thin relay: every client message is forwarded internally to the service that owns the current game state for that player (Matchmaking, Room Manager, or a specific Game Server), and every server-originated message is relayed back down the same socket.
5. The Gateway itself never holds game logic — this is what makes it stateless and trivially scalable (add more pods behind the LB).

**What the Gateway does / does not do**

| Does | Does NOT do |
|---|---|
| Terminate WebSocket/TLS | Validate a move against chess rules |
| Check auth token with Auth Service | Store `GameSession` or `Room` state |
| Look up `room_id` → server in Redis | Decide matchmaking pairings |
| Relay bytes in both directions | Persist anything to PostgreSQL |
| Multiplex many client connections | Retain state between reconnects |

Because the Gateway carries no state, a client can reconnect through a *different* Gateway pod mid-game (e.g., after a network blip) and resume seamlessly — the new Gateway just re-resolves the same `room_id` in Redis and reconnects to the same Game Server worker.

---

## 4. Inter-Service Communication

| From → To | Transport | Purpose |
|---|---|---|
| Gateway → Auth Service | Sync RPC (gRPC/HTTP) | Validate session on connect |
| Gateway → Matchmaking | Sync RPC + async push | Submit `PlayRequest`, receive match-found event |
| Gateway → Room Manager | Sync RPC | `RoomCreate` / `RoomJoin` |
| Gateway → Game Server | Direct routed connection (via Redis Registry lookup) | Forward gameplay moves, receive state updates |
| Matchmaking → Room Manager | Async event (pub/sub) | "players X,Y matched" → allocate room |
| Room Manager → Redis (Registry) | Redis `SET` | Register `room_id → server` |
| Room Manager → Game Server | Sync RPC | "open a room with these players" |
| Gateway → Redis (Registry) | Redis `GET` | Resolve `room_id → server` on every join/reconnect |
| Any service → Auth/Rating | Sync RPC | Read profile, write ELO update |
| Game Server → Redis | Pub/Sub | Broadcast room events for cross-pod visibility |

Internal traffic uses a service mesh / cluster-internal DNS (Kubernetes `ClusterIP` services); Redis pub/sub decouples services that don't need a direct synchronous call.

---

## 5. Assigning Players to Game Servers

- Game Servers **do not** self-select; the **Room Manager** owns the assignment decision.
- Each Game Server periodically reports its load (active rooms, CPU) into Redis (a lightweight heartbeat key per worker — again, no separate "Registry service," just more Redis keys alongside the room mapping).
- When a room must be created, Room Manager reads those heartbeat keys and picks the Game Server with the lowest active-room count (simple least-loaded strategy; consistent hashing is an alternative if session affinity by shard is preferred).
- The chosen `game_server_id` is written to Redis, keyed by the new `room_id`.
- Both players' Gateways are told which Game Server address to route to for that `room_id`.

---

## 6. Joining Any Room

- Rooms are **global**, not tied to any single Gateway. A `room_id` is a cluster-wide identifier.
- When a client sends `RoomJoin(room_id)`, its Gateway does a single Redis `GET room:{room_id}` to resolve the owning Game Server — there is no intermediate "Registry service" to call, Redis *is* the registry.
- The Gateway opens (or reuses) an internal connection to that Game Server and relays the join request.
- Because Redis is shared cluster-wide, it doesn't matter which Gateway pod, data-center zone, or Game Server originally created the room — any client connecting through any Gateway can reach it.

---

## 7. Room ID → Game Server Mapping

- Storage: a single **Redis hash / key-value** entry, `room:{room_id} -> {game_server_ip, port, worker_pid}`. This *is* the "Game Server Registry" referenced elsewhere in this document — it is intentionally not implemented as its own microservice, since that would just add a network hop in front of a lookup Redis already serves in sub-millisecond time.
- Written once at room creation by Room Manager; deleted by the Game Server on game termination (Section 15).
- TTL as a safety net (e.g. 2 hours) to auto-evict orphaned entries if a pod crashes without cleanup.
- Redis is chosen over PostgreSQL for this mapping because lookups happen on every join/reconnect and need sub-millisecond latency at 10M-concurrent scale; PostgreSQL is reserved for durable, less latency-sensitive data.

---

## 8. Docker Container Organization

| Container image | Contains | Scaling unit |
|---|---|---|
| `gateway` | WebSocket terminator, thin routing logic | Deployment, N replicas, stateless |
| `auth-service` | `auth_service.py`, `auth_handler.py`, PostgreSQL client | Deployment, N replicas, stateless |
| `matchmaking-service` | `matchmaker.py` logic against Redis queue | Deployment, N replicas, stateless |
| `room-manager` | `room_manager.py` + Registry client | Deployment, N replicas, stateless |
| `game-server` | `game_session.py`, `player_connection.py`, room shard logic | StatefulSet-like Deployment; each pod runs **one process per CPU core** internally |
| `rating-service` | `rating_service.py`, `elo.py` | Deployment, N replicas, stateless |
| `redis` | Registry, presence, matchmaking queue, pub/sub | Managed cluster (e.g. Redis Cluster / cloud-managed) |
| `postgres` | Users, ratings, match history | Managed cluster with read replicas |

Every service ships as its own image with its own `Dockerfile`; no shared "mega-container." This lets each layer scale, deploy, and roll back independently.

---

## 9. Where Multiprocessing Is Used, and Why

```
                       Game Server Pod  (container, e.g. 4 vCPUs)
        ┌──────────────────────────────────────────────────────────────────────┐
        │                     Supervisor (main process)                        │
        │        heartbeats load to Redis, spawns/monitors workers             │
        └────────┬────────────────┬─────────────────┬─────────────────┬────────┘
                 │                │                 │                 │
        ┌────────▼───────┐┌───────▼────────┐┌───────▼────────┐┌───────▼────────┐
        │  Worker proc 0 ││  Worker proc 1 ││  Worker proc 2 ││  Worker proc 3 │
        │  (own asyncio  ││  (own asyncio  ││  (own asyncio  ││  (own asyncio  │
        │   event loop)  ││   event loop)  ││   event loop)  ││   event loop)  │
        │                ││                ││                ││                │
        │  Rooms:        ││  Rooms:        ││  Rooms:        ││  Rooms:        │
        │  R101, R104,   ││  R102, R107,   ││  R103, R109,   ││  R105, R110,   │
        │  R108 ...      ││  R111 ...      ││  R112 ...      ││  R113 ...      │
        └────────────────┘└────────────────┘└────────────────┘└────────────────┘
                │               │               │               │
                └───────────────┴───────┬───────┴───────────────┘
                                        │
                          Redis: room:{id} → worker_pid (port)
                          so Gateways reach the exact process,
                          bypassing the supervisor on the hot path
```

- A single Game Server **pod/container** runs **one OS process per CPU core** (Python's GIL prevents true parallel CPU-bound work inside one process — `asyncio` alone only gives concurrency, not parallelism).
- Each worker process owns an independent shard of active rooms and runs its own `asyncio` event loop internally, exactly like today's `AppServer._match_loop` / per-connection coroutine model, but multiplied by `N cores`.
- Rooms are pinned to a single worker process for their entire lifetime (a game only lasts 30–90s, so no need for mid-game migration).
- The Game Server Registry stores not just the pod address but also the worker's port/PID, so the Gateway routes directly to the correct process.
- **Why:** Chess-with-real-time-moves game logic (validation, timers, state broadcast) is short but CPU-touching; multiprocessing lets one pod use all its cores instead of one, multiplying room capacity per container without needing more pods.

---

## 10. Where Kubernetes Fits

- Every service in Section 8 is deployed as a Kubernetes **Deployment** (or equivalent) with its own **HorizontalPodAutoscaler**, scaling on CPU/connection-count metrics.
- The **LB** is a Kubernetes `Service` (`LoadBalancer` type) in front of Gateway pods.
- **Game Server** pods scale based on active-room count reported to the Registry, not raw CPU alone, since games are short-lived and bursty.
- K3s is suitable for development, staging, or edge/regional mini-clusters (lighter control plane); full Kubernetes (EKS/GKE/AKS) is used for the production, multi-region deployment where managed control-plane HA and cloud-integrated LB/storage are needed.
- Namespaces separate environments (`dev`, `staging`, `prod`); each service has its own `Deployment` + `Service` + `HPA` manifest, with Redis/PostgreSQL as managed external dependencies rather than pods.

---

## 11. Replacing SQLite

**SQLite is not viable** at this scale: it's a single-file, single-writer database with no built-in replication, no network access from multiple hosts, and no horizontal scaling — it cannot be shared safely across dozens of Auth/Rating Service pods.

**Recommendation: PostgreSQL**, deployed as a managed cluster (e.g., Amazon Aurora PostgreSQL / Cloud SQL) with:
- A **primary** for writes (new users, rating updates, match history inserts).
- **Read replicas** for read-heavy queries (profile lookups, leaderboard queries), since reads vastly outnumber writes.
- **Sharding by user ID range** (or a managed distributed-Postgres flavor like Citus) once 100M users exceed a single primary's comfortable capacity.

PostgreSQL is chosen over a NoSQL store because user accounts, ratings, and match history are strongly relational, need transactional integrity (e.g., atomic ELO updates for two players in one game), and the existing `user_repository.py` abstraction maps naturally onto SQL.

---

## 12. Database Usage by Service

| Service | Reads | Writes |
|---|---|---|
| Auth Service | User credentials, profile on login | New user registration |
| Rating Service | Current ELO before a match | Updated ELO after a match ends |
| Matchmaking | Player rating (to bucket search) | — |
| Room Manager / Game Server | — | Match history record on game end |
| (Everything hot-path) | Room-server mapping, presence, matchmaking queue | *(via Redis, not PostgreSQL)* |

Redis is the **hot path** database (sub-ms, ephemeral, in-memory): presence, room↔server mapping, matchmaking queue.
PostgreSQL is the **durable path** database (accounts, ELO, match history) — written less frequently, tolerant of a few ms of latency.

---

## 13. Network Traffic Calculation

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

**Is this a lot?** For a single machine/NIC, yes — 16 Gbps sustained would saturate a typical 10 Gbps NIC. But distributed across, say, 200–500 Gateway/Game Server pods, this is roughly **30–80 Mbps per pod**, which is entirely manageable for standard cloud networking and exactly why horizontal scaling (many small pods behind a LB) — rather than one large server — is necessary at this scale.

---

## 14. Supporting the Scale Requirements

| Requirement | How the architecture supports it |
|---|---|
| **100M registered users** | PostgreSQL cluster with replicas/sharding stores accounts durably; Auth Service is stateless and scales independently of active-player count. |
| **10M concurrent players** | Load spread across many stateless Gateway pods and many multiprocess Game Server pods; Redis handles the high-frequency room-lookup/presence traffic that a relational DB couldn't sustain. |
| **Horizontal scaling** | Every service (Gateway, Auth, Matchmaking, Room Manager, Game Server, Rating) is a separate, independently-scaled Kubernetes Deployment; none holds cluster-wide state in-process — shared state lives in Redis/PostgreSQL. |
| **Fault tolerance** | Stateless services can be killed/restarted freely (K8s reschedules pods). Game Server pod loss only affects the rooms it owned; Registry TTL cleans up stale mappings; Matchmaking/Room Manager retry logic re-queues affected players. Redis and PostgreSQL run as managed, replicated clusters, not single instances. |

---

## 15. Game Lifecycle

1. **Matchmaking** — Player sends `PlayRequest` → Gateway → Matchmaking Service enqueues by ELO bucket → periodic match loop pairs two players → emits a "matched" event with both player IDs.
2. **Room Creation** — Room Manager receives the matched pair, generates a new `room_id`, selects the least-loaded Game Server, and writes `room_id → game_server` into the Registry.
3. **Game Execution** — Game Server's designated worker process instantiates a `GameSession`; both players' Gateways route moves directly to that worker; state broadcasts flow back through the same path; expected duration 30–90 seconds given short game rounds.
4. **Game Termination** — `GameSession` ends on checkmate/timeout/resignation; Game Server sends final result to Rating Service (ELO update) and match-history write to PostgreSQL.
5. **Resource Cleanup** — Game Server deletes the room's in-memory state and removes the `room_id` entry from Redis (`DEL`); the worker process becomes available for a new room immediately (no restart needed, matching the current in-process `_run_session` cleanup pattern, just generalized across pods/processes).

---

## 16. Failure Flow

Different components fail differently because only some of them hold state. The diagram and table below trace what happens for each failure case.

```
   Client                Gateway              Room Manager /             Game Server
                          Pods                 Matchmaking                Worker Proc
     │                     │                        │                        │
     │   Gateway pod dies   │                        │                        │
     │───────X              │                        │                        │
     │   LB detects failed   readiness probe,          │                        │
     │   health check, reconnects client to a          │                        │
     │   different Gateway pod ───────────────────────►│                        │
     │   New Gateway re-resolves room_id in Redis,      │                        │
     │   reconnects to the SAME worker ─────────────────────────────────────────►│
     │                     │                        │                        │
     │                     │   Game Server pod dies   │                        X
     │                     │   (worker + its rooms)   │                        │
     │                     │◄── Redis TTL / missed     │                        │
     │                     │    heartbeat marks pod    │                        │
     │                     │    stale                  │                        │
     │◄── Room Manager /   │                        │                        │
     │    Game Server      │                        │                        │
     │    detects the      │                        │                        │
     │    orphaned room,   │                        │                        │
     │    sends clients a  │                        │                        │
     │    "game aborted /  │                        │                        │
     │    reconnect" event │                        │                        │
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
| **Gateway pod crashes** | K8s liveness/readiness probe fails; LB stops routing to it | Only the clients currently connected to that pod | LB reconnects them to a healthy Gateway pod; new Gateway re-resolves `room_id` in Redis and reattaches to the same Game Server worker — no game state is lost, since the Gateway never held any |
| **Game Server pod (or one worker process) crashes** | Missed Redis heartbeat / K8s pod restart event | Only the rooms owned by that pod/worker (bounded, since rooms are sharded, not replicated across the whole fleet) | Affected clients receive a "game aborted" message via their Gateway (which still holds the socket) and are routed back into Matchmaking/Room Manager to start a fresh room; stale `room_id` entries expire via Redis TTL if not cleaned up explicitly |
| **Auth or Matchmaking or Room Manager pod crashes** | K8s restarts it; stateless, so any in-flight request simply retries | Only requests in flight to that specific pod instance | LB/service routing sends the next request to a different healthy replica; no persistent state to reconcile |
| **Redis node/shard fails** | Redis Cluster/Sentinel detects and promotes a replica | Brief (sub-second to low-second) latency spike or failed lookups during failover | Clients experience a short retry/reconnect; because the Registry, presence, and queue are all in Redis, this is the one component whose failure has cluster-wide (though brief) impact — mitigated by running Redis as a replicated cluster, not a single instance |
| **PostgreSQL primary fails** | Managed database failover (cloud-native, seconds-scale) | ELO updates and match-history writes queue or briefly fail; **live gameplay is unaffected**, since the hot path never touches PostgreSQL | Standby promoted automatically; queued writes flush once the new primary is available |

**Design takeaway:** the architecture is built so that the only genuinely cluster-wide single point of failure is Redis, and that risk is addressed by running it as a replicated cluster rather than a single node — every other component's failure is isolated to the slice of players it was directly serving.
