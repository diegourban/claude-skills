# Problem bank

Ten original problems, two per category, each solvable out loud in under ten minutes by an engineer
at the target level. `scripts/report.py pick` reads the `## <id>` headings and `Category:` lines, so
keep that shape when adding problems.

Every model solution fits in 15 lines (helpers may be named and elided). Per problem: **Say** is the
statement Leslie reads (adapt the wording, keep the facts). **Reveal on
ask** holds constraints Leslie gives only when the candidate asks a question that reaches them;
asking is rated under clarifying. **Tests** are the hidden inputs for the trace step; Leslie picks
the edge case. **Hints** are given in order, one per "hint". **Model solution** goes in the report.

Categories: `counting`, `window`, `intervals-heap`, `design`, `logs`.

## first-unique-visitor: First one-time visitor
Category: counting

**Say:** "You get a list of visitor IDs in the order they arrived. Return the first ID that appears
exactly once in the whole list."

**Reveal on ask:** IDs are strings. The list can be empty, or have no one-time visitor: return null
(or None). Up to a few million entries, fits in memory.

**Tests:**
- `["a","b","a","c","b"]` → `"c"`
- `["a","a"]` → null (edge: no one-time visitor)
- `[]` → null (edge: empty)

**Hints:**
1. "What would you need to know about each ID before you can answer?"
2. "Could one pass collect counts, and a second pass find the answer?"
3. "Count with a hash map, then walk the list again in order and return the first ID whose count is one."

**Follow-ups:** "The IDs now arrive as an endless stream and you must answer after each one." (insertion-
ordered map or a queue of candidates plus counts, popping repeated heads.)

**Model solution:** count occurrences in a `HashMap<String, Integer>`, then iterate the original list
and return the first ID with count 1. Time O(n), space O(k) for k distinct IDs.

```java
static String firstUnique(List<String> ids) {
    Map<String, Integer> counts = new HashMap<>();
    for (String id : ids) counts.merge(id, 1, Integer::sum);
    for (String id : ids) if (counts.get(id) == 1) return id;
    return null;
}
```

## inbox-groups: Group addresses by inbox
Category: counting

**Say:** "You get a list of email addresses. Some providers ignore dots in the local part and
everything after a plus sign, so `jo.ann+news@mail.com` and `joann@mail.com` reach the same inbox.
Group the addresses that reach the same inbox."

**Reveal on ask:** The rule applies to every domain in this problem. Comparison is case-insensitive.
Return groups in any order; inside a group keep input order. Every address has exactly one `@`.

**Tests:**
- `["jo.ann+news@mail.com","joann@mail.com","bob@mail.com"]` → `[[jo.ann+news@mail.com, joann@mail.com], [bob@mail.com]]`
- `["A.B@x.com","ab@X.COM"]` → one group (edge: case)
- `["+tag@x.com"]` → one group keyed by an empty local part (edge: nothing before the plus)

**Hints:**
1. "What would make two addresses equal for this problem?"
2. "What would two addresses of the same inbox have in common once you clean them up?"
3. "Lower-case it, cut the local part at the first plus, remove dots, then group by key in a map."

**Follow-ups:** "Now the dot rule applies to only one domain." (key function takes the domain into
account; the grouping is unchanged.)

**Model solution:** normalise each address to a key (lower-case, local part up to the first `+`,
dots removed, plus the domain) and group with a `LinkedHashMap<String, List<String>>`. Time and space
O(total characters across all addresses).

```java
static Collection<List<String>> groupByInbox(List<String> emails) {
    Map<String, List<String>> groups = new LinkedHashMap<>();
    for (String email : emails) {
        String lower = email.toLowerCase();
        int at = lower.indexOf('@');
        String local = lower.substring(0, at);
        int plus = local.indexOf('+');
        if (plus >= 0) local = local.substring(0, plus);
        String key = local.replace(".", "") + lower.substring(at);
        groups.computeIfAbsent(key, k -> new ArrayList<>()).add(email);
    }
    return groups.values();
}
```

