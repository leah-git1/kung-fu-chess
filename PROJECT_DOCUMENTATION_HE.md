# 📚 Kung-Fu Chess - תיעוד טכני מלא

## 🗂️ חלק 1 – מבנה הפרויקט

### 📁 מבנה התיקיות

```
kung-fu-chess/
│
├── .git/                         ← תיקיית גיט עם היסטוריית השינויים
├── .pytest_cache/               ← קובצי מטמון של PyTest (יחידות בדיקה)
│
├── assets/                       ← קבצי מדיה (תמונות) של המשחק
│   ├── gameplay_1.png           ← צילום מסך של משחק בשלב 1
│   ├── gameplay_2.png           ← צילום מסך של משחק בשלב 2
│   ├── gameplay_cooldown.png    ← צילום מסך של זמן קרירות
│   ├── game_over.png            ← צילום מסך של מסך סיום
│   └── start_screen.png         ← צילום מסך של מסך התחלה
│
├── client/                       ← יישום הקליינט - כל מה שמוצג למשתמש
│   ├── auth/                    ← אימות משתמש בצד הקליינט
│   │   ├── shell_login.py       ← ממשק קו פקודה להתחברות עם סיסמה
│   │   ├── __init__.py          ← איניציאליזציה של המודול
│   │   └── __pycache__/         ← קבצי מטמון של Python
│   │
│   ├── game_client_app.py       ← לולאת המשחק הראשית למשחק ברשת
│   │
│   ├── graphics/                ← שכבות הגרפיקה והצגת המשחק
│   │   ├── __init__.py
│   │   ├── __pycache__/
│   │   ├── app.py               ← אפליקציית גרפיקה למשחק מקומי
│   │   ├── board_renderer.py    ← מרנדר של לוח המשחק
│   │   ├── connecting_renderer.py ← מרנדר למסך החיבור
│   │   ├── game_renderer.py     ← מרנדר ראשי שמתאם את כל הגרפיקה
│   │   ├── gfx_config.py        ← הגדרות קבועות של גרפיקה
│   │   ├── img.py               ← מחלקה לניהול תמונות (wrapper סביב OpenCV)
│   │   ├── img_provider.py      ← מחלקה ליצירת תמונות וחלונות
│   │   ├── input_adapter.py     ← מתאם קלט מהמשתמש
│   │   ├── layout.py            ← מחלקה לניהול פריסת אלמנטים על המסך
│   │   ├── observers/           ← מחלקות שמאזינות לאירועי משחק
│   │   │   ├── moves_log.py     ← רישום תנועות של קטעים
│   │   │   └── score_board.py   ← לוח ניקוד
│   │   ├── panels/              ← פנלים (חלונות צפים) בגרפיקה
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__/
│   │   │   ├── game_over_panel.py ← פנל הצגת סיום המשחק
│   │   │   ├── panel_action.py  ← enum של פעולות פנלים
│   │   │   ├── player_names_panel.py ← פנל הצגת שמות שחקנים
│   │   │   ├── start_game_panel.py ← פנל התחלת המשחק
│   │   │   └── winning_screen_panel.py ← פנל הצגת מסך ניצחון
│   │   ├── piece_renderer.py    ← מרנדר של קטעי השחמט
│   │   ├── spritesheet.py       ← ניהול ספרייטים (תמונות קטעים)
│   │   └── utils/               ← כלי עזר לגרפיקה
│   │       ├── __init__.py
│   │       └── __pycache__/
│   │
│   ├── log_utils/               ← כלי עזר ללוגים בקליינט
│   │
│   ├── main.py                  ← נקודת כניסה ראשית לקליינט
│   │
│   ├── network/                 ← שכבה לניהול רשת ותקשורת
│   │   ├── __init__.py
│   │   ├── __pycache__/
│   │   ├── board_mirror.py      ← שיקוף מצב הלוח בצד הקליינט
│   │   ├── piece_vm.py          ← מחלקה לניהול קטעים בצד הקליינט
│   │   └── ws_client.py         ← לקוח WebSocket לתקשורת עם השרת
│   │
│   ├── tests/                   ← בדיקות יחידה לקליינט
│   │
│   ├── views/                   ← ניהול מסכים והצגתם
│   │   ├── __init__.py
│   │   ├── __pycache__/
│   │   ├── base_view.py         ← ממשק בסיס לכל המסכים
│   │   ├── connecting_view.py   ← מסך חיבור לשרת
│   │   ├── game_view.py         ← מסך המשחק הראשי
│   │   ├── view_action.py       ← enum של פעולות מעבר בין מסכים
│   │   └── view_manager.py      ← מנהל המסכים הראשי
│   │
│   ├── __init__.py              ← איניציאליזציה של המודול
│   └── __pycache__/             ← קבצי מטמון של Python
│
├── logs/                        ← קבצי לוגים של הפרויקט
│   ├── client.log               ← לוג של הקליינט
│   └── server.log               ← לוג של השרת
│
├── logic/                       ← מנוע המשחק - הלוגיקה הבסיסית
│   ├── .pytest_cache/           ← קבצי מטמון של PyTest
│   │
│   ├── board/                   ← ייצוג וניהול של לוח המשחק
│   │   ├── __init__.py
│   │   ├── __pycache__/
│   │   ├── board.py             ← מחלקת Board - לוח המשחק עצמו
│   │   ├── board_parser.py      ← מפענח לוח מקובץ טקסט
│   │   └── piece.py             ← מחלקה לייצוג קטע שחמט
│   │
│   ├── commands/                ← פקודות שניתן להריץ על המשחק
│   │   ├── __init__.py
│   │   └── __pycache__/
│   │
│   ├── config.py                ← הגדרות קבועות של הלוגיקה
│   │
│   ├── controller/              ← בקרת קלט וניהול אינטראקציה
│   │   ├── __init__.py
│   │   ├── __pycache__/
│   │   ├── board_mapper.py      ← מיפוי קואורדינטות מסך לתאים בלוח
│   │   └── input_controller.py  ← בקר קלט מהמשתמש
│   │
│   ├── errors/                  ← מחלקות שגיאה של הלוגיקה
│   │   ├── __init__.py
│   │   └── __pycache__/
│   │
│   ├── events/                  ← מערכת אירועים Pub/Sub
│   │   ├── __init__.py
│   │   ├── __pycache__/
│   │   ├── event_bus.py         ← האוטובוס הראשי של האירועים
│   │   ├── game_event_source.py ← מקור אירועי משחק
│   │   └── game_events.py       ← מחלקות אירועים של המשחק
│   │
│   ├── game/                    ← ניהול משחק ומצבו
│   │   ├── __init__.py
│   │   ├── __pycache__/
│   │   ├── arbiter.py           ← "שופט" המשחק - פותר סכסוכים
│   │   ├── game.py              ← מחלקת Game - ניהול משחק שלם
│   │   ├── game_builder.py      ← בונה משחקים
│   │   └── game_clock.py        ← שעון המשחק
│   │
│   ├── main.py                  ← נקודת כניסה ללוגיקה (לא בשימוש נרחב)
│   │
│   ├── realtime/                ← לוגיקה בזמן אמת (אנימציות, תנועות)
│   │   ├── __init__.py
│   │   ├── __pycache__/
│   │   ├── motion.py            ← מחלקה לייצוג תנועה של קטע
│   │   └── motion_orchestrator.py ← מתזמר התנועות של הקטעים
│   │
│   ├── rules/                   ← חוקי המשחק ובדיקות חוקיות
│   │   ├── __init__.py
│   │   ├── __pycache__/
│   │   ├── move_rules.py        ← חוקי תנועה של כלי השחמט
│   │   ├── piece_rules.py       ← חוקים ספציפיים לכל כלי
│   │   └── rule_validator.py    ← אימות חוקיות של מהלכים
│   │
│   ├── tests/                   ← בדיקות יחידה ללוגיקה
│   │
│   ├── texttests/               ← בדיקות טקסטואליות
│   │
│   ├── utils.py                 ← כלי עזר שונים ללוגיקה
│   │
│   ├── __init__.py              ← איניציאליזציה של המודול
│   └── __pycache__/             ← קבצי מטמון של Python
│
├── README.md                    ← קובץ תיעוד ראשי (באנגלית)
├── requirements.txt             ← תלותיות Python (חבילות נדרשות)
│
├── server/                      ← יישום השרת - בעל הסמכות על המשחק
│   ├── app_server.py            ← השרת הראשי שמקבל חיבורים
│   │
│   ├── auth/                    ← אימות משתמשים בצד השרת
│   │   ├── __init__.py
│   │   ├── __pycache__/
│   │   ├── auth_handler.py      ← מנהל אימות על WebSocket
│   │   └── auth_service.py      ← שירות אימות עם bcrypt
│   │
│   ├── db/                      ← מסד נתונים וניהול משתמשים
│   │   ├── __init__.py
│   │   ├── __pycache__/
│   │   ├── database.py          ← חיבור ל-SQLite ופעולות בסיסיות
│   │   └── user_repository.py   ← ממשק גישה למשתמשים
│   │
│   ├── errors.py                ← שגיאות מיוחדות של השרת
│   │
│   ├── logging/                 ← מערכת לוגים של השרת
│   │   ├── __init__.py
│   │   └── server_logger.py     ← מחלקה ליצירת לוגים עם timestamp
│   │
│   ├── main.py                  ← נקודת כניסה ראשית לשרת
│   │
│   ├── matchmaker.py            ← ניהול התאמת שחקנים
│   │
│   ├── protocol/                ← פרוטוקול תקשורת וסריאליזציה
│   │   ├── __init__.py
│   │   ├── __pycache__/
│   │   └── serializer.py        ← ממיר בין לוגיקה לפורמט רשת
│   │
│   ├── rating/                  ← חישוב ועדכון דירוגים ELO
│   │   ├── __init__.py
│   │   ├── __pycache__/
│   │   ├── elo.py               ← אלגוריתם חישוב ELO
│   │   └── rating_service.py    ← שירות עדכון דירוגים לאחר משחק
│   │
│   ├── room_manager.py          ← ניהול חדרים ומשחקים
│   │
│   ├── session/                 ← ניהול סשנים ומשחקים פעילים
│   │   ├── __init__.py
│   │   ├── __pycache__/
│   │   ├── game_session.py      ← סשן משחק - לולאת המשחק האוטוריטטיבית
│   │   └── player_connection.py ← חיבור WebSocket של שחקן
│   │
│   ├── tests/                   ← בדיקות יחידה לשרת
│   │
│   ├── __init__.py              ← איניציאליזציה של המודול
│   └── __pycache__/             ← קבצי מטמון של Python
│
└── shared/                      ← קבצים משותפים לשרת ולקליינט
    ├── constants.py             ← קבועים משותפים (זמנים, פורטים)
    ├── enums.py                 ← enumerations משותפות
    ├── messages.py              ← מחלקות הודעות (dataclasses)
    ├── message_types.py         ← קבועי סוגי הודעות
    ├── tests/                   ← בדיקות יחידה למודול המשותף
    ├── __init__.py              ← איניציאליזציה של המודול
    └── __pycache__/             ← קבצי מטמון של Python
```

## 🏗️ חלק 2 – ארכיטקטורה

### 🔍 סקירה כללית

הפרויקט בנוי בארכיטקטורת **Client-Server** עם סמכות מלאה לשרת (authoritative server). המשחק מחולק ל-3 שכבות עיקריות:

1. **Client** - יישום עשיר המתמחה בהצגת UI ובקלט משתמש
2. **Server** - סמכות המשחק, אימות, ומשחק בזמן אמת
3. **Shared** - פרוטוקול תקשורת וקבועים משותפים

### 📦 שכבות המערכת

#### **שכבה 1: Logic (מנוע המשחק)**
- **תפקיד:** הלוגיקה הבסיסית של המשחק ללא תלות ברשת או גרפיקה
- **מחלקות חשובות:** `Game`, `Board`, `Piece`, `Arbiter`
- **קבצים:** `logic/game/game.py`, `logic/board/board.py`
- **סביבה:** פועל גם בשרת וגם בקליינט (השלכה מקומית)

#### **שכבה 2: Shared (פרוטוקול)**
- **תפקיד:** הגדרת השפה המשותפת בין שרת לקליינט
- **מחלקות חשובות:** כל ה-dataclasses ב-`messages.py`
- **קבצים:** `shared/messages.py`, `shared/message_types.py`
- **סביבה:** מיובא בשני הצדדים

#### **שכבה 3: Server (הסמכות)**
- **תפקיד:** בעל האמת על מצב המשחק, אימות, שידור עדכונים
- **תת-שכבות:**
  - **Auth:** אימות משתמשים עם bcrypt
  - **DB:** ניהול SQLite עם משתמשים ודירוגים
  - **Rating:** חישוב ELO לאחר משחקים
  - **Session:** ניהול משחקים חיים
- **קבצים:** `server/session/game_session.py`, `server/auth/`

#### **שכבה 4: Client (יישום)**
- **תפקיד:** הצגת המשחק, אנימציות, קלט משתמש
- **תת-שכבות:**
  - **Network:** WebSocket בתהליך רקע (daemon thread)
  - **Views:** ניהול מסכים ומעברים
  - **Graphics:** ציור ואנימציות עם OpenCV
  - **Observers:** מאזינים לאירועי Pub/Sub (UI-only)

### 🔗 כיוון התלותיות

```
Graphics ← Views ← Network ← Client Main
     ↑          ↖                  ↑
Pub/Sub       EventBus          Shared
     ↓                           ↓   ↓
Observers                      Server ← Logic
                                    ↑   ↑
                                  Auth  DB  Rating
```

**חוק התלותיות:**
- **קליינט תלוי ב-Shared** ← אבל לא בכיוון ההפוך
- **שרת תלוי ב-Logic וב-Shared** ← השילוב של שניהם
- **Shared עצמאי לחלוטין** ← לא תלוי באף שכבה אחרת
- **Observers תלויים ב-Pub/Sub** ← רק בצד הקליינט

### 🎯 עקרונות עיצוב

#### 1. **Single Responsibility Principle (SRP)**
כל קובץ אחראי לדבר אחד בלבד:
- `database.py` - רק SQLite CRUD
- `serializer.py` - רק המרה בין פורמטים
- `ws_client.py` - רק WebSocket bridge

#### 2. **Dependency Inversion Principle (DIP)**
המודול `shared` הוא abstract ביותר - הוא לא יודע על שרת או קליינט. שניהם תלויים בו.

#### 3. **Separation of Concerns (SoC)**
- **לוגיקה ≠ רשת** - Game לא יודע על WebSocket
- **אימות ≠ משחק** - Auth נפרד מ-GameSession
- **גרפיקה ≠ קלט** - Renderer לא מטפל בקליקים

#### 4. **Immutability של הודעות**
כל הודעת `shared/messages.py` היא dataclass עם `to_json()` ו-`from_json()` - אפשר לשלוח על הרשת בלי לשנות.

