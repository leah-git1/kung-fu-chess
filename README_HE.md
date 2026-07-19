# 🏯 Kung-Fu Chess - מדריך מלא למבנה הפרויקט

מדריך זה מסביר את כל קבצי הפרויקט, תפקידם, ופונקציות עיקריות בכל אחד מהם.

---

## 📋 תוכן עניינים
1. [סקירה כללית](#סקירה-כללית)
2. [תיקיית Shared - קבצים משותפים](#תיקיית-shared---קבצים-משותפים)
3. [תיקיית Server - השרת](#תיקיית-server---השרת)
4. [תיקיית Client - הקליינט](#תיקיית-client---הקליינט)

---

## 🎮 סקירה כללית

Kung-Fu Chess הוא משחק שחמט ברשת מרתיע שבו הגדלים לא קובעים את הכל. השרת מנהל משחק עם שני שחקנים, והקליינט משדר אותו לעיני השחקן.

**זרימת תקשורת:**
```
קליינט A ──→ WebSocket ──→ שרת ──→ WebSocket ──→ קליינט B
```

**מצבי הקליינט:**
- **Offline** — משחק מחול עם עצמו בגרפיקה מקומית (GraphicsApp)
- **Online** — מתחבר לשרת ומציג משחק חי (GameClientApp)

---

## 🔗 תיקיית Shared - קבצים משותפים

קבצים שגם השרת וגם הקליינט צריכים — הפרוטוקול המשותף.

### `shared/constants.py`
**תפקיד:** הגדרות גלובליות המשמשות את כל הפרויקט.

**משתנים עיקריים:**
- `DEFAULT_PORT = 5555` — פורט חיבור WebSocket
- `PROTOCOL_VERSION = 1` — גרסת הפרוטוקול (לבדיקת תאימות)
- `TICK_RATE_MS = 50` — השרת מעדכן את מצב המשחק כל 50 מילי-שניות
- `MOVE_DURATION_PER_CELL = 600` — ריצוף תנועה: 600 אלפיות לכל תא בלוח
- `JUMP_DURATION = 1000` — קפיצה אורכת 1 שנייה
- `LONG_REST_DURATION = 2000` — קור ארוך לאחר הנעה
- `SHORT_REST_DURATION = 1000` — קור קצר לאחר קפיצה
- `DISCONNECT_GRACE_S = 20` — זמן טוגר להתחברות מחדש לפני הפסד

**מה הוא משמש:**
- הגדרות זמני אנימציה (לאחוי קליינט)
- הגדרות זמני משחק (לשרת)
- קבועי רשת

---

### `shared/message_types.py`
**תפקיד:** מגדיר סוגי הודעות כ-constants כדי לא לכתוב מחרוזות גולמיות.

**קטגוריות הודעות:**

| קטגוריה | סוגים | דוגמה |
|---------|-------|-------|
| Handshake | `HELLO` | התחברות ראשונית |
| Auth | `LOGIN`, `LOGIN_OK`, `LOGIN_FAIL` | אימות משתמש |
| Matchmaking | `PLAY_REQUEST`, `MATCH_FOUND`, `SEARCH_TIMEOUT` | מציאת יריב |
| Room | `ROOM_CREATE`, `ROOM_JOIN`, `ROOM_STATE` | חדרים פרטיים |
| In-game | `START`, `MOVE`, `JUMP`, `STATE_UPDATE`, `MOVE_ACK`, `JUMP_ACK`, `GAME_OVER` | משחק חי |
| Logging | `LOG_EVENT` | רישום אירועים |
| Errors | `ERROR`, `OPPONENT_DISCONNECTED` | טיפול בשגיאות |

**למה קונסטנטס?** — כדי לא לתקל בטעויות הקלדה (`"ove"` במקום `"move"`) בזמן run-time.

---

### `shared/messages.py`
**תפקיד:** הגדרות dataclasses לכל סוג הודעה + parser משותף.

**בנייה של כל class:**
```python
@dataclass
class MoveMsg:
    from_cell: list[int]   # [row, col]
    to_cell: list[int]

    def to_json(self) -> dict:
        # המרה לJSON (דיקט) לשליחה ברשת
        return _base(T.MOVE, {"from": self.from_cell, "to": self.to_cell})

    @classmethod
    def from_json(cls, d: dict) -> MoveMsg:
        # המרה מJSON חזרה ל-object Python
        return cls(from_cell=d["from"], to_cell=d["to"])
```

**פונקציה עוזרת: `_base(msg_type, data)`**
- מוסיפה שדה `"type"` בפיתוח JSON כדי שהמקבל יידע איזה class להשתמש

**הודעות עיקריות:**

| Class | שדות | תפקיד |
|-------|------|-------|
| `HelloMsg` | `protocol_version` | שכנוע ראשוני |
| `LoginMsg` | `name`, `password` | בקשת התחברות |
| `LoginOkMsg` | `name`, `elo` | התחברות הצליחה |
| `PlayRequestMsg` | `mode` ("ranked" / "casual") | בקשת משחק |
| `MatchFoundMsg` | `room_id`, `opponent`, `color` | יריב נמצא |
| `RoomStateMsg` | `room_id`, `players`, `started`, `color` | מצב חדר |
| `StartMsg` | — | משחק התחיל |
| `MoveMsg` | `from_cell`, `to_cell` | בקשת הנעה |
| `JumpMsg` | `cell` | בקשת קפיצה |
| `StateUpdateMsg` | `board`, `time_ms`, `motions` | עדכון מצב |
| `MoveAckMsg` | `from_cell`, `to_cell`, `time_ms` | אישור הנעה |
| `JumpAckMsg` | `cell`, `time_ms` | אישור קפיצה |
| `GameOverMsg` | `winner`, `reason` | המשחק הסתיים |
| `ErrorMsg` | `reason` | שגיאה |

**REGISTRY - מפה מרכזית:**
```python
REGISTRY: dict[str, type] = {
    T.MOVE: MoveMsg,
    T.JUMP: JumpMsg,
    ...
}
```

**פונקציה: `parse(d: dict)`**
- קח JSON dict, בדוק את `"type"`, והחזר את ה-object הנכון
- דוגמה: `parse({"type": "move", "from": [1,2], "to": [3,4]})` → `MoveMsg(...)`

---

## 🖥️ תיקיית Server - השרת

השרת הוא אוטוריטטיבי — הוא בעלי האמת לגבי מצב המשחק, ושום קליינט לא יכול לחתור תחתיו.

### `server/main.py`
**תפקיד:** נקודת כניסה לשרת.

**פונקציה `main(port: int = DEFAULT_PORT)`**
- יוצרת `AppServer` עם הפורט הנתון
- מריצה את השרת עם `asyncio.run(AppServer(port).start())`

**שימוש:**
```bash
python -m server.main
python -m server.main --port 5555
```

---

### `server/app_server.py`
**תפקיד:** ממנהל את החיבורים וההתאמות בין שחקנים.

**Class: `AppServer`**

**משתנים:**
- `_port` — פורט ההאזנה
- `_waiting` — שחקן ראשון שמחכה (או None)
- `_waiting_done` — asyncio.Event שנעדכן כשמשחק מסתיים
- `_lock` — mutex לביטול מצבים מתחרים

**פונקציות עיקריות:**

| פונקציה | תפקיד |
|---------|-------|
| `start()` | הפעל שרת WebSocket בעל הסכם |
| `_on_connect(websocket)` | טיפול בחיבור חדש |

**זרימת `_on_connect`:**

1. **שחקן ראשון מתחבר:**
   - יצור `PlayerConnection` עם `color="w"` (לבן)
   - שמור לו ב-`_waiting`
   - שלח `RoomStateMsg(started=False)` — אתה שחקן א', חכה ליריב
   - חכה עד שמשחק מסתיים

2. **שחקן שני מתחבר:**
   - יצור `PlayerConnection` עם `color="b"` (שחור)
   - קבל את ה-white מ-`_waiting`
   - שלח לשניהם `RoomStateMsg(started=True, color=...)`
   - יוצר `GameSession` — משחק מוקצה ומתחיל

---

### `server/session/player_connection.py`
**תפקיד:** wrapper סביב WebSocket עם סוג וצבע.

**Class: `PlayerConnection`**

**תכונות:**
- `websocket` — החיבור WebSocket בפועל
- `color` — `"w"` או `"b"` (צבע הקטע)
- `name` — שם השחקן

**פונקציות:**
- `send(msg)` — שלח הודעה dataclass, המרו ל-JSON
- `send_raw(d: dict)` — שלח dict גולמי ישירות

**דוגמה:**
```python
conn = PlayerConnection(websocket, color="w", name="Alice")
await conn.send(MoveAckMsg(from_cell=[1,2], to_cell=[3,4], time_ms=1000))
```

---

### `server/session/game_session.py`
**תפקיד:** לולאת המשחק האוטוריטטיבית — משחק זה.

**Class: `GameSession`**

**משתנים:**
- `_players` — מילון `{"w": white_conn, "b": black_conn}`
- `_game` — ה-Game instance מ-logic/ (אחריות אמיתית)
- `_bus` — EventBus להודעות משחק
- `_event_source` — זרם אירועים מהלוח
- `_game_over_sent` — הגנה מפני שליחת GAME_OVER פעמיים

**פונקציות עיקריות:**

| פונקציה | תפקיד |
|---------|-------|
| `run()` | הפעל את המשחק (entry point) |
| `_tick_loop()` | לולאת זמן: advance_time, broadcast STATE_UPDATE |
| `_receive_loop(color)` | השמע הודעות מ-שחקן (MOVE / JUMP) |
| `_handle(color, msg)` | טיפול בהודעה |
| `_broadcast(msg)` | שלח הודעה לשני השחקנים |

**טיק חשוב: `_tick_loop()`**

כל 50 אלפיות:
1. קדם את `game.current_time`
2. עדכן את ה-EventBus
3. בנה `StateUpdateMsg` עם:
   - לוח עדכני
   - זמן
   - motions (הנעות, קפיצות, קרירויות)
4. שלח לשני השחקנים

אם `game.game_over`:
- שלח `GameOverMsg` עם הזוכה

**טיק חשוב: `_receive_loop(color)`**

כל הודעה שמגיעה מ-שחקן:
1. Parse את ה-JSON ל-dataclass
2. בדוק שהקטע שלו (`_game.get_piece_at(from_cell)`)
3. אם `MoveMsg` — קרא `apply_move()` מ-serializer
4. אם זה הצליח — שלח `MoveAckMsg`
5. אחרת — שלח `ErrorMsg`

---

### `server/protocol/serializer.py`
**תפקיד:** bridge בין wire-protocol לבין logic-layer objects.

**פונקציות עיקריות:**

| פונקציה | קלט | פלט | תפקיד |
|---------|-----|-----|-------|
| `board_to_json(game)` | Game | `list[list[...]]` | המרו לוח ל-JSON |
| `motions_to_json(game)` | Game | `{"moves": [...], "jumps": [...]}` | המרו תנועות ל-JSON |
| `cooldowns_to_json(game)` | Game | `[{"key": ..., "rest_type": ...}]` | המרו קרירויות ל-JSON |
| `apply_move(msg, game)` | MoveMsg, Game | bool | בצע הנעה בלוח |
| `apply_jump(msg, game)` | JumpMsg, Game | bool | בצע קפיצה בלוח |

**פונקציה: `board_to_json(game)`**
```python
# לכל תא בלוח:
{
    "k": piece.sprite_key,  # "wR", "bK", וכו'
    "s": piece.state_name,  # "idle", "moving", "long_rest"
    "cd_finish": cooldown_finish_time  # זמן סיום קרירות
}
```

**פונקציה: `motions_to_json(game)`**
- תנועות: `origin`, `destination`, `actual_dest`, `start_time`, `finish_time`
- קפיצות: `cell`, `finish_time`
- בדוק את `game.active_moves()` ו-`game.active_jumps()`

**פונקציה: `apply_move(msg, game)`**
1. הוצא את הקטע מ-`from_cell`
2. קרא `game.request_move(piece, from_cell, to_cell)`
3. החזר True אם קיבלנו

זה אומר: השרת מביא את הלוגיקה מ-logic/ ומבצע את הפעולה בעצמו.

---

### `server/logging/server_logger.py`
**תפקיד:** logging פשוט עם timestamp.

**פונקציה: `log(msg: str)`**
- הדפיס `[HH:MM:SS] msg`
- השתמשו בכל מקום בשרת לדיבוגים

---

## 🎯 תיקיית Client - הקליינט

הקליינט משדר את המשחק אבל אינו אוטוריטטיבי — השרת תמיד צודק.

### `client/main.py`
**תפקיד:** נקודת כניסה הקליינט.

**פונקציה: `main(host: str = None, port: int = None, name: str = "Player")`**
- אם `host` ניתן → משחק ברשת (`GameClientApp`)
- אחרת → משחק מקומי (`GraphicsApp` בלבד)

**שימוש:**
```bash
# משחק מקומי (offline)
python -m client.main

# משחק ברשת (online)
python -m client.main --host 127.0.0.1 --port 5555 --name Alice
```

---

### `client/game_client_app.py`
**תפקיד:** לולאת הקליינט לברשת — שילוב בין רשת וגרפיקה.

**Class: `GameClientApp`**

**משתנים:**
- `_ws` — WsClient (קשר אסינכרוני ברחוק)
- `_connecting_view` — מסך המתנה
- `_game_view` — מסך המשחק
- `_window` — WindowManager (cv2)
- `_color` — `"w"` או `"b"` (צבעך)
- `_white_name`, `_black_name` — שמות השחקנים

**זרימת `run()`:**

1. **חיבור:**
   - הפעל את `WsClient` (asyncio thread בידוד)
   - שלח `LoginMsg`
   - הצג את ConnectingView

2. **לולאה כל frame:**
   - ברוק את `inbound` queue (הודעות מן השרת)
   - טיפול בהודעות (`_handle_server_message`)
   - טיפול באירועי משתמש (click, resize)
   - render frame

3. **הודעה: RoomStateMsg(started=True)**
   - חיל ל-GameView
   - התחל משחק

**פונקציה: `_handle_server_message(msg)`**

| סוג הודעה | טיפול |
|-----------|-------|
| `RoomStateMsg(started=True)` | מורה ל-GameView, עדכן שמות |
| כללי | העבר ל-view נוכחי |

**פונקציה: `_dispatch_event(event)`**
- טיפול בקליקים, resize, וכו'
- העבר ל-view נוכחי

**חשוב:** הקליינט מעביר את ה-WsClient ל-GameView כדי שיוכל לשלוח פעולות.

---

### `client/network/ws_client.py`
**תפקיד:** הנהל חיבור WebSocket באופן אסינכרוני בחוט שונה.

**Class: `WsClient`**

**מבנה:**
- asyncio loop בחוט daemon
- שתי queues: `inbound` (קבל), `_outbound` (שלח)

**זרימה:**

```
קליינט (main thread)              WsClient (daemon thread)
    │                                    │
    ├─→ client.send(msg)  ───→  _outbound queue
    │                                    │
    │                            ┌───────┴─────┐
    │                            │             │
    │                      _send_loop    _receive_loop
    │                            │             │
    └─← inbound.get()  ←──────────── parse JSON ←── ws
```

**פונקציות:**

| פונקציה | תפקיד |
|---------|-------|
| `start()` | הפעל asyncio loop בחוט daemon |
| `send(msg)` | הוסף msg ל-outbound queue (thread-safe) |
| `_run()` | יצור asyncio loop וקשור להודעות |
| `_connect()` | התחבר ל-WebSocket |
| `_receive_loop(ws)` | השמע הודעות, parse, הוסף ל-inbound |
| `_send_loop(ws)` | שאב מ-outbound, שלח ל-WebSocket |
| `_flush_pending_outbound()` | נקה הודעות שנשלחו לפני החיבור |

**משתנים:**
- `connected` — האם מחובר?
- `error` — בעיה אחרונה?
- `inbound` — queue.Queue של הודעות מפורסמות

**דוגמה:**
```python
client = WsClient("ws://127.0.0.1:5555")
client.start()
client.send(LoginMsg(name="Alice", password=""))

# בלולאת הקליינט:
while not client.inbound.empty():
    msg = client.inbound.get_nowait()
    print(f"Got: {msg}")
```

---

### `client/network/piece_vm.py`
**תפקיד:** מודל הקטע מצד הקליינט (לא תלוי logic/).

**Class: `PieceVM`**

**תכונות:**
- `sprite_key` — `"wR"`, `"bK"`, וכו' (מזהה ספרייט)
- `state_name` — `"idle"`, `"moving"`, `"long_rest"`, וכו'

**הערה:** זו רק תיבה מידע — אין logic כאן, רק מה שהמרנדר צריך.

---

### `client/network/board_mirror.py`
**תפקיד:** שיקוף צד-קליינט של לוח השרת עם אנימציות.

**Class: `BoardMirror`**

**משתנים:**
- `current_time` — זמן משחק
- `game_over` — האם הסתיים?
- `_grid` — לוח 8x8 עם PieceVM
- `_registry` — bucket של PieceVMs (יציבות על פני עדכונים)
- `_move_vms` — הנעות פעילות
- `_jump_vms` — קפיצות פעילות
- `_cd_vms` — קרירויות פעילות

**טריק חשוב: יציבות**

בכל עדכון, מתבצעת scan של הלוח. לכל קטע מסוג `"wR"`, עושים indexing בדלי:
```python
vms = self._registry.setdefault("wR", [])
vms[0]  # הראשון wR
vms[1]  # השני wR וכו'
```

זה מבטיח שאותו PieceVM object נשמר על פני עדכונים, כלומר:
- ה-render שם יכול לשמור state
- אנימציות לא קופצות

**פונקציות עיקריות:**

| פונקציה | תפקיד |
|---------|-------|
| `apply_state_update(board, time_ms, motions)` | עדכן לוח ותנועות מהשרת |
| `snapshot()` | החזר עותק של הלוח הנוכחי |
| `active_moves()` | החזר רשימת הנעות מחוייות |
| `active_jumps()` | החזר רשימת קפיצות מחוייות |
| `cooldown_progress(piece_vm)` | קבל %(0..1) של קרירות |
| `get_piece_at(cell)` | החזר את הקטע בתא או None |
| `is_inside(cell)` | בדוק אם התא בתוך הלוח |

**Motion View Models:**

| Class | תפקיד |
|-------|-------|
| `MoveMotionVM` | תנועה: origin, destination, actual_destination, זמנים |
| `JumpMotionVM` | קפיצה: cell, finish_time |
| `CooldownVM` | קרירות: piece, rest_type, זמנים |

---