## longest-focused-session: Longest stretch with few distinct pages
Category: window

**Say:** "A user's clickstream is a list of page IDs in order. Find the length of the longest
contiguous stretch that touches at most K distinct pages."

**Reveal on ask:** K is at least 1. The list can be empty (answer 0). Page IDs are strings. Up to a
million clicks, so something better than checking every stretch is expected.

**Tests:**
- `["home","search","home","cart","cart"]`, K=2 → 3 (`home,search,home` or `home,cart,cart`: both 3)
- `["a","b","c"]`, K=5 → 3 (edge: K larger than the distinct count)
- `[]`, K=1 → 0 (edge: empty)

**Hints:**
1. "If a stretch is valid, is every stretch inside it valid too?"
2. "Keep a window with two ends and grow the right end; when is it time to move the left one?"
3. "Count pages in the window with a map; when the map has more than K keys, shrink from the left, removing keys that hit zero."

**Follow-ups:** "Return the stretch itself, not just its length." (track the best left index.)

**Model solution:** sliding window with a `HashMap<String, Integer>` of counts; advance the right end,
and while the map has more than K keys advance the left end and decrement, removing zero counts.
Track the maximum width. Time O(n), space O(K).

```java
static int longest(List<String> pages, int k) {
    Map<String, Integer> inWindow = new HashMap<>();
    int best = 0, left = 0;
    for (int right = 0; right < pages.size(); right++) {
        inWindow.merge(pages.get(right), 1, Integer::sum);
        while (inWindow.size() > k) {
            String out = pages.get(left++);
            if (inWindow.merge(out, -1, Integer::sum) == 0) inWindow.remove(out);
        }
        best = Math.max(best, right - left + 1);
    }
    return best;
}
```

## closest-budget-pair: Two ads closest to the budget
Category: window

**Say:** "You get ad slot prices, sorted ascending, and a budget. Pick two different slots whose total
is as close to the budget as possible without going over. Return the total."

**Reveal on ask:** Prices are positive integers (a sum may exceed `int`; use `long` if asked). Return -1 when no pair fits. Two slots can have the
same price but are different slots. Up to a million prices.

**Tests:**
- `[10,20,30,45]`, budget 52 → 50
- `[10,20]`, budget 25 → -1 (edge: every pair over budget)
- `[15,15]`, budget 30 → 30 (edge: equal prices, exact hit)

**Hints:**
1. "The list is sorted. What does that let you skip?"
2. "Start one pointer at each end. If the pair is over budget, which pointer should move?"
3. "Over budget: move the right pointer left. Within budget: record it and move the left pointer right. Stop when they meet."

**Follow-ups:** "The prices arrive unsorted." (sort first, O(n log n); or a TreeSet floor lookup.)

**Model solution:** two pointers from both ends; if `price[l] + price[r]` exceeds the budget move `r`
left, otherwise record the best total and move `l` right. Time O(n), space O(1).

```java
static int closestPair(int[] prices, int budget) {
    int l = 0, r = prices.length - 1, best = -1;
    while (l < r) {
        int sum = prices[l] + prices[r];
        if (sum > budget) r--;
        else { best = Math.max(best, sum); l++; }
    }
    return best;
}
```

## merge-maintenance-windows: Merge maintenance windows
Category: intervals-heap

**Say:** "Teams book maintenance windows as start and end times. Merge them so we get the list of
periods when anything is in maintenance."

**Reveal on ask:** Windows are half-open, start inclusive and end exclusive, so `[1,3)` and `[3,5)`
touch and merge into `[1,5)`. Input is unsorted. Times are integers, start < end. Empty input gives an
empty list.

**Tests:**
- `[[1,3],[2,6],[8,10]]` → `[[1,6],[8,10]]`
- `[[3,5],[1,3]]` → `[[1,5]]` (edge: unsorted and touching)
- `[[1,10],[2,3]]` → `[[1,10]]` (edge: one window inside another)