#### 5. **Pub/Sub ל-UI בלבד**
EventBus פועל רק בצד הקליינט לעדכוני UI. לא עובר ברשת - מטעמי ביצועים וסמכות.

### 🧭 בעלות על אובייקטים

#### **מי יוצר?**
1. **AppServer** ← יוצר `PlayerConnection` ו-`GameSession`
2. **GameSession** ← יוצר `Game` (מהלוגיקה)
3. **GameClientApp** ← יוצר `WsClient`, `ViewManager`, `GameView`
4. **GameView** ← יוצר `Game` (מקומי), `GameRenderer`

#### **מי בעלים?**
1. **GameSession** ← בעל `Game` ו-`PlayerConnection`×2
2. **GameRenderer** ← בעל `EventBus` וכל ה-renderers
3. **ViewManager** ← בעל `BaseView` הנוכחי
4. **WsClient** ← בעל `inbound/outbound` queues

#### **מי משתמש?**
1. **GameView** ← משתמש ב-`WsClient` לשליחת הודעות
2. **GameRenderer** ← משתמש ב-`EventBus` להאזנה
3. **BoardMirror** ← משתמש ב-PieceVM ליציבות אובייקטים
4. **Serializer** ← משתמש ב-`Game` object להמרה ל-JSON

### 🔄 זרימת מידע

```
משתמש ← קליק ← GameView.handle_click() 
                ↓
           send(MoveMsg) ← WsClient.send() 
                ↓
           WebSocket → Server
                ↓
       GameSession._receive_loop() 
                ↓
       _handle() ← apply_move() 
                ↓
       Game.advance_time() + event 
                ↓
       _broadcast(MoveAckMsg) 
                ↓
       WebSocket ← לקליינטים
                ↓
       WsClient.inbound queue 
                ↓
       GameView.handle_server_message() 
                ↓
       Game.apply_move() (מקומי) 
                ↓
       GameEventSource.poll() 
                ↓
       publish(PieceMovedEvent) 
                ↓
       EventBus → MovesLog._on_piece_moved() 
                ↓
       GameRenderer.render_frame() 
                ↓
       Canvas ← מסך
```

### 🧵 מודל Threading

#### **בשרת:**
- **Thread 1:** Main thread עם `asyncio` event loop
- **Threads N:** חוטים לכל `GameSession` (מתוך `asyncio.gather`)
- **אין blocking I/O** ← הכל אסינכרוני עם WebSockets

#### **בקליינט:**
- **Thread 1:** Main thread עם CV2 render loop (30 FPS)
- **Thread 2:** Daemon thread עם `asyncio` ל-WebSocket
- **Bridge:** `queue.Queue` thread-safe בין החוטים

### ⚡ מודל Async

#### **בשרת:**
```python
async def _tick_loop(self):
    while not self._game_over_sent:
        await asyncio.sleep(0.050)  # 50ms
        self._game.advance_time(50)
        await self._broadcast(StateUpdateMsg(...))
```

#### **בקליינט:**
```python
async def _receive_loop(self, ws):
    async for raw in ws:  # חכה להודעות
        msg = parse(json.loads(raw))
        self.inbound.put_nowait(msg)  # thread-safe
```

**יתרונות:**
- Scale לאלפי משתמשים עם מעט חוטים
- לא חסם על I/O של רשת
- Resource-efficient

---

## 📄 חלק 3 – סקירת קבצים מלאה

בואו נעבור על כל קובץ Python בפרויקט אחד אחד:
עכשיו אמשיך לכתוב את חלק 3 - סקירת הקבצים. בואו נתחיל לקרוא את הקבצים בפועל.
### 📄 shared/messages.py

**מטרת הקובץ:**
הקובץ מכיל את כל מחלקות ההודות (dataclasses) המשמשות לתקשורת בין שרת לקליינט. כל הודעה מיוצגת כקלאס עם serialization ו-deserialization מובנים.

**מדוע קובץ זה קיים:**
נדרשת שפה משותפת בין השרת לקליינט. במקום להשתמש ב-dictionaries גולמיים עם שדות מחרוזת, הקובץ מגדיר טיפוסים עם שדות מובנים וטיפוסים כדי למנוע שגיאות זמן ריצה.

**אילו קבצים משתמשים בו:**
- כל הקובץ `ws_client.py` - משתמש ב-`parse()` ובחלק מ-`REGISTRY`
- `server/protocol/serializer.py` - ממיר בין אובייקטי לוגיקה ל-dataclasses
- `client/network/ws_client.py` - שולח ומקבל הודות
- `server/session/game_session.py` - מטפל בהודעות משחק

**אילו מודולים הוא מייבא:**
- `from __future__ import annotations` - לתמיכה בטיפוסים בגרסאות Python ישנות
- `from dataclasses import dataclass, field, asdict` - עבור dataclasses
- `from typing import Optional` - לטיפוסי אופציונליים
- `import shared.message_types as T` - קבועי סוגי הודעות

**אילו מודולים מייבאים אותו:**
- `shared` module עצמו (בקובץ `__init__.py`)
- `client.network.ws_client`
- `server.protocol.serializer`
- `server.session.game_session`

**איך הוא משתתף בפרויקט:**
קובץ זה הוא הפרוטוקול עצמו. הוא מגדיר את "החוזה" בין השרת לקליינט. כל הודעה ששולחת או מקבלת היא instance של אחת המחלקות כאן.

#### 📝 מחלקות:

**1. `_base(msg_type: str, data: dict) -> dict`**

**תפקיד:**
יצירת מבנה JSON בסיסי לכל הודעה עם שדה `type` בשביל דיספצ'ינג.

**מדוע קיים:**
פרוטוקול תקשורת צריך לדעת איזה סוג הודעה הוא מקבל. השדה `type` הוא מפתחת.

**פרמטרים:**
- `msg_type: str` - סוג ההודעה (מ-`message_types.py`)
- `data: dict` - נתוני ההודעה עצמם

**ערך מוחזר:**
`dict` עם שדה `type` וכל הנתונים

**אלגוריתם:**
```python
return {"type": msg_type, **data}
```

**פרטי מימוש חשובים:**
- השימוש ב-`**data` מפזר את כל השדות באותו רמה
- זה מבנה קבוע: `{"type": "...", "field1": ..., "field2": ...}`

**מתי נקרא:**
בכל פעם שמחלקה מופעלת ומבצעת `to_json()`

**מי קורא:**
כל מחלקת הודעה קוראת לזה ב-`to_json()` שלה

**2. `@dataclass class HelloMsg`**

**תפקיד:**
הודעת handshake התחלתית בין קליינט לשרת.

**מדוע קיים:**
נדרש גרסת פרוטוקול כדי לבדוק תאימות.

**שדות חשובים:**
- `protocol_version: int` - גרסת הפרוטוקול שהקליינט תומך בה

**מחזור חיים:**
1. נוצר על ידי הקליינט בהתחברות
2. נשלח לשרת
3. נבדק על ידי השרת
4. נהרס אחרי הבדיקה

**שיתוף פעולה:**
- `WsClient` יוצר אותו
- `AppServer` מטפל בו

**3. `@dataclass class LoginMsg`**

**תפקיד:**
בקשה להתחברות עם שם משתמש וסיסמה.

**מדוע קיים:**
לבצע אימות משתמש.

**שדות חשובים:**
- `name: str` - שם המשתמש
- `password: str` - הסיסמה (לא מוצפנת! בשילוב עם HTTPS)
- `register: bool = False` - אם זו בקשה להרשמה או התחברות

**פונקציה `to_json()`:**

**מטרה:**
להמיר את ה-dataclass ל-dict לתקשורת ברשת.

**פרמטרים:**
אין (מתייחס ל-self)

**ערך מוחזר:**
`dict` עם סוג ההודעה וכל השדות

**אלגוריתם:**
```python
return _base(T.LOGIN, {
    "name": self.name,
    "password": self.password, 
    "register": self.register
})
```

**פרטי מימוש חשובים:**
- הסיסמה נשלחת כטקסט גולמי (צריך HTTPS)
- השדה `register` הוא אופציונלי עם ברירת מחדל `False`

**מתי נקרא:**
כשהקליינט רוצה להתחבר לשרת

**מי קורא:**
`client.auth.shell_login.py` או UI התחברות

**4. `@classmethod from_json(cls, d: dict) -> LoginMsg`**

**מטרה:**
ליצור instance של `LoginMsg` מתוך dict שקיבלנו מהרשת.

**פרמטרים:**
- `cls` - המחלקה עצמה
- `d: dict` - המילון עם הנתונים

**ערך מוחזר:**
instance חדש של `LoginMsg`

**אלגוריתם:**
```python
return cls(
    name=d["name"],
    password=d["password"],
    register=d.get("register", False)  # ברירת מחדל אם אין
)
```

**פרטי מימוש חשובים:**
- משתמש ב-`.get()` עם ברירת מחדל עבור שדות אופציונליים
- עושה type casting אוטומטי (Python dynamic typing)

**מתי נקרא:**
כשהשרת מקבל הודעת LOGIN

**מי קורא:**
הפונקציה `parse()` בקובץ זה

**5. `@dataclass class LoginOkMsg`**

**תפקיד:**
אישור התחברות מוצלח.

**מדוע קיים:**
להודיע לקליינט שהאימות הצליח ולתת לו נתונים על עצמו.

**שדות חשובים:**
- `name: str` - שם המשתמש
- `elo: int` - הדירוג הנוכחי של המשתמש

**6. `@dataclass class LoginFailMsg`**

**תפקיד:**
הודעת כישלון התחברות.

**מדוע קיים:**
להודיע לקליינט למה ההתחברות נכשלה.

**שדות חשובים:**
- `reason: str` - הסיבה לכישלון ("user not found", "wrong password", etc.)

**7. `@dataclass class PlayRequestMsg`**

**תפקיד:**
בקשה להתאמת שחקן למשחק.

**מדוע קיים:**
להכניס שחקן לתור Matchmaking.

**שדות חשובים:**
- `mode: str` - סוג המשחק: `"ranked"` (מדורג) או `"casual"` (רגיל)

**8. `@dataclass class MatchFoundMsg`**

**תפקיד:**
הודעה ששחקן מתאים נמצא.

**מדוע קיים:**
להודיע לשחקן שהוא יכול להתחיל משחק.

**שדות חשובים:**
- `room_id: str` - מזהה החדר החדש
- `opponent: str` - שם היריב
- `color: str` - הצבע של השחקן המקבל: `"w"` (לבן) או `"b"` (שחור)

**9. `@dataclass class SearchTimeoutMsg`**

**תפקיד:**
הודעה שחיפוש שחקן נכשל.

**מדוע קיים:**
כדי שהקליינט לא ימתין לנצח אם אין שחקנים מתאימים.

**שדות חשובים:**
אין (dataclass ריק)

**10. `@dataclass class RoomCreateMsg`**

**תפקיד:**
יצירת חדר פרטי.

**מדוע קיים:**
למשחקים מוזמנים עם חברים.

**שדות חשובים:**
- `room_id: str` - מזהה החדר שנוצר

**11. `@dataclass class RoomJoinMsg`**

**תפקיד:**
הצטרפות לחדר קיים.

**מדוע קיים:**
להצטרף למשחק של חבר.

**שדות חשובים:**
- `room_id: str` - מזהה החדר להצטרף אליו

**12. `@dataclass class RoomStateMsg`**

**תפקיד:**
עדכון מצב החדר.

**מדוע קיים:**
ל��ודיע לשחקנים מי בחדר ומצב המשחק.

**שדות חשובים:**
- `room_id: str` - מזהה החדר
- `players: list[str]` - רשימת שמות שחקנים בחדר
- `started: bool` - האם המשחק התחיל
- `color: str = ""` - הצבע של המקבל (או מחרוזת ריקה לצופה)

**13. `@dataclass class RoomErrorMsg`**

**תפקיד:**
שגיאה בחדר.

**מדוע קיים:**
להודיע על שגיאות בחדר ("room full", "room not found", etc.)

**שדות חשובים:**
- `reason: str` - הסיבה לשגיאה

**14. `@dataclass class StartMsg`**

**תפקיד:**
בקשה להתחיל משחק.

**מדוע קיים:**
כאשר כל השחקנים בחדר רוצים להתחיל.

**שדות חשובים:**
אין (dataclass ריק)

**15. `@dataclass class MoveMsg`**

**תפקיד:**
בקשה להזיז קטע.

**מדוע קיים:**
המשחק מתבסס על תנועות של קטעים.

**שדות חשובים:**
- `from_cell: list[int]` - תא ההתחלה `[row, col]`
- `to_cell: list[int]` - תא היעד `[row, col]`

**16. `@dataclass class JumpMsg`**

**תפקיד:**
בקשה לקפיצה (בריחת יחידה).

**מדוע קיים:**
אחת הפעולות המיוחדות של Kung-Fu Chess.

**שדות חשובים:**
- `cell: list[int]` - התא לקפוץ אליו `[row, col]`

**17. `@dataclass class StateUpdateMsg`**

**תפקיד:**
עדכון מצב לוח מלא.

**מדוע קיים:**
השרת שולח את המצב המלא של הלוח כל 200ms.

**שדות חשובים:**
- `board: list` - ייצוג הלוח (רשימה של רשימות)
- `time_ms: int` - הזמן הנוכחי של המשחק במילישניות
- `motions: dict = None` - תנועות אקטיביות (עם ברירת מחדל)

**פונקציה `to_json()`:**

**מטרה:**
להמיר את המצב ל-JSON.

**פרמטרים:**
אין

**ערך מוחזר:**
`dict` עם כל השדות

**אלגוריתם:**
```python
return _base(T.STATE_UPDATE, {
    "board": self.board,
    "time_ms": self.time_ms,
    "motions": self.motions or {"moves": [], "jumps": []}
})
```

**פרטי מימוש חשובים:**
- אם `self.motions` הוא `None`, משתמש בערך ברירת מחדל
- מבנה ברירת המחדל: `{"moves": [], "jumps": []}`

**מתי נקרא:**
כל 200ms על ידי השרת

**מי קורא:**
`GameSession._tick_loop()`

**18. `@dataclass class MoveAckMsg`**

**תפקיד:**
אישור תנועה ששודרה ליריב.

**מדוע קיים:**
להודיע לקליינט שהתנועה שלו התבצעה בהצלחה.

**שדות חשובים:**
- `from_cell: list[int]` - תא ההתחלה
- `to_cell: list[int]` - תא היעד
- `time_ms: int` - הזמן שבו התנועה התרחשה

**19. `@dataclass class JumpAckMsg`**

**תפקיד:**
אישור קפיצה ששודרה ליריב.

**מדוע קיים:**
להודיע לקליינט שהקפיצה שלו התבצעה בהצלחה.

**שדות חשובים:**
- `cell: list[int]` - התא שאליו קפץ
- `time_ms: int` - הזמן שבו הקפיצה התרחשה

**20. `@dataclass class GameOverMsg`**

**תפקיד:**
הודעת סיום משחק.

