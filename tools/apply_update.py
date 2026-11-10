"""Apply a shop-list update (from a GitHub issue body) to shops.json."""
import json, re, sys, datetime

body = open(sys.argv[1], encoding="utf-8").read()
m = re.search(r"```json\s*(\{.*?\})\s*```", body, re.S)
if not m:
    sys.exit("找不到更新內容（```json ... ```）")
upd = json.loads(m.group(1))
FILE = upd.get("file", "shops_l.json")
if FILE not in ("shops_b.json", "shops_l.json", "shops_d.json"):
    sys.exit("檔案名稱不正確：" + FILE)
data = json.load(open(FILE, encoding="utf-8"))
shops = data["shops"]
by_id = {s["id"]: s for s in shops}
FIELDS = ["n", "c", "cat", "p", "h", "la", "ln", "r", "v", "walk", "link", "dish", "tel"]
log = []

for a in upd.get("add", []):
    if not a.get("id") or not a.get("n"):
        continue
    rec = {"id": a["id"], **{k: a.get(k) for k in FIELDS if a.get(k) is not None}}
    if a["id"] in by_id:
        by_id[a["id"]].update(rec); log.append(f"更新 {a['n']}")
    else:
        shops.append(rec); by_id[a["id"]] = rec; log.append(f"新增 {a['n']}")

for sid, e in upd.get("edit", {}).items():
    if sid in by_id:
        for k in FIELDS:
            if k in e:
                if e[k] is None:
                    by_id[sid].pop(k, None)
                else:
                    by_id[sid][k] = e[k]
        log.append(f"修改 {by_id[sid]['n']}")

hide = set(upd.get("hide", []))
for s in [s for s in shops if s["id"] in hide]:
    log.append(f"移除（歇業）{s['n']}")
data["shops"] = [s for s in shops if s["id"] not in hide]

# basic validation
for s in data["shops"]:
    assert isinstance(s.get("n"), str) and s["n"].strip(), "店名不可空白"
    assert isinstance(s.get("h"), list) and len(s["h"]) == 7, f"{s['n']} 營業時間格式錯誤"
    assert s.get("p") in (1, 2, 3), f"{s['n']} 價位只能是 1、2 或 3"

if not log:
    open("apply_log.txt", "w", encoding="utf-8").write("沒有變更")
    print("沒有變更"); sys.exit(0)

data["updated"] = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime("%Y-%m-%d %H:%M")
json.dump(data, open(FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
open("apply_log.txt", "w", encoding="utf-8").write("\n".join(log) or "沒有變更")
print("\n".join(log))