**Hints:**
1. "What order would make overlaps easy to spot?"
2. "Sort by start. When does the next window join the current one?"
3. "After sorting, extend the current window's end with max(end, next end) while next start <= current end; otherwise start a new one."

**Follow-ups:** "Windows now arrive one at a time and you must keep the merged list up to date."
(a TreeMap keyed by start, merging neighbours on insert.)

**Model solution:** sort by start; walk the list, merging while the next start is at or before the
current end (touching counts) and taking the larger end. Time O(n log n), space O(n) for the output.

```java
static List<int[]> merge(List<int[]> windows) {
    List<int[]> sorted = new ArrayList<>(windows);
    sorted.sort(Comparator.comparingInt(w -> w[0]));
    List<int[]> out = new ArrayList<>();
    for (int[] w : sorted) {
        int[] last = out.isEmpty() ? null : out.get(out.size() - 1);
        if (last != null && w[0] <= last[1]) last[1] = Math.max(last[1], w[1]);
        else out.add(new int[] {w[0], w[1]});
    }
    return out;
}
```

## top-k-campaigns: Top campaigns by clicks
Category: intervals-heap

**Say:** "You get click events, each a campaign ID and a click count. Return the K campaigns with the
most total clicks."

**Reveal on ask:** A campaign appears many times; sum its counts. Ties break by campaign ID
alphabetically. If there are fewer than K campaigns, return them all. Many events, few distinct
campaigns relative to events.

**Tests:**
- `[(a,5),(b,3),(a,1),(c,4)]`, K=2 → `[a, c]`
- `[(b,2),(a,2)]`, K=1 → `[a]` (edge: tie breaks alphabetically)
- `[(a,1)]`, K=3 → `[a]` (edge: fewer than K)

**Hints:**
1. "Two jobs here: totals per campaign, then the best K. Take them one at a time."
2. "For the best K, do you need to sort everything?"
3. "Sum in a map, then keep a min-heap of size K ordered by total (and ID for ties); evict the smallest when it grows past K."

**Follow-ups:** "The events never stop and you need the top K every minute." (keep the totals map;
recompute the heap per minute, or bucket by count if counts are small.)

**Model solution:** totals in a `HashMap`, then a min-heap of size K whose comparator orders by total
ascending and, on ties, by ID descending, so the weakest entry is on top; drain and reverse. Time
O(n + m log K) for n events and m campaigns, space O(m).

```java
static List<String> topK(List<Map.Entry<String, Integer>> events, int k) {
    Map<String, Integer> totals = new HashMap<>();
    for (var e : events) totals.merge(e.getKey(), e.getValue(), Integer::sum);
    Comparator<String> weakestFirst = Comparator.<String>comparingInt(totals::get)
            .thenComparing(Comparator.<String>reverseOrder());
    PriorityQueue<String> heap = new PriorityQueue<>(weakestFirst);
    for (String id : totals.keySet()) { heap.add(id); if (heap.size() > k) heap.poll(); }
    List<String> out = new ArrayList<>();
    while (!heap.isEmpty()) out.add(heap.poll());
    Collections.reverse(out);
    return out;
}
```

## lru-cache: LRU cache
Category: design

**Say:** "Design a fixed-capacity cache with get and put, both constant time, that evicts the least
recently used entry when full. Describe the structures, then talk me through put."

**Reveal on ask:** `get` returns the value or nothing. A `get` counts as a use. A `put` on an existing key updates the value and counts
as a use. Capacity is at least 1. Single-threaded.

**Tests:**
- capacity 2: put(a), put(b), get(a), put(c) → b is evicted, a and c remain
- capacity 1: put(a), put(b) → only b remains (edge: capacity one)
- capacity 2: put(a,1), put(a,2), put(b), put(c) → a is evicted (its last use, the update, is older than b), get(a) is empty and get(b) is present (edge: an update is a use, but still ages out)