**מדוע קיים:**
להודיע שהמשחק נגמר ולמה.

**שדות חשובים:**
- `winner: str` - הצבע המנצח: `"w"` או `"b"`
- `reason: str` - הסיבה לסיום (`"king captured"`, etc.)

**21. `@dataclass class ResignMsg`**

**תפקיד:**
הודעת כניעה.

**מדוע קיים:**
לאפשר לשחקנים לפרוש ממשחק.

**שדות חשובים:**
אין (dataclass ריק)

**22. `@dataclass class LogEventMsg`**

**תפקיד:**
הודעת אירוע ללוג.

**מדוע קיים:**
לשלוח אירועים טקסטואליים ללוג הצד לקליינט.

**שדות חשובים:**
- `text: str` - טקסט האירוע
- `time_ms: int` - זמן האירוע

**23. `@dataclass class ErrorMsg`**

**תפקיד:**
הודעת שגיאה כללית.

**מדוע קיים:**
לשלוח שגיאות שלא קשורות להודעות אחרות.

**שדות חשובים:**
- `reason: str` - הסיבה לשגיאה

**24. `@dataclass class OpponentDisconnectedMsg`**

**תפקיד:**
הודעה שהיריב התנתק.

**מדוע קיים:**
להודיע שיש זמן חסד לפני ניצחון אוטומטי.

**שדות חשובים:**
- `grace_s: int` - שניות חסד לפני ניצחון אוטומטי

#### 📝 משתנים גלובליים:

**1. `REGISTRY: dict[str, type]`**

**תפקיד:**
מילון שממפה שמות הודעות למחלקות שלהן.

**מדוע קיים:**
לאפשר deserialization דינמית: `parse()` משתמש בזה כדי לדעת איזו מחלקה ליצור.

**שדות חשובים:**
המפתחות הם ערכים מ-`message_types.py`, הערכים הם מחלקות הודעות.

**מחזור חיים:**
נוצר בעת טעינת המודול ונשאר קבוע.

**שיתוף פעולה:**
משמש על ידי `parse()`.

**2. `def parse(d: dict)`**

**תפקיד:**
לפרסר מילון JSON ולהחזיר instance של המחלקה המתאימה.

**מדוע קיים:**
זו פונקציית ה-deserialization המרכזית של הפרויקט.

**פרמטרים:**
- `d: dict` - המילון עם ההודעה (כולל שדה `"type"`)

**ערך מוחזר:**
instance של אחת ממחלקות ההודעות

**אלגוריתם:**
1. לקחת את השדה `"type"` מהמילון
2. לחפש ב-`REGISTRY` את המחלקה המתאימה
3. אם לא נמצא - להעלות `ValueError`
4. לקרוא ל-`from_json()` של המחלקה עם המילון

**פרטי מימוש חשובים:**
- משתמש ב-`.get()` עם ברירת מחדל `None` עבור שדה `"type"`
- מעלה `ValueError` עם הודעת שגיאה ברורה

**מתי נקרא:**
כל פעם שמקבלים הודעה מהרשת

**מי קורא:**
- `WsClient._receive_loop()` - כשמקבל הודעה מהשרת
- כל מקום שמבצע deserialization של הודעות

### 📄 shared/message_types.py

**מטרת הקובץ:**
הקובץ מגדיר קבועים עבור סוגי ההודעות. זה מונע שימוש במחרוזות גולמיות בקוד.

**מדוע קובץ זה קיים:**
משתמשים בקבועים כדי למנוע שגיאות הקלדה. במקום `"login"` בקוד, משתמשים ב-`T.LOGIN` וטעויות הקלדה יתגלו בעת טעינת הקובץ.

**אילו קבצים משתמשים בו:**
- `shared/messages.py` - לכל מחלקות ה-to_json()
- `server/protocol/serializer.py` - לאימות סוגי הודעות
- `client/network/ws_client.py` - לבדיקה

**אילו מודולים הוא מייבא:**
אין ייבוא

**אילו מודולים מייבאים אותו:**
- `shared/messages.py` (כ-`import shared.message_types as T`)
- כל קובץ שצריך לדעת על סוגי הודעות

**איך הוא משתתף בפרויקט:**
זה המילון המרכזי של הפרוטוקול. כל הודעה חייבת להיות מוגדרת כאן.

#### 📝 קבועים:

**קבועי Handshake:**
- `HELLO = "hello"` - הודעת התחברות ראשונית

**קבועי Auth:**
- `LOGIN = "login"` - התחברות משתמש
- `LOGIN_OK = "login_ok"` - אישור התחברות
- `LOGIN_FAIL = "login_fail"` - כישלון התחברות

**קבועי Matchmaking:**
- `PLAY_REQUEST = "play_request"` - בקשה למשחק
- `MATCH_FOUND = "match_found"` - מציאת יריב
- `SEARCH_TIMEOUT = "search_timeout"` - זמן חיפוש עבר

**קבועי Room:**
- `ROOM_CREATE = "room_create"` - יצירת חדר
- `ROOM_JOIN = "room_join"` - הצטרפות לחדר
- `ROOM_STATE = "room_state"` - עדכון מצב חדר
- `ROOM_ERROR = "room_error"` - שגיאה בחדר

**קבועי In-game:**
- `START = "start"` - התחלת משחק
- `MOVE = "move"` - בקשה לתנועה
- `JUMP = "jump"` - בקשה לקפיצה
- `STATE_UPDATE = "state_update"` - עדכון מצב לוח
- `MOVE_ACK = "move_ack"` - אישור תנועה
- `JUMP_ACK = "jump_ack"` - אישור קפיצה
- `GAME_OVER = "game_over"` - סיום משחק
- `RESIGN = "resign"` - כניעה

**קבועי Events/logging:**
- `LOG_EVENT = "log_event"` - אירוע ללוג

**קבועי Errors/connection:**
- `ERROR = "error"` - שגיאה כללית
- `OPPONENT_DISCONNECTED = "opponent_disconnected"` - יריב התנתק

### 📄 shared/constants.py

**מטרת הקובץ:**
הקובץ מכיל כל קבוע מספרי או מחרוזת שמשותף לשרת ולקליינט.

**מדוע קובץ זה קיים:**
כדי לשמור על עקביות בין השרת לקליינט (זמני אנימציה, הגדרות רשת, etc.)

**אילו קבצים משתמשים בו:**
- `server/main.py` - עבור `DEFAULT_PORT`
- `logic/config.py` - יכול להשתמש בקבועי משחק
- `client/graphics/gfx_config.py` - עבור זמני אנימציה

**אילו מודולים הוא מייבא:**
אין ייבוא

**אילו מודולים מייבאים אותו:**
כל קובץ שצריך קבועים משותפים

**איך הוא משתתף בפרויקט:**
מגדיר את "הפיזיקה" המשותפת של המשחק.

#### 📝 מחלקות קבועים:

**1. `class GameOverReason:`**

**תפקיד:**
מכיל מחרוזות הסיבה לסיום משחק.

**מדוע קיים:**
כדי למנוע שגיאות הקלדה בהודעות `GameOverMsg`.

**קבועים:**
- `KING_CAPTURED = "king captured"` - המלך נתפס
- `OPPONENT_DISCONNECTED = "opponent disconnected"` - יריב התנתק

**2. `class RoomId:`**

**תפקיד:**
מכיל מזהה חדרים סטנדרטיים.

**מדוע קיים:**
למקרים של חדרים מיוחדים (כמו לובי ראשי).

**קבועים:**
- `MAIN = "main"` - החדר הראשי (לא בשימוש)

**קבועים גלובליים:**

**3. `ROOM_ID_LENGTH = 4`**

**מטרה:**
אורך קוד החדר שנוצר (למשל "A3F7").

**מדוע קיים:**
לאחידות בהפקת קודי חדר.

**4. `DEFAULT_PORT = 5555`**

**מטרה:**
פורט ברירת המחדל של השרת.

**מדוע קיים:**
כדי שלקליינט ושרת ידברו באותו פורט.

**5. `PROTOCOL_VERSION = 1`**

**מטרה:**
גרסת הפרוטוקול הנוכחית.

**מדוע קיים:**
לבדיקת תאימות בין גרסאות שונות.

**6. `TICK_RATE_MS = 50`**

**מטרה:**
הריענון של השרת - כל כמה מילישניות השרת מתקדם בזמן המשחק.

**מדוע קיים:**
לקצב קבוע של עדכוני משחק.

**7. `STATE_UPDATE_INTERVAL_MS = 200`**

**מטרה:**
כל כמה מילישניות השרת שולח עדכון מצב מלא לקליינטים.

**מדוע קיים:**
לאזן בין תקורה לרשת לבין עדכניות.

**8. `ELO_RANGE = 100`**

**מטרה:**
טווח דירוג מקסימלי להתאמה מדורגת.

**מדוע קיים:**
להתאים שחקנים ברמות דומות.

**9. `MATCH_TIMEOUT_S = 60`**

**מטרה:**
מספר שניות לחכות לפני שביטול חיפוש שחקן.

**מדוע קיים:**
כדי לא להשאיר שחקנים בתור לנצח.

**10. `PLAY_REQUEST_TIMEOUT_S = 300`**

**מטרה:**
מספר שניות לחכות לבקשת משחק אחרי התחברות.

**מדוע קיים:**
ניקוי אוטומטי של שחקנים לא פעילים.

**11. `ELO_K_FACTOR = 32`**

**מטרה:**
פקטור K באלגוריתם ELO - כמה דירוג משתנה לאחר משחק.

**מדוע קיים:**
לחישוב דירוגים מדויק.

**12. `ELO_SCALE = 400`**

**מטרה:**
פקטור קנה מידה באלגוריתם ELO.

**מדוע קיים:**
חלק סטנדרטי מנוסחת ELO.

**13. `ELO_DEFAULT = 1200`**

**מטרה:**
דירוג התחלתי של שחקן חדש.

**מדוע קיים:**
נקודת התחלה הוגנת.

**14. `DISCONNECT_GRACE_S = 20`**

**מטרה:**
מספר שניות חסד לפני ניצחון אוטומטי כששחקן מתנתק.

**מדוע קיים:**
לתת לשחקן סיכוי להתחבר מחדש.

**15. `MOVE_DURATION_PER_CELL = 600`**

**מטרה:**
מספר מילישניות לכל תא בלוח שאנימציית תנועה נמשכת.

**מדוע קיים:**
לקבוע את קצב האנימציה של תנועות.

**16. `JUMP_DURATION = 1000`**

**מטרה:**
משך אנימציית קפיצה במילישניות.

**מדוע קיים:**
לקבוע את קצב האנימציה של קפיצות.

**17. `LONG_REST_DURATION = 2000`**

**מטרה:**
משך זמן הקרירות אחרי תנועה במילישניות.

**מדוע קיים:**
לקבוע את קצב המשחק.

**18. `SHORT_REST_DURATION = 1000`**

**מטרה:**
משך זמן הקרירות אחרי קפיצה במילישניות.

**מדוע קיים:**
לקבוע את קצב המשחק.

### 📄 shared/enums.py

בואו נסתכל על הקובץ:
### 📄 shared/enums.py

**מטרת הקובץ:**
הקובץ מכיל enumerations שמשמשים בשרת ובקליינט.

**מדוע קובץ זה קיים:**
Enums מונעים שגיאות של הקלדת מחרוזות ומספקים type safety.

**אילו קבצים משתמשים בו:**
- `logic/game/game.py` - עבור `Color`
- `server/matchmaker.py` - עבור `PlayMode`
- `logic/events/game_events.py` - עבור `RestType`

**אילו מודולים הוא מייבא:**
- `from enum import Enum` - מהספרייה הסטנדרטית

**אילו מודולים מייבאים אותו:**
כל קובץ שצריך enumerations

**איך הוא משתתף בפרויקט:**
מספק טיפוסים מאובטחים במקום מחרוזות גולמיות.

#### 📝 Enumerations:

**1. `class Color(Enum):`**

**תפקיד:**
ייצוג של צבעי השחקנים.

**מדוע קיים:**
למנוע שימוש במחרוזות כמו `"w"` ו-`"b"` ישירות בקוד.

**ערכים:**
- `WHITE = "w"` - שחקן לבן
- `BLACK = "b"` - שחקן שחור

**שימוש:**
```python
# נכון:
if color == Color.WHITE:
    ...

# לא נכון:
if color == "w":  # יכול להיות שגיאה הקלדה
    ...
```

**2. `class RestType(Enum):`**

**תפקיד:**
סוג זמן קרירות (cooldown).

**מדוע קיים:**
להבדיל בין זמן קרירות ארוך אחרי תנועה לבין קצר אחרי קפיצה.

**ערכים:**
- `LONG = "long"` - קרירות ארוך (אחרי תנועה)
- `SHORT = "short"` - קרירות קצר (אחרי קפיצה)

**3. `class PlayMode(Enum):`**

**תפקיד:**
סוג משחק (מדורג או רגיל).

**מדוע קיים:**
להבדיל בין משחקים שמשפיעים על דירוג לבין משחקים חברתיים.

**ערכים:**
- `RANKED = "ranked"` - משחק מדורג (משפיע על ELO)
- `CASUAL = "casual"` - משחק רגיל (לא משפיע על דירוג)

---

## 🗂️ המשך סקירת הקבצים - תיקיית Server

### 📄 server/db/database.py

בואו נסתכל על מסד הנתונים:
### 📄 server/db/database.py

**מטרת הקובץ:**
הקובץ מטפל בחיבור ל-SQLite ופעולות CRUD בסיסיות על טבלת המשתמשים.

**מדוע קובץ זה קיים:**
נדרש איחסון משתמשים, סיסמאות מוצפנות, ודירוגים. SQLite מתאים למשחק קטן כי הוא קל ואינו דורש התקנת שרת נפרד.

**אילו קבצים משתמשים בו:**
- `server/db/user_repository.py` - wrapper מסביב לפונקציות כאן
- `server/auth/auth_service.py` - עבור אימות משתמשים

**אילו מודולים הוא מייבא:**
- `import sqlite3` - ספריית SQLite הסטנדרטית
- `import os` - עבור מסלולי קבצים
- `from shared.constants import ELO_DEFAULT` - דירוג התחלתי

**אילו מודולים מייבאים אותו:**
רק `user_repository.py` (לא באופן ישיר, דרך wrapper)

**איך הוא משתתף בפרויקט:**
זה השכבה הנמוכה ביותר של גישת הנתונים. כל שאילתה למסד הנתונים עוברת דרך פונקציות כאן.

#### 📝 משתנים גלובליים:

**1. `_DB_PATH`**

**תפקיד:**
מסלול לקובץ SQLite בתיקיית ה-db.

**מדוע קיים:**
לשמור על מיקום קבוע של קובץ ה-database.

**מחזור חיים:**
קבוע לאורך ריצת השרת.

**ערך:**
`os.path.join(os.path.dirname(__file__), "users.db")` - קובץ `users.db` באותה תיקייה.