**Hints:**
1. "Constant-time lookup by key suggests one structure. What tracks recency in constant time?"
2. "A doubly linked list can move or remove a node in O(1) if you can find the node."
3. "Map key to list node; on use, move the node to the front; on overflow, remove the tail node and its key."

**Follow-ups:** "Several threads now share the cache." (one lock around both structures, or striped
caches; LinkedHashMap with access order is the library shortcut.)

**Model solution:** a `HashMap<K, Node>` plus a doubly linked list ordered by recency, with sentinel
head and tail. `get` moves the node to the front; `put` inserts or updates at the front and, past
capacity, unlinks the tail node and removes its key. O(1) per operation, O(capacity) space.

```java
class LruCache<K, V> {
    private final int capacity;
    private final Map<K, Node<K, V>> index = new HashMap<>();
    private final Node<K, V> head = new Node<>(null, null), tail = new Node<>(null, null);
    LruCache(int capacity) { this.capacity = capacity; head.next = tail; tail.prev = head; }
    V get(K key) { Node<K, V> n = index.get(key); if (n == null) return null; unlink(n); pushFront(n); return n.value; }
    void put(K key, V value) {
        Node<K, V> n = index.get(key);
        if (n != null) { n.value = value; unlink(n); pushFront(n); return; }
        if (index.size() == capacity) { Node<K, V> lru = tail.prev; unlink(lru); index.remove(lru.key); }
        n = new Node<>(key, value); index.put(key, n); pushFront(n);
    }
    // unlink, pushFront and the Node record are a few lines each.
}
```

## fixed-window-limiter: Per-user rate limiter
Category: design

**Say:** "Write `allow(userId, timestampSeconds)`. Each user may make at most N requests per minute.
Return true if this request is allowed."

**Reveal on ask:** Minutes are fixed windows aligned to the clock, `timestamp / 60`. Timestamps per
user arrive in non-decreasing order. A rejected request does not count. Many users, single node.

**Tests:**
- N=2: (u,0) true, (u,10) true, (u,59) false, (u,60) true (edge: new window at 60)
- N=1: (u,5) true, (v,5) true (edge: users are independent)
- N=1: (u,119) true, (u,120) true (edge: window boundary)

**Hints:**
1. "What do you need to remember per user?"
2. "How would you know a new minute has started for that user?"
3. "Map user to (window, count) with window = timestamp / 60; if the window changed, reset the count; allow while count < N."

**Follow-ups:** "Bursts at the window edge let a user make 2N requests in two seconds. Fix it."
(sliding log of timestamps per user, or a token bucket with refill rate N per minute.)

**Model solution:** a map from user to `{window, count}`. Compute `window = timestamp / 60`; reset the
count when the window differs; allow and increment while the count is below N. O(1) per call, O(users)
space. A stale-user eviction is worth naming.

```java
class FixedWindowLimiter {
    private final int limit;
    private final Map<String, long[]> state = new HashMap<>(); // {window, count}
    FixedWindowLimiter(int limit) { this.limit = limit; }
    boolean allow(String user, long ts) {
        long window = ts / 60;
        long[] s = state.computeIfAbsent(user, u -> new long[] {window, 0});
        if (s[0] != window) { s[0] = window; s[1] = 0; }
        if (s[1] >= limit) return false;
        s[1]++;
        return true;
    }
}
```

## slowest-endpoints: Slowest endpoints from access logs
Category: logs

**Say:** "You get access log lines like `2026-11-24T10:00:01Z GET /orders 200 123ms`. Return the three
endpoints with the highest average latency."

**Reveal on ask:** An endpoint is method plus path. Count only 2xx responses. Skip malformed lines
instead of failing. Fewer than three endpoints: return what there is. Ties in any order.