**2. `def _connect() -> sqlite3.Connection:`**

**תפקיד:**
יצירת חיבור חדש ל-SQLite עם הגדרות ברירת מחדל.

**מדוע קיים:**
לא לחזור על קוד חיבור בכל פונקציה.

**פרמטרים:**
אין

**ערך מוחזר:**
`sqlite3.Connection` מוגדר עם `row_factory=sqlite3.Row`

**אלגוריתם:**
1. `conn = sqlite3.connect(_DB_PATH)` - פתיחת חיבור
2. `conn.row_factory = sqlite3.Row` - החזר רשומות כ-`sqlite3.Row` במקום tuple
3. `return conn`

**פרטי מימוש חשובים:**
- `sqlite3.Row` מאפשר גישה לשדות בשם (`row["username"]`) ולא באינדקס
- אין pool חיבורים - כל פונקציה פותחת חיבור חדש (פשוט ל-SQLite)

**מתי נקרא:**
בכל פונקציה CRUD בקובץ

**מי קורא:**
כל שאר הפונקציות בקובץ (בתוך context manager)

**3. `def init_db() -> None:`**

**תפקיד:**
אתחול טבלת המשתמשים אם היא לא קיימת.

**מדוע קיים:**
לאפשר התקנה ראשונית של השרת ללא הגדרות ידניות.

**פרמטרים:**
אין

**ערך מוחזר:**
`None`

**אלגוריתם:**
1. פתיחת חיבור עם context manager
2. הרצת `CREATE TABLE IF NOT EXISTS` עם סכימה קבועה
3. סגירה אוטומטית של החיבור

**פרטי מימוש חשובים:**
- משתמש ב-`IF NOT EXISTS` כדי לא לגרום לשגיאה אם הטבלה קיימת
- מגדיר עמודת `user_id` כ-`AUTOINCREMENT` (מזהה אוטומטי)
- שדה `username` הוא `UNIQUE` - לא יכולות להיות שתי רשומות עם אותו שם
- שימוש ב-`ELO_DEFAULT` (1200) כדירוג ברירת מחדל

**מתי נקרא:**
בעת אתחול השרת, לפני קבלת חיבורים

**מי קורא:**
`server/main.py` ב-`main()` או `server/auth/auth_service.py` ב-`__init__`

**4. `def insert_user(username: str, password_hash: str) -> int:`**

**תפקיד:**
הוספת משתמש חדש למסד הנתונים.

**מדוע קיים:**
להרשמת משתמשים חדשים.

**פרמטרים:**
- `username: str` - שם המשתמש (חייב להיות ייחודי)
- `password_hash: str` - הסיסמה המוצפנת (עם bcrypt)

**ערך מוחזר:**
`int` - ה-`user_id` החדש שהוקצה אוטומטית

**אלגוריתם:**
1. פתיחת חיבור
2. הרצת `INSERT` עם הפרמטרים
3. החזרת `lastrowid` (ה-ID שנוצר)
4. סגירה אוטומטית

**פרטי מימוש חשובים:**
- משתמש ב-parameterized queries (`?, ?`) למניעת SQL injection
- `lastrowid` הוא תכונה של SQLite שמחזירה את ה-ID של השורה האחרונה שהוכנסה
- לא שומר את ה-password_hash ב-plain text אלא מוצפן (ב-`auth_service`)

**מתי נקרא:**
כאשר משתמש נרשם לראשונה

**מי קורא:**
`server/auth/auth_service.register()`

**5. `def fetch_user(username: str) -> sqlite3.Row | None:`**

**תפקיד:**
קבלת פרטי משתמש לפי שם משתמש.

**מדוע קיים:**
לאימות התחברות וקבלת דירוג.

**פרמטרים:**
- `username: str` - שם המשתמש לחיפוש

**ערך מוחזר:**
- `sqlite3.Row` אם המשתמש נמצא
- `None` אם המשתמש לא נמצא

**אלגוריתם:**
1. פתיחת חיבור
2. הרצת `SELECT *` עם שם משתמש
3. `fetchone()` - מקבל שורה אחת או None
4. סגירה אוטומטית

**פרטי מימוש חשובים:**
- שוב parameterized query למניעת SQL injection
- `fetchone()` במקום `fetchall()` כי אנחנו מצפים לשורה אחת או אפס
- מחזיר `sqlite3.Row` שניתן לגשת אליו בשם עמודה

**מתי נקרא:**
בעת התחברות משתמש

**מי קורא:**
`server/auth/auth_service.authenticate()`

**6. `def set_rating(username: str, rating: int) -> None:`**

**תפקיד:**
עדכון דירוג משתמש לאחר משחק.

**מדוע קיים:**
לעדכן את דירוג ה-ELO לאחר סיום משחק.

**פרמטרים:**
- `username: str` - שם המשתמש לעדכון
- `rating: int` - הדירוג החדש

**ערך מוחזר:**
`None`

**אלגוריתם:**
1. פתיחת חיבור
2. הרצת `UPDATE` עם הפרמטרים
3. סגירה אוטומטית

**פרטי מימוש חשובים:**
- משפיע רק על עמודת ה-`rating`
- לא מחזיר ערך - עדכון בלבד

**מתי נקרא:**
לאחר סיום משחק מדורג

**מי קורא:**
`server/rating/rating_service.update_ratings()`

### 📄 server/protocol/serializer.py

בואו נסתכל על הקובץ הפתוח בעורך:
### 📄 server/protocol/serializer.py

**מטרת הקובץ:**
הקובץ ממיר בין אובייקטים של שכבות הלוגיקה לבין פורמט הרשת (JSON). זה הגשר בין העולם הפנימי של המשחק לעולם החיצוני של הרשת.

**מדוע קובץ זה קיים:**
אובייקטי `Game` ו-`Piece` מורכבים מדי לשליחה ישירה ברשת. צריך להפוך אותם ל-dicts פשוטים.

**אילו קבצים משתמשים בו:**
- `server/session/game_session.py` - להמרת מצב לוח להודעות `STATE_UPDATE`
- `server/session/game_session.py` - להחלת `MoveMsg` ו-`JumpMsg` על `Game`

**אילו מודולים הוא מייבא:**
- `from __future__ import annotations` - לתמיכה בטיפוסים
- `from shared.enums import RestType` - עבור סוגי קרירות

**אילו מודולים מייבאים אותו:**
רק `server/session/game_session.py`

**איך הוא משתתף בפרויקט:**
זה ה-"מתרגם" בין השרת לקליינט. כאשר השרת צריך לשלוח את מצב הלוח, הוא קורא ל-`board_to_json()`. כאשר קליינט שולח בקשה לזוז, קוראים ל-`apply_move()`.

#### 📝 פונקציות:

**1. `def board_to_json(game) -> list:`**

**תפקיד:**
להמיר את מצב הלוח הנוכחי לרשימה של רשימות של dicts (או `None`).

**מדוע קיים:**
השרת צריך לשלוח את הלוח המלא לקליינטים.

**פרמטרים:**
- `game` - אובייקט `Game` מהלוגיקה

**ערך מוחזר:**
`list` - מטריצה 8x8 שבה כל תא הוא:
- `None` אם אין קטע
- `dict` עם מפתחות `"k"`, `"s"`, `"cd_finish"`

**אלגוריתם:**
1. יצירת מילון `cooldown_finish` שממפה ID קטע → זמן סיום קרירות
2. מעבר על כל התנועות ב-`game._arbiter._motions`
3. אם התנועה היא `CooldownMotion`, שמירת זמן הסיום
4. יצירת לוח: לכל שורה ב-`game.snapshot()`, לכל קטע בשורה:
   - אם `piece is None`: `None`
   - אחרת: dict עם:
     - `"k"`: `piece.sprite_key` (מפתח הספרייט)
     - `"s"`: `piece.state_name` (שם המצב: "idle", "move", etc.)
     - `"cd_finish"`: זמן סיום הקרירות (אם יש)

**פרטי מימוש חשובים:**
- משתמש ב-`id(m.piece)` כמפתח ב-map (ה-ID הייחודי של האובייקט)
- `game.snapshot()` מחזירה את הלוח הנוכחי כרשימת רשימות
- הפורמט מותאם ליכולות הציור של הקליינט

**מתי נקרא:**
כל 200ms על ידי `GameSession._tick_loop()`

**מי קורא:**
`GameSession._broadcast_state_update()`

**2. `def motions_to_json(game) -> dict:`**

**תפקיד:**
להמיר תנועות אקטיביות (moves ו-jumps) ל-JSON לאנימציה בצד לקליינט.

**מדוע קיים:**
הקליינט צריך לדעת איזה קטעים נעים כדי להפעיל אנימציות.

**פרמטרים:**
- `game` - אובייקט `Game`

**ערך מוחזר:**
`dict` עם מפתחות:
- `"moves"`: רשימה של dicts לתנועות
- `"jumps"`: רשימה של dicts לקפיצות

**אלגוריתם:**
1. ל-`moves`: עבור כל תנועה ב-`game.active_moves()`:
   - יצירת dict עם:
     - `"key"`: מפתח הספרייט של הקטע
     - `"origin"`: קואורדינטת המוצא
     - `"destination"`: קואורדינטת היעד המבוקש
     - `"actual_dest"`: קואורדינטת היעד האמיתי (אם שונה)
     - `"start_time"`: זמן התחלה (חישוב לאחור מ-`finish_time`)
     - `"finish_time"`: זמן סיום

2. ל-`jumps`: עבור כל קפיצה ב-`game.active_jumps()`:
   - יצירת dict עם:
     - `"key"`: מפתח הספרייט של הקטע
     - `"cell"`: התא שאליו קופצים
     - `"finish_time"`: זמן סיום הקפיצה

**פרטי מימוש חשובים:**
- `game.active_moves()` ו-`game.active_jumps()` מחזירות רק תנועות פעילות (לא הושלמו)
- `_move_duration()` מחשבת את משך התנועה לפי מרחק
- `actual_destination` חשוב לתנועות שמותרות לקטעי שחמט מסוימים (למשל פרש)

**מתי נקרא:**
בעת בניית `STATE_UPDATE` אם יש תנועות פעילות

**מי קורא:**
`GameSession` כאשר בונה `StateUpdateMsg`

**3. `def cooldowns_to_json(game) -> list:`**

**תפקיד:**
להמיר זמני קרירות אקטיביים ל-JSON להתקדמות בצד לקליינט.

**מדוע קיים:**
הקליינט צריך להראות פסי התקדמות לזמן קרירות.

**פרמטרים:**
- `game` - אובייקט `Game`

**ערך מוחזר:**
`list` של dicts, כל אחד מייצג קרירות אקטיבי

**אלגוריתם:**
1. יצירת `piece_cell` map: ID קטע → `(row, col)` מהלוח הנוכחי
2. עבור כל תנועה ב-`game._arbiter._motions`:
   - אם זו `CooldownMotion`:
     - קביעת משך לפי סוג המצב (`LONG_REST` או `SHORT_REST`)
     - חיפוש הקואורדינטה של הקטע ב-`piece_cell`
     - אם נמצא, הוספת dict עם:
       - `"key"`: מפתח הספרייט
       - `"cell"`: הקואורדינטה
       - `"rest_type"`: סוג הקרירות (`"long"` או `"short"`)
       - `"start_time"`: זמן התחלה
       - `"finish_time"`: זמן סיום

**פרטי מימוש חשובים:**
- משתמש ב-`PieceState.LONG_REST.value` ו-`PieceState.SHORT_REST.value` לזיהוי סוג הקרירות
- `config.LONG_REST_DURATION` ו-`config.SHORT_REST_DURATION` לקביעת המשך
- מייבא את המודולים בתוך הפונקציה (לא בראש הקובץ) כדי למנוע import cycles

**מתי נקרא:**
לא בשימוש כרגע - יכול לשמש לשליחת מידע נוסף לקליינט

**מי קורא:**
אין קריאות בפועל בקוד הנוכחי

**4. `def _move_duration(origin, destination) -> int:`**

**תפקיד:**
חישוב משך התנועה במילישניות לפי מרחק.

**מדוע קיים:**
תנועה של מספר תאים לוקחת יותר זמן מתנועה של תא אחד.

**פרמטרים:**
- `origin: tuple` - קואורדינטת המוצא `(row, col)`
- `destination: tuple` - קואורדינטת היעד `(row, col)`

**ערך מוחזר:**
`int` - משך במילישניות

**אלגוריתם:**
1. חישוב ההפרש המוחלט בשורות: `abs(destination[0] - origin[0])`
2. חישוב ההפרש המוחלט בעמודות: `abs(destination[1] - origin[1])`
3. לקיחת המקסימום בין שניהם (תנועה אלכסונית = תנועה אנכית/אופקית)
4. הכפלה ב-`config.MOVE_DURATION_PER_CELL` (600ms)

**פרטי מימוש חשובים:**
- `Chebyshev distance` (מרחק מלך) - המקסימום של ההפרשים
- עבור פרש (שזז ב-L shape) זה לא מדויק אך מקובל

**מתי נקרא:**
בתוך `motions_to_json()` לחישוב `start_time`

**מי קורא:**
רק `motions_to_json()`

**5. `def apply_move(msg, game) -> bool:`**

**תפקיד:**
להחיל הודעת `MoveMsg` על אובייקט `Game`.

**מדוע קיים:**
כאשר קליינט שולח בקשה לזוז, צריך לתרגם אותה לפעולה במשחק.

**פרמטרים:**
- `msg: MoveMsg` - הודעת תנועה מהקליינט
- `game: Game` - אובייקט המשחק

**ערך מוחזר:**
`bool` - `True` אם התנועה התקבלה, `False` אם נדחתה

**אלגוריתם:**
1. המרת `msg.from_cell` מ-`list[int]` ל-`tuple`
2. המרת `msg.to_cell` מ-`list[int]` ל-`tuple`
3. חיפוש הקטע בתא המוצא: `game.get_piece_at(from_cell)`
4. קריאה ל-`game.request_move()` עם הקטע והקואורדינטות
5. החזרת התוצאה

**פרטי מימוש חשובים:**
- `tuple` במקום `list` כי `game.get_piece_at()` מצפה ל-tuple
- הבדיקה אם הקטע קיים בתוך `request_move()` (עשוי להחזיר `False` אם אין קטע)
- `request_move()` מבצעת את כל בדיקות החוקיות

**מתי נקרא:**
כאשר `GameSession` מקבלת `MoveMsg` מקליינט

**מי קורא:**
`GameSession._handle()` עבור הודעות מסוג `MOVE`

**6. `def apply_jump(msg, game) -> bool:`**

**תפקיד:**
להחיל הודעת `JumpMsg` על אובייקט `Game`.

**מדוע קיים:**
כאשר קליינט שולח בקשה לקפוץ, צריך לתרגם אותה לפעולה במשחק.

**פרמטרים:**
- `msg: JumpMsg` - הודעת קפיצה מהקליינט
- `game: Game` - אובייקט המשחק

**ערך מוחזר:**
`bool` - `True` אם הקפיצה התקבלה, `False` אם נדחתה

**אלגוריתם:**
1. המרת `msg.cell` מ-`list[int]` ל-`tuple`
2. חיפוש הקטע בתא: `game.get_piece_at(cell)`
3. קריאה ל-`game.request_jump()` עם הקטע והקואורדינטה
4. החזרת התוצאה

**פרטי מימוש חשובים:**
- `request_jump()` היא פעולה מיוחדת של Kung-Fu Chess (בריחת יחידה)
- לא כל הקטעים יכולים לקפוץ (רק כאלה שתחת מתקפה)

**מתי נקרא:**
כאשר `GameSession` מקבלת `JumpMsg` מקליינט

**מי קורא:**
`GameSession._handle()` עבור הודעות מסוג `JUMP`

### 📄 server/app_server.py

בואו נסתכל על שרת האפליקציה הראשי:
### 📄 server/app_server.py

**מטרת הקובץ:**
קובץ השרת הראשי שמקבל חיבורים חדשים, מנהל חדרים, ומתאם בין שחקנים.

**מדוע קובץ זה קיים:**
נקודת הכניסה הראשית של השרת. כל חיבור חדש מתחיל כאן ומכוון לחדר, משחק או צפייה.

**אילו קבצים משתמשים בו:**
רק `server/main.py` שמפעיל אותו

**אילו מודולים הוא מייבא:**
- `asyncio`, `json`, `sys`, `os` - ספריות סטנדרטיות
- `websockets` ו-`websockets.exceptions.ConnectionClosed` - ספריית WebSocket
- קבצים מ-`shared`: הודעות, קבועים, enums
- קבצים מ-`server`: חיבורים, סשנים, אימות, matchmaking, חדרים

**אילו מודולים מייבאים אותו:**
רק `server/main.py`

**איך הוא משתתף בפרויקט:**
הוא המוח הראשי של השרת. מקבל חיבורים, מנתב שחקנים, ומנהל את מחזור החיים של המשחקים.

#### 📝 מחלקות:

**1. `class AppServer:`**

**תפקיד:**
השרת הראשי של האפליקציה. מנהל את כל החיבורים, החדרים, והמשחקים.

**מדוע קיים:**
צריך מקום מרכזי לניהול מצב השרת.

**שדות חשובים:**
- `_port: int` - הפורט עליו השרת מאזין
- `_matchmaker: Matchmaker` - מנוע התאמת שחקנים
- `_room_manager: RoomManager` - מנהל חדרים פרטיים
- `_sessions: dict[str, asyncio.Event]` - מיפוי בין שמות שחקנים לאירועי סיום
- `_session_lock: asyncio.Lock` - נעילת thread לביצועים

**מחזור חיים:**
1. נוצר על ידי `server/main.py`
2. מפעיל `start()` שרץ לנצח
3. נהרס כאשר השרת נסגר

**שיתוף פעולה:**
- `Matchmaker` - עבור התאמת שחקנים אוטומטית
- `RoomManager` - עבור חדרים פרטיים
- `PlayerConnection` - חיבורי שחקנים
- `GameSession` - משחקים פעילים

**2. `def __init__(self, port: int = DEFAULT_PORT):`**

**תפקיד:**
אתחול השרת עם ברירת מחדל לפורט 5555.

**מדוע קיים:**
לאפשר הרצה עם פורט מותאם אם צריך.

**פרמטרים:**
- `port: int` - הפורט להאזנה (ברירת מחדל: 5555)

**ערך מוחזר:**
instance חדש של `AppServer`

**אלגוריתם:**
1. שמירת הפורט
2. יצירת `Matchmaker`
3. יצירת `RoomManager`
4. אתחול מילון `_sessions` (ריק)
5. יצירת `_session_lock`

**פרטי מימוש חשובים:**
- שימוש ב-`DEFAULT_PORT` מ-`shared.constants`
- `_sessions` מתעדכן דינמית כאשר משחקים מתחילים ומסתיימים

**מתי נקרא:**
בעת אתחול השרת

**מי קורא:**
`server/main.py` ב-`main()`

**3. `async def start(self) -> None:`**

**תפקיד:**
הפעלת השרת - מאזין לחיבורים ומריץ את לולאת ההתאמה.

**מדוע קיים:**
לולאה ראשית של השרת.

**פרמטרים:**
אין

**ערך מוחזר:**
`None` (רץ לנצח)

**אלגוריתם:**
1. קריאה ל-`init_db()` לאתחול מסד הנתונים
2. הדפסת לוג עם כתובת השרת
3. יצירת שרת WebSocket עם `websockets.serve()`:
   - מאזין ב-`0.0.0.0` (כל הממשקים)
   - בפורט `_port`
   - פונקציית callback: `_on_connect`
4. הרצת `_match_loop()` (לולאה אינסופית)

**פרטי מימוש חשובים:**
- `websockets.serve()` מחזירה context manager
- `0.0.0.0` מאזין על כל הממשקים (גם localhost, גם LAN)
- `_match_loop()` רץ בתוך אותו event loop

**מתי נקרא:**
לאחר יצירת ה-`AppServer`

**מי קורא:**
`server/main.main()`

**4. `async def _match_loop(self) -> None:`**

**תפקיד:**
לולאה שמפעילה את המנוע להתאמת שחקנים כל שנייה.

**מדוע קיים:**
צריך לבדוק באופן קבוע אם יש שחקנים שיכולים להתאים.

**פרמטרים:**
אין

**ערך מוחזר:**
`None` (לולאה אינסופית)

**אלגוריתם:**
1. `await asyncio.sleep(1)` - המתנה לשנייה
2. `self._matchmaker.match()` - ניסיון להתאים שחקנים
3. חזרה לשלב 1

**פרטי מימוש חשובים:**
- רץ כל שנייה, לא כל הזמן
- `match()` של `Matchmaker` מחפש זוגות אפשריים

**מתי נקרא:**
באופן רציף לאחר אתחול השרת

**מי קורא:**
`start()` לאחר יצירת שרת ה-WebSocket

**5. `async def _on_connect(self, websocket) -> None:`**

**תפקיד:**
טיפול בחיבור WebSocket חדש.

**מדוע קיים:**
כל שחקן שמתחבר עובר דרך פונקציה זו.

**פרמטרים:**
- `websocket` - חיבור WebSocket מהספרייה

**ערך מוחזר:**
`None` (החיבור מסתיים בסופו של דבר)

**אלגוריתם:**
1. קריאה ל-`authenticate(websocket)` לאימות
   - אם מחזיר `None`: צאץ (כישלון אימות)
2. קבלת `name` ו-`rating` מהאימות
3. יצירת `PlayerConnection` עם הצבע הלבן זמני
4. שליחת `RoomStateMsg` עם החדר הראשי
5. המתנה להודעה ראשונה מהשחקן (עם timeout של 300 שניות)
6. ניתוק אם timeout או שגיאה
7. הפניה לטיפול לפי סוג ההודעה:
   - `RoomCreateMsg`: `_handle_room_create()`
   - `RoomJoinMsg`: `_handle_room_join()`
   - `PlayRequestMsg`: `_handle_matchmaking()`

**פרטי מימוש חשובים:**
- `PLAY_REQUEST_TIMEOUT_S` = 300 שניות לחכות
- `json.loads(raw)` מפענח את ה-JSON
- `parse()` הופך את ה-dict להודעת dataclass

**מתי נקרא:**
לכל חיבור WebSocket חדש

**מי קורא:**
`websockets.serve()` (ספריית WebSocket)

**6. `async def _handle_room_create(self, conn: PlayerConnection) -> None:`**

**תפקיד:**
טיפול בבקשה ליצירת חדר פרטי.

**מדוע קיים:**
לאפשר לשחקנים לשחק עם חברים.

**פרמטרים:**
- `conn: PlayerConnection` - החיבור של היוצר

**ערך מוחזר:**
`None`

**אלגוריתם:**
1. יצירת חדר עם `_room_manager.create(conn)`
2. קביעת צבע היוצר ללבן
3. שליחת `RoomStateMsg` עם פרטי החדר
4. המתנה לאירוע `room.ready` (שחקן שני מצטרף)
5. כאשר מוכן: קריאה ל-`_start_room_session()`

**פרטי מימוש חשובים:**
- היוצר תמיד לבן בחדרים פרטיים
- `room.ready` הוא `asyncio.Event()` שמתמלא כאשר שחקן שני מצטרף

**מתי נקרא:**
כאשר שחקן שולח `RoomCreateMsg`

**מי קורא:**
`_on_connect()` לאחר ניתוח ההודעה

**7. `async def _handle_room_join(self, conn: PlayerConnection, room_id: str) -> None:`**

**תפקיד:**
טיפול בהצטרפות לחדר קיים.

**מדוע קיים:**
לאפשר לשחקן שני (או צופה) להצטרף לחדר.

**פרמטרים:**
- `conn: PlayerConnection` - החיבור המצטרף
- `room_id: str` - מזהה החדר

**ערך מוחזר:**
`None`

**אלגוריתם:**
1. חיפוש החדר עם `_room_manager.join(room_id, conn)`
   - אם `None`: שליחת `RoomErrorMsg` וחזרה
2. קביעת התפקיד עם `room.add(conn)`:
   - `"b"` אם השחקן השני
   - מחרוזת ריקה אם צופה
3. קביעת צבע החיבור לפי התפקיד
4. אם שחקן שני:
   - המתנה לאירוע סיום מהלבן
5. אם צופה:
   - שליחת `RoomStateMsg` עם מצב החדר
   - אם יש כבר `session`, הוספה כצופה
   - המתנה לאירוע סיום

**פרטי מימוש חשובים:**
- `room.add()` מחזירה את התפקיד (`"b"` או `""`)
- צופים לא משפיעים על המשחק
- `session.add_spectator()` מאפשרת לצופה לקבל עדכונים

**מתי נקרא:**
כאשר שחקן שולח `RoomJoinMsg`

**מי קורא:**
`_on_connect()` לאחר ניתוח ההודעה

**8. `async def _start_room_session(self, room) -> None:`**

**תפקיד:**
הפעלת משחק בחדר.

**מדוע קיים:**
כאשר שני שחקנים בחדר, צריך להתחיל את המשחק.

**פרמטרים:**
- `room` - אובייקט החדר עם שני השחקנים

**ערך מוחזר:**
`None`

**אלגוריתם:**
1. קבלת הלבן (`white`) והשחור (`black`) מהחדר
2. שליחת `RoomStateMsg` לכל שחקן עם מצב התחלה
3. שליחת `RoomStateMsg` לכל צופה
4. יצירת `session_key` = שם הלבן
5. עם נעילת `_session_lock`:
   - אם אין `session_key` ב-`_sessions`: יצירת `asyncio.Event()`
6. קבלת ה-`done_event` מה-`_sessions`
7. יצירת `GameSession` עם:
   - השחקנים
   - הצופים
   - callback `on_done=done_event.set()`
8. הגדרת `room.session` למשחק החדש
9. הרצת `session.run()` (עד לסיום המשחק)
10. לבסוף:
    - הסרת החדר מה-`_room_manager`
    - הסרת ה-`session_key` מה-`_sessions`

**פרטי מימוש חשובים:**
- `done_event.set()` נקרא כאשר המשחק מסתיים
- הצופים מקבלים עדכונים מהסשן
- נעילת `_session_lock` מגינה על `_sessions` מריבוי threads

**מתי נקרא:**
כאשר שני שחקנים בחדר פרטי

**מי קורא:**
`_handle_room_create()` כאשר `room.ready` מתמלא

**9. `async def _get_or_create_done_event(self, key: str) -> asyncio.Event:`**

**תפקיד:**
קבלת או יצירת אירוע סיום לסשן.

**מדוע קיים:**
לסנכרן בין שחקנים שצריכים לחכות לסשן מסוים.

**פרמטרים:**
- `key: str` - מפתח (שם השחקן הלבן)

**ערך מוחזר:**
`asyncio.Event` קיים או חדש

**אלגוריתם:**
1. עם נעילת `_session_lock`:
2. אם `key` לא ב-`_sessions`: יצירת `asyncio.Event()`
3. החזרת ה-event

**פרטי מימוש חשובים:**
- נעילה מונעת race conditions
- אירועים נשמרים למשך חיי הסשן

**מתי נקרא:**
כאשר שחקן שחור או צופה מצטרף לחדר

**מי קורא:**
`_handle_room_join()` ו-`_start_room_session()`

**10. `async def _handle_matchmaking(self, conn: PlayerConnection) -> None:`**

**תפקיד:**
טיפול בבקשה להתאמה אוטומטית (matchmaking).

**מדוע קיים:**
לשחק עם שחקן אקראי ברשת דומה.

**פרמטרים:**
- `conn: PlayerConnection` - החיבור המחפש

**ערך מוחזר:**
`None`

**אלגוריתם:**
1. הוספת החיבור ל-`_matchmaker.add(conn)` (מחזירה `Future`)
2. המתנה ל-`MATCH_TIMEOUT_S` (60 שניות) שימצא יריב
3. אם timeout:
   - הסרת החיבור מה-matchmaker
   - שליחת `SearchTimeoutMsg()`
   - חזרה
4. אם נמצא יריב:
   - קבלת ה-`opponent` מה-`Future`
   - קביעת מי לבן ומי שחור לפי `id()` של החיבור
   - שליחת `RoomStateMsg` לשני השחקנים
   - אם הקליינט הוא הלבן:
     - יצירת `GameSession` והרצתו
     - הסרת ה-`session_key` מה-`_sessions`
   - אם הקליינט הוא השחור:
     - המתנה לאירוע סיום של הלבן

**פרטי מימוש חשובים:**
- `id(conn) < id(opponent)` קובע מי לבן (קבוע אך לא אקראי לחלוטין)
- `asyncio.shield(fut)` מגן על ה-Future מ-cancellation
- הלבן מתחיל את הסשן, השחור מחכה

**מתי נקרא:**
כאשר שחקן שולח `PlayRequestMsg`

**מי קורא:**
`_on_connect()` לאחר ניתוח ההודעה

---

## 🗂️ המשך סקירת הקבצים - תיקיית Server Auth

### 📄 server/auth/auth_handler.py

בואו נסתכל על האנדלר לאימות:
### 📄 server/auth/auth_handler.py

**מטרת הקובץ:**
טיפול בבקשות אימות (LOGIN/REGISTER) על חיבור WebSocket טרם כניסה ל-matchmaking או חדר.

**מדוע קובץ זה קיים:**
צריך להפריד את הלוגיקה של אימות מהלוגיקה של המשחק. כל שחקן חייב לעבור אימות לפני שהוא יכול לשחק.

**אילו קבצים משתמשים בו:**
- `server/app_server.py` - קורא ל-`authenticate()` עבור כל חיבור חדש