**Tests** (each line also starts with a timestamp, left out here):
- `GET /a 200 100ms`, `GET /a 200 300ms`, `GET /b 200 150ms` → `[GET /a, GET /b]`
- `GET /a 200 100ms`, `garbage`, `GET /b 200 150ms` → `[GET /b, GET /a]` (edge: malformed line skipped)
- `GET /a 500 900ms`, `GET /a 200 100ms`, `GET /b 200 150ms` → `[GET /b, GET /a]` (edge: the 500 is ignored, so /a averages 100)

**Hints:**
1. "Split the problem: parse a line, aggregate, then rank."
2. "What do you need per endpoint to compute an average?"
3. "Keep sum and count per endpoint in a map, then sort the endpoints by sum/count, descending, and take three."

**Follow-ups:** "Product wants p95, not the average." (keep the latencies per endpoint and select the
95th percentile, or a histogram if memory is tight.)

**Model solution:** split each line on spaces; skip it unless it has five fields, a status between 200
and 299 and a latency ending in `ms`; aggregate sum and count per `method + " " + path`; sort by average descending
and take three. Time O(n + m log m), space O(m) for m endpoints.

```java
static List<String> slowest(List<String> lines) {
    Map<String, long[]> agg = new HashMap<>(); // {sum, count}
    for (String line : lines) {
        String[] f = line.trim().split("\\s+");
        if (f.length != 5 || !f[3].matches("2\\d\\d") || !f[4].matches("\\d+ms")) continue;
        long[] a = agg.computeIfAbsent(f[1] + " " + f[2], k -> new long[2]);
        a[0] += Long.parseLong(f[4].substring(0, f[4].length() - 2)); a[1]++;
    }
    return agg.entrySet().stream()
            .sorted((x, y) -> Double.compare(avg(y.getValue()), avg(x.getValue())))
            .limit(3).map(Map.Entry::getKey).toList();
}

static double avg(long[] sumCount) { return (double) sumCount[0] / sumCount[1]; }
```

## sessions-per-user: Count sessions per user
Category: logs

**Say:** "You get event lines `userId,timestampSeconds,eventName`, not in any order. A user's session
ends after 30 minutes with no events. Return how many sessions each user had."

**Reveal on ask:** 30 minutes means a gap strictly greater than 1800 seconds starts a new session; a
gap of exactly 1800 continues it. Lines are well formed. Many users, events fit in memory.

**Tests:**
- `u,0,a`, `u,1000,b`, `u,5000,c` → `{u: 2}`
- `u,1800,b`, `u,0,a` → `{u: 1}` (edge: unsorted input, gap of exactly 1800)
- `u,0,a`, `v,0,a` → `{u: 1, v: 1}` (edge: users are independent)

**Hints:**
1. "How would you find one user's gaps if you only had that user's events?"
2. "Group timestamps by user, then look at each user's events in time order."
3. "Map user to a list of timestamps, sort each list, and count one session plus one per gap over 1800."

**Follow-ups:** "The events now stream in roughly time order and you can't hold them all." (per user,
keep only the last timestamp and the session count; handle late events with a small reorder buffer.)

**Model solution:** group timestamps per user in a map, sort each list, then sessions = 1 + number of
consecutive gaps greater than 1800. Time O(n log n), space O(n).

```java
static Map<String, Integer> sessions(List<String> lines) {
    Map<String, List<Long>> byUser = new HashMap<>();
    for (String line : lines) {
        String[] f = line.split(",");
        byUser.computeIfAbsent(f[0], k -> new ArrayList<>()).add(Long.parseLong(f[1]));
    }
    Map<String, Integer> out = new HashMap<>();
    byUser.forEach((user, ts) -> {
        Collections.sort(ts);
        int count = 1;
        for (int i = 1; i < ts.size(); i++) if (ts.get(i) - ts.get(i - 1) > 1800) count++;
        out.put(user, count);
    });
    return out;
}
```