**אילו מודולים הוא מייבא:**
- `json` - עבור serialization
- `shared.messages` - הודעות LOGIN ו-OK/FAIL
- `server.auth.auth_service` - הלוגיקה האמיתית של האימות
- `server.errors` - שגיאות מיוחדות
- `server.logging.server_logger` - מערכת לוגים

**אילו מודולים מייבאים אותו:**
רק `server/app_server.py`

**איך הוא משתתף בפרויקט:**
זה השער לאימות. כל שחקן חייב לעבור דרך פונקציה זו לפני שהוא יכול לשחק.

#### 📝 פונקציות:

**1. `async def authenticate(websocket) -> tuple[str, int] | None:`**

**תפקיד:**
קריאת הודעות LOGIN/REGISTER עד שאימות מצליח.

**מדוע קיים:**
לאפשר לשחקנים להתחבר או להירשם דרך אותה נקודת כניסה.

**פרמטרים:**
- `websocket` - חיבור WebSocket מהספרייה

**ערך מוחזר:**
- `tuple[str, int]` - `(username, rating)` אם האימות הצליח
- `None` אם החיבור נסגר או שגיאת database

**אלגוריתם:**
1. לולאה `async for raw in websocket:` (מקבלת הודעות)
2. לכל הודעה:
   - ניסיון ל-`parse(json.loads(raw))` להפוך ל-dataclass
   - אם שגיאה: continue (מחכה להודעה הבאה)
   - אם לא `LoginMsg`: continue (מחכה להודעת LOGIN)
   - ניסיון אימות:
     - אם `msg.register == True`: קריאה ל-`auth_service.register()`
     - אחרת: קריאה ל-`auth_service.login()`
   - אם הצליח:
     - הדפסת לוג
     - שליחת `LoginOkMsg` לקליינט
     - החזרת `(username, rating)`
   - אם `AuthError`:
     - הדפסת לוג אזהרה
     - שליחת `LoginFailMsg` עם הסיבה
     - continue (מנסה שוב)
   - אם `DatabaseError`:
     - הדפסת לוג שגיאה
     - החזרת `None` (סיום החיבור)

**פרטי מימוש חשובים:**
- `async for` מקבל הודעות בצורה אסינכרונית
- רק `LoginMsg` מתקבלת, כל הודעה אחרת מתעלמים ממנה
- יכול להתנסות מספר פעמים (משתמש יכול לטעות בסיסמה)
- `auth_service` עושה את העבודה הקשה

**מתי נקרא:**
לכל חיבור WebSocket חדש לשרת

**מי קורא:**
`AppServer._on_connect()`

### 📄 server/auth/auth_service.py

בואו נסתכל על שירות האימות:
### 📄 server/db/user_repository.py

**מטרת הקובץ:**
שכבת גישה למשתמשים ברמת domain - wrapper מסביב לפונקציות ה-raw של ה-database.

**מדוע קובץ זה קיים:**
להפריד בין ה-dataclasses של המשתמשים לבין הפונקציות ה-raw של ה-SQLite.

**אילו קבצים משתמשים בו:**
- `server/auth/auth_service.py` - עבור `get()` ו-`create()`
- `server/rating/rating_service.py` - עבור `update_rating()`

**אילו מודולים הוא מייבא:**
- `from server.db import database as db` - הפונקציות ה-raw
- `from shared.constants import ELO_DEFAULT` - דירוג ברירת מחדל

**אילו מודולים מייבאים אותו:**
- `server.auth.auth_service`
- `server.rating.rating_service`

**איך הוא משתתף בפרויקט:**
זה ה-Repository pattern - מספק ממשק נקי לגישת משתמשים מבלי לחשוף פרטי SQLite.

#### 📝 מחלקות:

**1. `@dataclass class User:`**

**תפקיד:**
ייצוג משתמש בתוך הקוד של השרת.

**מדוע קיים:**
לעבוד עם אובייקטים נקיים במקום עם `sqlite3.Row`.

**שדות חשובים:**
- `user_id: int` - מזהה ייחודי (אוטומטי)
- `username: str` - שם המשתמש
- `password_hash: str` - הסיסמה המוצפנת עם bcrypt
- `rating: int` - דירוג ELO הנוכחי

**מחזור חיים:**
- נוצר בעת קריאת משתמש מה-database
- מוחזר לפונקציות קוראות
- לא נשמר באופן אוטומטי (צריך `update_rating()`)

**שיתוף פעולה:**
- `auth_service` - עבור אימות
- `rating_service` - עבור עדכון דירוגים

**2. `def get(username: str) -> User | None:`**

**תפקיד:**
קבלת משתמש לפי שם משתמש.

**מדוע קיים:**
להסתיר את פרטי ה-`sqlite3.Row` מהקוד הקורא.

**פרמטרים:**
- `username: str` - שם המשתמש לחיפוש

**ערך מוחזר:**
- `User` אם נמצא
- `None` אם לא נמצא

**אלגוריתם:**
1. קריאה ל-`db.fetch_user(username)` (מחזיר `sqlite3.Row` או `None`)
2. אם `row`:
   - יצירת `User` עם השדות מה-row
   - החזרת ה-`User`
3. אחרת: החזרת `None`

**פרטי מימוש חשובים:**
- גישה לשדות ב-row עם `row["field_name"]`
- `dataclass` מספק ייצוג נקי יותר מ-`sqlite3.Row`

**מתי נקרא:**
בעת התחברות משתמש

**מי קורא:**
`auth_service.login()`

**3. `def create(username: str, password_hash: str) -> User:`**

**תפקיד:**
יצירת משתמש חדש.

**מדוע קיים:**
להחזיר אובייקט `User` במקום רק user_id.

**פרמטרים:**
- `username: str` - שם המשתמש החדש
- `password_hash: str` - הסיסמה המוצפנת

**ערך מוחזר:**
`User` - המשתמש שנוצר

**אלגוריתם:**
1. קריאה ל-`db.insert_user(username, password_hash)` (מחזיר `user_id`)
2. יצירת `User` עם:
   - `user_id`: מה-database
   - `username`: מהפרמטר
   - `password_hash`: מהפרמטר
   - `rating`: `ELO_DEFAULT` (1200)
3. החזרת ה-`User`

**פרטי מימוש חשובים:**
- `ELO_DEFAULT` מהקבועים המשותפים
- ה-`password_hash` כבר מוצפן לפני שמועבר לכאן

**מתי נקרא:**
כאשר משתמש נרשם

**מי קורא:**
`auth_service.register()`

**4. `def update_rating(username: str, rating: int) -> None:`**

**תפקיד:**
עדכון דירוג משתמש.

**מדוע קיים:**
לעדכן את ה-database לאחר חישוב ELO.

**פרמטרים:**
- `username: str` - שם המשתמש לעדכון
- `rating: int` - הדירוג החדש

**ערך מוחזר:**
`None`

**אלגוריתם:**
1. קריאה ל-`db.set_rating(username, rating)`
2. אין החזרת ערך

**פרטי מימוש חשובים:**
- פונקציה פשוטת wrapper
- לא צורך להחזיר את המשתמש המעודכן

**מתי נקרא:**
לאחר סיום משחק מדורג

**מי קורא:**
`rating_service.update_ratings()`

### 📄 server/errors.py

בואו נסתכל על שגיאות השרת:
### 📄 server/errors.py

**מטרת הקובץ:**
הגדרת שגיאות מיוחדות של השרת.

**מדוע קובץ זה קיים:**
להבדיל בין שגיאות business (אימות) לבין שגיאות טכניות (database).

**אילו קבצים משתמשים בו:**
- `server/auth/auth_service.py` - מעלה `AuthError` ו-`DatabaseError`
- `server/auth/auth_handler.py` - תופס את השגיאות

**אילו מודולים הוא מייבא:**
אין ייבוא

**אילו מודולים מייבאים אותו:**
- `server.auth.auth_service`
- `server.auth.auth_handler`

**איך הוא משתתף בפרויקט:**
מספק טיפוסי שגיאה ספציפיים למערכת.

#### 📝 מחלקות:

**1. `class AuthError(Exception):`**

**תפקיד:**
שגיאת אימות - כאשר login או registration נכשל מסיבה business.

**מדוע קיים:**
להבדיל בין "שם משתמש כבר בשימוש" לבין שגיאת database.

**מחזור חיים:**
- נוצר על ידי `auth_service`
- נתפס על ידי `auth_handler`
- מומר ל-`LoginFailMsg` ונשלח לקליינט

**דוגמאות לשימוש:**
- "username already taken"
- "invalid credentials"

**2. `class DatabaseError(Exception):`**

**תפקיד:**
שגיאת database - כאשר פעולת database נכשלת באופן בלתי צפוי.

**מדוע קיים:**
להבדיל בין שגיאות business לבין תקלות טכניות.

**מחזור חיים:**
- נוצר על ידי `auth_service` או `database.py`
- נתפס על ידי `auth_handler`
- גורם לניתוק החיבור (לא נשלח לקליינט)

**דוגמאות לשימוש:**
- "could not create user: disk full"
- "could not fetch user: table does not exist"

---

## 🗂️ המשך סקירת הקבצים - Matchmaking ו-Rating

### 📄 server/matchmaker.py

בואו נסתכל על מנוע ההתאמה:
### 📄 server/matchmaker.py

**מטרת הקובץ:**
מנוע התאמת שחקנים - מחזיק שחקנים שמחכים למשחק ומתאם ביניהם.

**מדוע קובץ זה קיים:**
צריך לאפשר לשחקנים למצוא יריבים ברמת דירוג דומה.

**אילו קבצים משתמשים בו:**
- `server/app_server.py` - קורא ל-`add()`, `remove()`, ו-`match()`

**אילו מודולים הוא מייבא:**
- `asyncio` - עבור `Future` ו-event loop
- `server.session.player_connection` - עבור חיבורי שחקנים
- `shared.constants import ELO_RANGE` - טווח דירוג להתאמה

**אילו מודולים מייבאים אותו:**
רק `server/app_server.py`

**איך הוא משתתף בפרויקט:**
מנהל תור שחקנים ומתאם ביניהם כאשר הדירוגים תואמים.

#### 📝 מחלקות:

**1. `class Matchmaker:`**

**תפקיד:**
מחזיק שחקנים שמחכים למשחק ומתאם ביניהם.

**מדוע קיים:**
להפריד את לוגיקת ההתאמה מהלוגיקה של החיבורים.

**שדות חשובים:**
- `_queue: list[tuple[PlayerConnection, asyncio.Future]]` - תור שחקנים עם futures

**מחזור חיים:**
- נוצר על ידי `AppServer`
- פעיל לכל אורך חיי השרת
- מסיים כאשר השרת נסגר

**שיתוף פעולה:**
- `AppServer` - קורא ל-`match()` כל שנייה
- `PlayerConnection` - אובייקטים שחקנים בתור

**2. `def __init__(self):`**

**תפקיד:**
אתחול ה-matchmaker עם תור ריק.

**מדוע קיים:**
להכין את המבנה הפנימי.

**פרמטרים:**
אין

**ערך מוחזר:**
instance חדש של `Matchmaker`

**אלגוריתם:**
1. יצירת רשימה ריקה ל-`_queue`

**פרטי מימוש חשובים:**
- `_queue` הוא list של tuples: `(PlayerConnection, asyncio.Future)`
- ה-Future נפתר כאשר נמצא יריב

**מתי נקרא:**
בעת יצירת `AppServer`

**מי קורא:**
`AppServer.__init__()`

**3. `def add(self, conn: PlayerConnection) -> asyncio.Future:`**

**תפקיד:**
הוספת שחקן לתור ההתאמה.

**מדוע קיים:**
להכניס שחקן חדש שמחפש משחק.

**פרמטרים:**
- `conn: PlayerConnection` - חיבור השחקן

**ערך מוחזר:**
`asyncio.Future` - נפתר ל-`PlayerConnection` של היריב כשנמצא

**אלגוריתם:**
1. יצירת `Future` חדש עם `asyncio.get_event_loop().create_future()`
2. הוספת ה-tuple `(conn, fut)` ל-`_queue`
3. החזרת ה-`Future`

**פרטי מימוש חשובים:**
- ה-`Future` נשאר pending עד שנמצא יריב
- השחקן ממתין ב-`await fut` (נעשה ב-`AppServer`)
- אם timeout, ה-`Future` מבוטל

**מתי נקרא:**
כאשר שחקן שולח `PlayRequestMsg`

**מי קורא:**
`AppServer._handle_matchmaking()`

**4. `def remove(self, conn: PlayerConnection) -> None:`**

**תפקיד:**
הסרת שחקן מהתור (התנתק לפני התאמה).

**מדוע קיים:**
לנקות שחקנים שהתנתקו בזמן ההמתנה.

**פרמטרים:**
- `conn: PlayerConnection` - החיבור להסרה

**ערך מוחזר:**
`None`

**אלגוריתם:**
1. יצירת רשימה `remaining` ריקה
2. עבור כל `(c, f)` ב-`_queue`:
   - אם `c is conn`: `f.cancel()` (ביטול ה-Future)
   - אחרת: הוספה ל-`remaining`
3. עדכון `_queue` ל-`remaining`

**פרטי מימוש חשובים:**
- `is` operator במקום `==` לבדיקת זהות אובייקט
- `f.cancel()` מסמן ל-Future שהוא מבוטל
- השחקן השני בתור לא יודע על ההתנתקות

**מתי נקרא:**
כאשר שחקן מתנתק בזמן ההמתנה

**מי קורא:**
`AppServer._handle_matchmaking()` על timeout

**5. `def match(self) -> list[tuple[PlayerConnection, PlayerConnection]]:`**

**תפקיד:**
סריקת התור ומציאת זוגות תואמים (דירוג בטווח).

**מדוע קיים:**
לבצע את ההתאמה בפועל.

**פרמטרים:**
אין

**ערך מוחזר:**
`list[tuple[PlayerConnection, PlayerConnection]]` - רשימת הזוגות שהותאמו

**אלגוריתם:**
1. יצירת `matched: set[int]` (אינדקסים של שחקנים שכבר הותאמו)
2. יצירת `pairs: list` ריקה
3. לולאה כפולה על `_queue`:
   - ל-`i` מ-0 עד סוף:
     - אם `i` כבר ב-`matched`: continue
     - ל-`j` מ-`i+1` עד סוף:
       - אם `j` כבר ב-`matched`: continue
       - אם `abs(a.rating - b.rating) <= ELO_RANGE`:
         - הוספת `i` ו-`j` ל-`matched`
         - הוספת `(a, b)` ל-`pairs`
         - `fa.set_result(b)` (פיתרון Future של a)
         - `fb.set_result(a)` (פיתרון Future של b)
         - break (יציאה מהלולאה הפנימית)
4. עדכון `_queue` - רק שחקנים שלא ב-`matched`
5. החזרת `pairs`

**פרטי מימוש חשובים:**
- `ELO_RANGE` = 100 (מהקבועים)
- `set_result()` מעיר את ה-`await` ב-`AppServer`
- O(n²) algorithm אבל n קטן (מספר שחקנים מחכים)
- מתאים את הראשון לתואם הראשון

**מתי נקרא:**
כל שנייה על ידי `AppServer._match_loop()`

**מי קורא:**
`AppServer._match_loop()`

### 📄 server/room_manager.py

בואו נסתכל על מנהל החדרים:
### 📄 server/room_manager.py

**מטרת הקובץ:**
ניהול חדרים פרטיים - יצירה, הצטרפות, ומחיקה.

**מדוע קובץ זה קיים:**
צריך מקום מרכזי לעקוב אחרי כל החדרים הפעילים.

**אילו קבצים משתמשים בו:**
- `server/app_server.py` - קורא ל-`create()`, `join()`, ו-`remove()`

**אילו מודולים הוא מייבא:**
- `uuid` - יצירת מזהה ייחודי
- `server.session.player_connection` - חיבורי שחקנים
- `server.session.room` - מחלקת החדר
- `shared.constants import ROOM_ID_LENGTH` - אורך קוד החדר

**אילו מודולים מייבאים אותו:**
רק `server/app_server.py`

**איך הוא משתתף בפרויקט:**
מנהל את כל החדרים הפרטיים במערכת.

#### 📝 מחלקות:

**1. `class RoomManager:`**

**תפקיד:**
מנהל רישום של כל החדרים הפעילים.

**מדוע קיים:**
להחזיק dictionary מרכזי של חדרים.

**שדות חשובים:**
- `_rooms: dict[str, Room]` - מיפוי בין room_id ל-Room

**מחזור חיים:**
- נוצר על ידי `AppServer`
- פעיל לכל אורך חיי השרת
- מסיים כאשר השרת נסגר

**שיתוף פעולה:**
- `AppServer` - מבצע פעולות על חדרים
- `Room` - אובייקטי חדרים שנשמרים כאן

**2. `def __init__(self):`**

**תפקיד:**
אתחול ה-RoomManager עם מילון ריק.

**מדוע קיים:**
להכין את המבנה הפנימי.

**פרמטרים:**
אין

**ערך מוחזר:**
instance חדש של `RoomManager`

**אלגוריתם:**
1. יצירת מילון ריק ל-`_rooms`

**פרטי מימוש חשובים:**
- `dict` עם room_id כמפתח ו-`Room` כערך
- גישה מהירה O(1) לחדרים לפי ID

**מתי נקרא:**
בעת יצירת `AppServer`

**מי קורא:**
`AppServer.__init__()`

**3. `def create(self, conn: PlayerConnection) -> Room:`**

**תפקיד:**
יצירת חדר חדש עם שחקן יוצר.

**מדוע קיים:**
לאפשר לשחקנים ליצור חדרים פרטיים.

**פרמטרים:**
- `conn: PlayerConnection` - החיבור של היוצר

**ערך מוחזר:**
`Room` - החדר החדש שנוצר

**אלגוריתם:**
1. יצירת `room_id` ייחודי עם `_unique_id()`
2. יצירת `Room` חדש עם ה-room_id וה-conn
3. הוספת החדר ל-`_rooms`
4. החזרת ה-`Room`

**פרטי מימוש חשובים:**
- היוצר הופך לשחקן הלבן בחדר
- `Room` מקבל את ה-`PlayerConnection` ב-constructor

**מתי נקרא:**
כאשר שחקן שולח `RoomCreateMsg`

**מי קורא:**
`AppServer._handle_room_create()`

**4. `def join(self, room_id: str, conn: PlayerConnection) -> Room | None:`**

**תפקיד:**
הצטרפות לחדר קיים.

**מדוע קיים:**
לאפשר לשחקנים להצטרף לחדרים של אחרים.

**פרמטרים:**
- `room_id: str` - מזהה החדר
- `conn: PlayerConnection` - החיבור המצטרף

**ערך מוחזר:**
- `Room` אם החדר נמצא
- `None` אם החדר לא נמצא

**אלגוריתם:**
1. חיפוש ב-`_rooms` עם `room_id.upper()`
2. החזרת התוצאה של `.get()` (יכול להיות `None`)

**פרטי מימוש חשובים:**
- `room_id.upper()` - הופך את הקוד ל-uppercase (לא תלוי רישיות)
- `dict.get()` מחזיר `None` אם המפתח לא קיים
- הוספת השחקן לחדר נעשית ב-`Room.add()` (לא כאן)

**מתי נקרא:**
כאשר שחקן שולח `RoomJoinMsg`

**מי קורא:**
`AppServer._handle_room_join()`

**5. `def remove(self, room_id: str) -> None:`**

**תפקיד:**
הסרת חדר מהרישום.

**מדוע קיים:**
כאשר משחק בחדר מסתיים, צריך לנקות.

**פרמטרים:**
- `room_id: str` - מזהה החדר להסרה

**ערך מוחזר:**
`None`

**אלגוריתם:**
1. `self._rooms.pop(room_id, None)` - הסרה עם ברירת מחדל

**פרטי מימוש חשובים:**
- `.pop()` עם ברירת מחדל מונעת `KeyError` אם החדר כבר נמחק
- הסרה אטומית מהמילון

**מתי נקרא:**
לאחר סיום משחק בחדר

**מי קורא:**
`AppServer._start_room_session()` בסיום הסשן

**6. `def _unique_id(self) -> str:`**

**תפקיד:**
יצירת מזהה חדר ייחודי.

**מדוע קיים:**
להבטיח שלכל חדר יש קוד ייחודי.

**פרמטרים:**
אין

**ערך מוחזר:**
`str` - קוד חדר ייחודי

**אלגוריתם:**
1. לולאה אינסופית:
2. יצירת קוד עם `uuid.uuid4().hex[:ROOM_ID_LENGTH].upper()`:
   - `uuid.uuid4()` - UUID אקראי
   - `.hex` - המרה ל-hex string
   - `[:4]` - 4 תווים ראשונים
   - `.upper()` - הופך ל-uppercase
3. אם הקוד לא ב-`_rooms`: החזרת הקוד
4. חזרה לשלב 2 (בסבירות נמוכה מאוד להתנגשות)

**פרטי מימוש חשובים:**
- `ROOM_ID_LENGTH` = 4 תווים
- UUID v4 נותן 32 תווים hex, לוקחים 4 ראשונים
- הסתברות להתנגשות מאוד נמוכה (16^4 = 65536 אפשרויות)
- לולאה רק במקרה נדיר של התנגשות

**מתי נקרא:**
בתוך `create()` כאשר יוצרים חדר

**מי קורא:**
`create()`

### 📄 server/session/room.py

בואו נסתכל על מחלקת החדר:
### 📄 server/session/room.py

**מטרת הקובץ:**
מחלקה המייצגת חדר פרטי במערכת.

**מדוע קובץ זה קיים:**
לאגד את כל המידע על חדר אחד במקום אחד.

**אילו קבצים משתמשים בו:**
- `server/room_manager.py` - יוצר `Room` objects
- `server/app_server.py` - משתמש בשדות של `Room`

**אילו מודולים הוא מייבא:**
- `asyncio` - עבור `Event`
- `server.session.player_connection` - חיבורי שחקנים

**אילו מודולים מייבאים אותו:**
- `server.room_manager`
- `server.app_server`

**איך הוא משתתף בפרויקט:**
מייצג חדר פרטי עם שחקנים וצופים.

#### 📝 מחלקות:

**1. `class Room:`**

**תפקיד:**
מיכל נתונים לחדר פרטי אחד.

**מדוע קיים:**
לאגד את כל המידע על חדר במקום אחד.

**שדות חשובים:**
- `room_id: str` - מזהה ייחודי של החדר
- `white: PlayerConnection` - השחקן הראשון שהצטרף (תמיד לבן)
- `black: PlayerConnection | None` - השחקן השני (או `None` אם אין)
- `spectators: list[PlayerConnection]` - רשימת צופים
- `ready: asyncio.Event` - אירוע שמתמלא כאשר יש לבן ושחור
- `session: object | None` - `GameSession` לאחר שהמשחק התחיל

**מחזור חיים:**
1. נוצר על ידי `RoomManager.create()`
2. מתמלא בהדרגה עם שחקנים וצופים
3. כאשר `ready` מתמלא, `GameSession` נוצר
4. נהרס לאחר סיום המשחק

**שיתוף פעולה:**
- `PlayerConnection` - שחקנים בחדר
- `GameSession` - המשחק הפעיל בחדר

**2. `def __init__(self, room_id: str, white: PlayerConnection):`**

**תפקיד:**
אתחול חדר עם מזהה ושחקן לבן.

**מדוע קיים:**
כאשר יוצר חדר, יש כבר שחקן אחד (היוצר).

**פרמטרים:**
- `room_id: str` - מזהה החדר
- `white: PlayerConnection` - השחקן הלבן (היוצר)

**ערך מוחזר:**
instance חדש של `Room`

**אלגוריתם:**
1. שמירת `room_id`
2. שמירת `white`
3. אתחול `black` ל-`None`
4. אתחול `spectators` ל-רשימה ריקה
5. יצירת `asyncio.Event()` ל-`ready`
6. אתחול `session` ל-`None`

**פרטי מימוש חשובים:**
- היוצר תמיד לבן בחדרים פרטיים
- `ready` הוא `Event` שלא מתמלא עד שיש שחור
- `session` מצביע ל-`GameSession` לאחר התחלה

**מתי נקרא:**
בעת יצירת חדר חדש

**מי קורא:**
`RoomManager.create()`

**3. `@property def player_names(self) -> list[str]:`**

**תפקיד:**
קבלת רשימת שמות השחקנים בחדר.

**מדוע קיים:**
נוחיות - לקבל רק את השמות ללא האובייקטים המלאים.

**פרמטרים:**
אין (property)

**ערך מוחזר:**
`list[str]` - רשימת שמות שחקנים

**אלגוריתם:**
1. יצירת `names` עם `[self.white.name]`
2. אם `self.black` קיים: הוספת `self.black.name`
3. החזרת `names`

**פרטי מימוש חשובים:**
- property ולא method - ניתן לגשת כ-`room.player_names`
- לא כולל שמות צופים (רק שחקנים פעילים)
- אם אין שחור, מחזיר רק שם אחד

**מתי נקרא:**
כאשר שולחים `RoomStateMsg` עם רשימת שחקנים

**מי קורא:**
`AppServer._start_room_session()` ועוד מקומות

**4. `def add(self, conn: PlayerConnection) -> str:`**

**תפקיד:**
הוספת חיבור לחדר.

**מדוע קיים:**
להקצות תפקידים לשחקנים שמצטרפים.

**פרמטרים:**
- `conn: PlayerConnection` - החיבור להצטרפות

**ערך מוחזר:**
`str` - התפקיד שהוקצה: `"b"` לשחור, `""` לצופה

**אלגוריתם:**
1. אם `self.black is None`:
   - קביעת `self.black = conn`
   - `self.ready.set()` (ממלא את האירוע)
   - החזרת `"b"`
2. אחרת:
   - הוספת `conn` ל-`self.spectators`
   - החזרת `""`

**פרטי מימוש חשובים:**
- השחקן השני תמיד שחור
- כל חיבור נוסף הופך לצופה
- `ready.set()` מעיר את היוצר שמחכה

**מתי נקרא:**
כאשר שחקן מצטרף לחדר קיים

**מי קורא:**
`AppServer._handle_room_join()`

---

## 🗂️ המשך סקירת הקבצים - Session ו-PlayerConnection

### 📄 server/session/player_connection.py

בואו נסתכל על חיבור שחקן:
### 📄 server/session/player_connection.py

**מטרת הקובץ:**
wrapper מסביב לחיבור WebSocket אחד והצבע שהוקצה לשחקן הזה.

**מדוע קובץ זה קיים:**
לאגד את כל המידע על חיבור שחקן במקום אחד: websocket, צבע, שם, ודירוג.

**אילו קבצים משתמשים בו:**
- `server/app_server.py` - יוצר `PlayerConnection` objects
- `server/session/game_session.py` - שולח הודעות דרך `PlayerConnection`
- `server/matchmaker.py` - מחזיק `PlayerConnection` בתור
- `server/room_manager.py` ו-`server/session/room.py` - עובד עם חיבורים

**אילו מודולים הוא מייבא:**
- `json` - עבור serialization

**אילו מודולים מייבאים אותו:**
כמעט כל קובץ ב-`server/` directory

**איך הוא משתתף בפרויקט:**
זה ה-representation של שחקן בשרת - כולל חיבור רשת ונתונים.

#### 📝 מחלקות:

**1. `class PlayerConnection:`**

**תפקיד:**
עוטף חיבור WebSocket אחד ואת הנתונים של השחקן.

**מדוע קיים:**
להפריד בין ה-WebSocket הגולמי לבין השחקן עצמו.

**שדות חשובים:**
- `websocket` - חיבור WebSocket מהספרייה
- `color: str` - הצבע שהוקצה לשחקן (`"w"` או `"b"`)
- `name: str` - שם המשתמש
- `rating: int` - דירוג ELO הנוכחי (ברירת מחדל: 1200)

**מחזור חיים:**
1. נוצר על ידי `AppServer` לאחר אימות מוצלח
2. מועבר בין מערכות (matchmaking, rooms, sessions)
3. נהרס כאשר החיבור נסגר או המשחק מסתיים

**שיתוף פעולה:**
- `websockets` library - החיבור הבסיסי
- `AppServer` - ניהול החיבור
- `GameSession` - משחק דרך החיבור

**2. `def __init__(self, websocket, color: str, name: str, rating: int = 1200):`**

**תפקיד:**
אתחול חיבור שחקן חדש.

**מדוע קיים:**
לצרף את כל הנתונים לאובייקט אחד.

**פרמטרים:**
- `websocket` - חיבור WebSocket
- `color: str` - צבע השחקן (`"w"` או `"b"`)
- `name: str` - שם המשתמש
- `rating: int = 1200` - דירוג ELO (ברירת מחדל)

**ערך מוחזר:**
instance חדש של `PlayerConnection`

**אלגוריתם:**
1. שמירת ה-`websocket`
2. שמירת ה-`color`
3. שמירת ה-`name`
4. שמירת ה-`rating`

**פרטי מימוש חשובים:**
- דירוג ברירת מחדל 1200 (כמו `ELO_DEFAULT`)
- `color` יכול להשתנות כאשר שחקן מוקצה לחדר
- `name` ו-`rating` מקובעים לאחר יצירה

**מתי נקרא:**
לאחר אימות מוצלח של משתמש

**מי קורא:**
`AppServer._on_connect()`

**3. `async def send(self, msg) -> None:`**

**תפקיד:**
שליחת הודעה לשחקן דרך ה-WebSocket.

**מדוע קיים:**
wrapper נוח שממיר אוטומטית dataclass ל-JSON.

**פרמטרים:**
- `msg` - אובייקט הודעה מ-`shared/messages.py`

**ערך מוחזר:**
`None`

**אלגוריתם:**
1. קריאה ל-`msg.to_json()` להמרה ל-dict
2. `json.dumps()` להמרה ל-string JSON
3. `await self.websocket.send()` לשליחה על הרשת

**פרטי מימוש חשובים:**
- כל הודעת dataclass יש לה `to_json()`
- `await` כי `websocket.send()` היא אסינכרונית
- עוטף שגיאות - יכול להעלות `ConnectionClosed`

**מתי נקרא:**
בכל פעם שצריך לשלוח הודעה לשחקן

**מי קורא:**
`AppServer`, `GameSession`, ו-`Room` כאשר שולחים הודעות

**4. `async def send_raw(self, d: dict) -> None:`**

**תפקיד:**
שליחת dict גולמי לשחקן.

**מדוע קיים:**
למקרים נדירים שצריך לשלוח משהו שלא dataclass.

**פרמטרים:**
- `d: dict` - המילון לשליחה

**ערך מוחזר:**
`None`

**אלגוריתם:**
1. `json.dumps(d)` להמרה ל-string JSON
2. `await self.websocket.send()` לשליחה

**פרטי מימוש חשובים:**
- לא בשימוש נרחב - העדיפות היא ל-`send()` עם dataclasses
- יכול להיות שימושי עבור debugging

**מתי נקרא:**
לא בשימוש בפועל בקוד הנוכחי

**מי קורא:**
אין קריאות בפועל

### 📄 server/session/game_session.py

בואו נסתכל על הסשן של המשחק (זה קובץ מורכב מאוד, אז אקרא אותו בהדרגה):
### 📄 server/session/game_session.py

**מטרת הקובץ:**
לולאת המשחק האוטוריטטיבית למשחק אחד. זה המוח של המשחק בשרת.

**מדוע קובץ זה קיים:**
צריך מקום שמחזיק את מצב המשחק, מקבל פקודות משחקנים, מתקדם בזמן, ושולח עדכונים.

**אילו קבצים משתמשים בו:**
- `server/app_server.py` - יוצר ומריץ `GameSession`

**אילו מודולים הוא מייבא:**
- `asyncio`, `json`, `sys`, `os` - ספריות סטנדרטיות
- `game.game` ו-`board.board_parser` - מהלוגיקה
- כל הקבועים והודעות מה-`shared`
- `server.protocol.serializer` - המרת אובייקטים
- `server.rating.rating_service` - עדכון דירוגים
- `websockets.exceptions.ConnectionClosed` - שגיאות חיבור

**אילו מודולים מייבאים אותו:**
רק `server/app_server.py`

**איך הוא משתתף בפרויקט:**
זה המוח של כל משחק רשת - בעל הסמכות על המשחק.

#### 📝 מחלקות:

**1. `_STARTING_POSITION`**

**תפקיד:**
מחרוזת טקסטואלית המציגה את הלוח ההתחלתי של שחמט סטנדרטי.

**מדוע קיים:**
ליצור את אותו לוח התחלתי לכל משחק.

**ערך:**
לוח שחמט רגיל עם כל הקטעים במקומם.

**2. `class GameSession:`**

**תפקיד:**
סשן משחק - לולאה אוטוריטטיבית למשחק אחד.

**מדוע קיים:**
לנהל משחק שלם מהתחלה ועד סיום.

**שדות חשובים:**
- `_players: dict[str, PlayerConnection]` - שחקנים לפי צבע
- `_spectators: list[PlayerConnection]` - רשימת צופים
- `_on_done` - callback כאשר הסשן מסתיים
- `_game: Game` - אובייקט המשחק מהלוגיקה
- `_game_over_sent: bool` - האם הודעת סיום כבר נשלחה
- `_ms_since_update: int` - מילישניות מאז העדכון האחרון

**מחזור חיים:**
1. נוצר על ידי `AppServer`
2. מפעיל `run()` שרץ עד סיום המשחק
3. נהרס כאשר המשחק מסתיים

**שיתוף פעולה:**
- `Game` - לוגיקת המשחק
- `PlayerConnection` - חיבורי שחקנים
- `rating_service` - עדכון דירוגים

**3. `def __init__(self, white: PlayerConnection, black: PlayerConnection, spectators: list[PlayerConnection] | None = None, on_done=None):`**

**תפקיד:**
אתחול סשן משחק חדש.

**מדוע קיים:**
להכין את כל המשתנים לפני הרצת הלולאה.

**פרמטרים:**
- `white: PlayerConnection` - השחקן הלבן
- `black: PlayerConnection` - השחקן השחור
- `spectators: list[PlayerConnection] | None = None` - צופים (אופציונלי)
- `on_done` - callback לסיום (אופציונלי)

**ערך מוחזר:**
instance חדש של `GameSession`

**אלגוריתם:**
1. יצירת `_players` dict עם הלבן והשחור
2. שמירת `_spectators` (או רשימה ריקה)
3. שמירת `_on_done` callback
4. יצירת לוח התחלתי עם `BoardParser().parse()`
5. יצירת `Game` עם הלוח
6. אתחול `_game_over_sent = False`
7. אתחול `_ms_since_update = 0`

**פרטי מימוש חשובים:**
- `_STARTING_POSITION` היא מחרוזת טקסטואלית פשוטה
- `BoardParser` מפענח את הטקסט לאובייקט `Board`
- ה-`Game` הוא ממנוע הלוגיקה

**מתי נקרא:**
כאשר מתחיל משחק חדש

**מי קורא:**
`AppServer._start_room_session()` או `_handle_matchmaking()`

**4. `def add_spectator(self, conn: PlayerConnection) -> None:`**

**תפקיד:**
הוספת צופה שמצטרף מאוחר לסשן שכבר רץ.

**מדוע קיים:**
לאפשר לצופים להצטרף למשחק שכבר התחיל.

**פרמטרים:**
- `conn: PlayerConnection` - החיבור של הצופה

**ערך מוחזר:**
`None`

**אלגוריתם:**
1. הוספת `conn` ל-`_spectators` list

**פרטי מימוש חשובים:**
- פשוט מוסיף לרשימה
- הצופה יתחיל לקבל עדכונים מה-`_broadcast()`

**מתי נקרא:**
כאשר צופה מצטרף לחדר שכבר יש לו `GameSession`

**מי קורא:**
`AppServer._handle_room_join()` עבור צופים

**5. `async def run(self) -> None:`**

**תפקיד:**
הרצת הסשן - מתחיל את כל הלולאות.

**מדוע קיים:**
להתחיל את המשחק בפועל.

**פרמטרים:**
אין

**ערך מוחזר:**
`None` (רץ עד סיום המשחק)

**אלגוריתם:**
1. הדפסת לוג שהסשן התחיל
2. הרצת `asyncio.gather()` עם:
   - `_tick_loop()` - לולאת זמן
   - `_receive_loop(Color.WHITE)` - לולאת קבלה ללבן
   - `_receive_loop(Color.BLACK)` - לולאת קבלה לשחור
3. ב-`finally`: אם יש `_on_done`, קריאה לו

**פרטי מימוש חשובים:**
- `asyncio.gather()` מריץ את כל הלולאות במקביל
- אם אחת הלולאות מסתיימת, ה-`gather` מסתיים
- `finally` מבטיח שה-`on_done` תמיד נקרא

**מתי נקרא:**
לאחר יצירת ה-`GameSession`

**מי קורא:**
`AppServer` לאחר שהתחיל משחק חדש

**6. `async def _tick_loop(self) -> None:`**

**תפקיד:**
לולאת זמן - מתקדמת בזמן המשחק כל 50ms ושולחת עדכונים.

**מדוע קיים:**
המשחק צריך להתקדם בזמן, גם אם שחקנים לא עושים כלום.

**פרמטרים:**
אין

**ערך מוחזר:**
`None` (לולאה עד סיום המשחק)

**אלגוריתם:**
1. חישוב `interval = TICK_RATE_MS / 1000` (0.05 שניות)
2. לולאה כל עוד לא `_game_over_sent`:
   - `await asyncio.sleep(interval)` - המתנה ל-50ms
   - `self._game.advance_time(TICK_RATE_MS)` - התקדמות בזמן
   - אם `self._game.game_over` (המשחק הסתיים):
     - סימון `_game_over_sent = True`
     - קביעת המנצח והמפסיד
     - קריאה ל-`rating_service.apply_game_result()`
     - שליחת `GameOverMsg` לכולם
     - חזרה (סיום הלולאה)
   - עדכון `_ms_since_update += TICK_RATE_MS`
   - אם `_ms_since_update >= 200` (זמן לשידור עדכון):
     - איפוס `_ms_since_update`
     - שליחת `StateUpdateMsg` עם:
       - `board_to_json(self._game)` - הלוח הנוכחי
       - `time_ms` - הזמן הנוכחי
       - `motions` - תנועות אקטיביות

**פרטי מימוש חשובים:**
- `TICK_RATE_MS = 50` (השרת מתקדם כל 50ms)
- `STATE_UPDATE_INTERVAL_MS = 200` (שולחים עדכון כל 200ms)
- `advance_time()` מעדכן תנועות וזמנים במשחק
- `GameOverMsg` נשלח רק פעם אחת

**מתי נקרא:**
בתוך `run()` דרך `asyncio.gather()`

**מי קורא:**
`run()` מתחיל את הלולאה

**7. `async def _receive_loop(self, color: str) -> None:`**

**תפקיד:**
לולאת קבלה - מקבלת הודעות משחקן בצבע מסוים.

**מדוע קיים:**
לטפל בבקשות תנועה וקפיצה מהשחקנים.

**פרמטרים:**
- `color: str` - הצבע של השחקן

**ערך מוחזר:**
`None` (לולאה עד ניתוק או סיום)

**אלגוריתם:**
1. קבלת ה-`conn` (חיבור) מה-`_players[color]`
2. לולאה `async for raw in conn.websocket` (מקבל הודעות):
   - אם `_game_over_sent`: break (המשחק הסתיים)
   - ניסיון ל-`parse(json.loads(raw))` להודעת dataclass
   - אם שגיאה: שליחת `ErrorMsg` והמשך
   - קריאה ל-`_handle(color, msg)` לטיפול בהודעה
   - אם שגיאה לא צפויה: לוג והמשך
3. אם `ConnectionClosed` (החיבור נסגר):
   - אם המשחק לא הסתיים: קריאה ל-`_disconnect_countdown(color)`

**פרטי מימוש חשובים:**
- `async for` מקבל הודעות בצורה אסינכרונית
- שגיאות parsing לא מפסיקות את הלולאה
- ניתוק מפעיל ספירת זמן חסד

**מתי נקרא:**
בתוך `run()` דרך `asyncio.gather()` - פעמיים (לכל צבע)

**מי קורא:**
`run()` מתחיל את הלולאות

**8. `async def _disconnect_countdown(self, disconnected_color: str) -> None:`**

**תפקיד:**
ספירת זמן חסד כאשר שחקן מתנתק.

**מדוע קיים:**
לתת לשחקן סיכוי להתחבר מחדש לפני הפסד אוטומטי.

**פרמטרים:**
- `disconnected_color: str` - הצבע של השחקן שהתנתק

**ערך מוחזר:**
`None`

**אלגוריתם:**
1. קבלת הצבע השני (`other_color`)
2. קבלת החיבור של הצבע השני (`other_conn`)
3. לולאה מ-`DISCONNECT_GRACE_S` (20) ל-1:
   - אם `_game_over_sent`: חזרה (המשחק כבר הסתיים)
   - שליחת `OpponentDisconnectedMsg` עם הזמן הנותר
   - `await asyncio.sleep(1)` - המתנה לשנייה
4. אם הגיע ל-0 והמשחק לא הסתיים:
   - סימון `_game_over_sent = True`
   - קביעת המנצח (השחקן השני) והמפסיד (זה שהתנתק)
   - קריאה ל-`rating_service.apply_game_result()`
   - שליחת `GameOverMsg` לכולם

**פרטי מימוש חשובים:**
- `DISCONNECT_GRACE_S = 20` שניות
- שולח הודעת ספירה כל שנייה לשחקן השני
- השחקן שהתנתק מפסיד (forfeit)

**מתי נקרא:**
כאשר `_receive_loop()` מזהה `ConnectionClosed`

**מי קורא:**
`_receive_loop()` כאשר חיבור נסגר

**9. `async def _handle(self, color: str, msg) -> None:`**

**תפקיד:**
טיפול בהודעה ספציפית משחקן.

**מדוע קיים:**
לטפל בבקשות תנועה וקפיצה.

**פרמטרים:**
- `color: str` - הצבע של השולח
- `msg` - ההודעה עצמה

**ערך מוחזר:**
`None`

**אלגוריתם:**
1. קבלת ה-`conn` (חיבור) של השולח
2. אם `MoveMsg`:
   - המרת `from_cell` ל-`tuple`
   - חיפוש הקטע בתא ההתחלה
   - אם אין קטע או הקטע לא של השחקן: שליחת `ErrorMsg`
   - אם `apply_move()` הצליחה: שידור `MoveAckMsg` לכולם
3. אם `JumpMsg`:
   - המרת `cell` ל-`tuple`
   - חיפוש הקטע בתא
   - אם אין קטע או הקטע לא של השחקן: שליחת `ErrorMsg`
   - אם `apply_jump()` הצליחה: שידור `JumpAckMsg` לכולם

**פרטי מימוש חשובים:**
- `apply_move()` ו-`apply_jump()` מ-`serializer.py`
- הבדיקה `piece.color != color.value` מונעת מהלכים של היריב
- ה-`AckMsg` נשלחת לכולם (גם ליריב)

**מתי נקרא:**
עבור כל הודעה שהתקבלה מ-`_receive_loop()`

**מי קורא:**
`_receive_loop()` לאחר parsing של הודעה

**10. `async def _broadcast(self, msg) -> None:`**

**תפקיד:**
שידור הודעה לכל השחקנים והצופים.

**מדוע קיים:**
לשלוח עדכונים לכולם בבת אחת.

**פרמטרים:**
- `msg` - ההודעה לשליחה

**ערך מוחזר:**
`None`

**אלגוריתם:**
1. יצירת רשימה של כל החיבורים: `list(self._players.values()) + self._spectators`
2. עבור כל `conn`:
   - ניסיון `await conn.send(msg)`
   - אם `ConnectionClosed`: דילוג (החיבור נסגר)

**פרטי מימוש חשובים:**
- שימוש ב-`list()` כדי לא לשנות את ה-dict תוך כדי איטרציה
- `try-except` מגן מפני חיבורים שנסגרו בין הרגע
- הצופים מקבלים את אותן הודעות כמו השחקנים

**מתי נקרא:**
לשליחת `StateUpdateMsg`, `GameOverMsg`, `MoveAckMsg`, `JumpAckMsg`

**מי קורא:**
`_tick_loop()` ו-`_handle()` כאשר צריך לשלוח לכולם

### 📄 server/rating/elo.py

בואו נסתכל על חישוב ELO: