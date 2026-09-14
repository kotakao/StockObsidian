#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
new_note.py — vault 筆記「骨架」產生器(只生結構,內容由後續填入)。

為什麼存在:把 7 種模板的「frontmatter / 代碼優先命名 / 資料夾 / 麵包屑 / 章節骨架」
程式化產生,避免每次手打(省 token)且消滅檔名編碼、幽靈連結、放錯資料夾等錯誤。

設計原則:
- 只產生「結構」;數據/分析由人(或 Claude)之後填入,一律標來源、不虛構。
- 個股/ETF 檔名一律「代碼優先」:個股_<代碼>_<名>.md、ETF_<代碼>_<名>.md。
- 事件/分析/報告/決策自動放進 分析報告/YYYY/MM/第N週/(週依實際日期,週一為界)。
- 路徑依型別自動推定,可用 --out 覆寫(相對 vault 根,或絕對路徑)。
- 拒絕覆蓋既有檔(要覆蓋加 --force);成功只印出建立的相對路徑(stdout 精簡)。

7 種型別:stock / etf / sector / event / analysis / report / decision

範例:
  python scripts/new_note.py stock --ticker 6515 --name 穎崴 --sector '[[族群_半導體測試與介面]]' --en WinWay --tag 測試介面
  python scripts/new_note.py etf --ticker 0050 --name 元大台灣50 --held --tag 市值型
  python scripts/new_note.py sector --topic 光通訊與CPO --baton 第二棒 --confidence 中 --tag 光通訊
  python scripts/new_note.py event --title 台積電ASML_12吋光罩 --related '[[個股_2330_台積電]]' --related '[[族群_晶圓代工與先進封裝]]'
  python scripts/new_note.py analysis --title 功率元件之後的下一棒
  python scripts/new_note.py report --title TOP追蹤 --tracks '[[個股_6515_穎崴]]'
  python scripts/new_note.py decision --ticker 6515 --name 穎崴 --action 觀望
"""
import argparse
import sys
import datetime
from pathlib import Path

try:  # Windows 主控台以 UTF-8 輸出,避免中文路徑/訊息在終端變亂碼(檔案內容一律 UTF-8)
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

VAULT = Path(__file__).resolve().parent.parent          # scripts/ 的上一層 = vault 根
INDEX = "[[族群輪動索引_AI供應鏈]]"
PORTFOLIO = "[[我的持股_Portfolio]]"
DISCLAIMER = "非投資建議。"
REPORTS = "分析報告"
CN_NUM = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六"}


def today() -> str:
    return datetime.date.today().isoformat()


def parse_date(s: str) -> datetime.date:
    return datetime.date.fromisoformat(s) if s else datetime.date.today()


def yaml_flow(items) -> str:
    """YAML flow list:[a, "b", c];空值略過。"""
    return "[" + ", ".join(str(x) for x in items if x not in (None, "")) + "]"


def yaml_block(key: str, items) -> str:
    """YAML block list(link 用,加引號):key:\\n  - \"[[..]]\"。空則 key: []。"""
    items = [x for x in items if x]
    if not items:
        return f"{key}: []\n"
    return f"{key}:\n" + "".join(f'  - "{x}"\n' for x in items)


def week_folder(d: datetime.date) -> str:
    """分析報告/YYYY/MM/第N週(週一為界,含 1 號的首週為第一週)。"""
    first_wd = datetime.date(d.year, d.month, 1).weekday()   # Mon=0..Sun=6
    n = (d.day - 1 + first_wd) // 7 + 1
    return f"{REPORTS}/{d.year:04d}/{d.month:02d}/第{CN_NUM.get(n, str(n))}週"


def resolve_out(relpath: str, out: str) -> Path:
    if not out:
        return VAULT / relpath
    p = Path(out)
    return p if p.is_absolute() else VAULT / p


def write_note(target: Path, content: str, force: bool):
    if target.exists() and not force:
        sys.exit(f"[拒絕] 已存在,未覆蓋:{target}(要覆蓋加 --force)")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    try:
        print(target.relative_to(VAULT).as_posix())
    except ValueError:
        print(str(target))


# ============ 模板 ============
def build_stock(a):
    created, dd = a.created or today(), a.data_date or today()
    aliases = [a.name, f'"{a.ticker}"'] + ([a.en] if a.en else []) + a.alias
    tags = a.tag if "個股筆記" in a.tag else ["個股筆記"] + a.tag
    sector = a.sector or "待補(族群未建則用純文字,勿留幽靈連結)"
    sec_crumb = f"｜族群:{a.sector}" if a.sector else ""
    fm = ("---\n" "type: stock\n" f'ticker: "{a.ticker}"\n' f'sector: "{sector}"\n'
          f"aliases: {yaml_flow(aliases)}\n" f"tags: {yaml_flow(tags)}\n"
          f"created: {created}\n" f"data_date: {dd}\n" "---\n")
    body = (f"\n# {a.name}({a.ticker})\n\n"
            f"> 索引:{INDEX}{sec_crumb}\n"
            f"> 資料日 {dd}(taiwan-stock MCP,TWSE/TPEX 官方;月營收 MOPS)。{DISCLAIMER}\n\n"
            "## 供應鏈定位\n\n"
            "## 基本面追蹤(月營收/季損益,附來源+日期)\n- ⏳ 待撈〔源A/B〕。\n\n"
            "## 籌碼追蹤(三大法人,單位:張,股÷1000 概算)\n- ⏳ 待撈〔源A〕。\n\n"
            "## 我的持倉\n- 無。\n\n"
            "## 重大事件時間軸\n\n"
            "## 關聯事件 / 報告\n\n"
            "## 疑點與待查證清單\n- [ ] \n\n"
            "## 公司背景(以年報/官網為準,不確定標待查)\n"
            "- 成立 / 上市:待查〔上市日 get_company_profile,源A〕。\n"
            "- 經營層:待查(以最新年報為準)。\n- 本業一句話:\n\n"
            "## 詳細業務\n- 主要產品線:\n- 應用 / 客戶:\n")
    return f"個股/個股_{a.ticker}_{a.name}.md", fm + body


def build_etf(a):
    created, dd = a.created or today(), a.data_date or today()
    aliases = [a.name, f'"{a.ticker}"'] + ([a.en] if a.en else []) + a.alias
    tags = list(a.tag)
    if "ETF筆記" not in tags:
        tags = ["ETF筆記"] + tags
    if a.held and "持股" not in tags:
        tags.append("持股")
    held_crumb = f"｜持股:{PORTFOLIO}" if a.held else ""
    fm = ("---\n" "type: etf\n" f'ticker: "{a.ticker}"\n'
          f"aliases: {yaml_flow(aliases)}\n" f"tags: {yaml_flow(tags)}\n"
          f"created: {created}\n" f"data_date: {dd}\n" "---\n")
    body = (f"\n# {a.name}({a.ticker})\n\n"
            f"> 索引:{INDEX}{held_crumb}\n"
            f"> 資料日 {dd}(taiwan-stock MCP,TWSE 官方)。{DISCLAIMER}\n\n"
            "## 定位\n\n"
            "## 與 AI / 我的部位的關係\n\n"
            f"## 我的持倉〔{PORTFOLIO}〕\n- {'見 ' + PORTFOLIO if a.held else '無'}。\n\n"
            "## 待查證\n- [ ] 成分權重 / 費用率(發行商月報)。\n")
    return f"ETF/ETF_{a.ticker}_{a.name}.md", fm + body


def build_sector(a):
    created, dd = a.created or today(), a.data_date or today()
    tags = list(a.tag)
    for base in ("族群筆記", "AI供應鏈"):
        if base not in tags:
            tags = [base] + tags if base == "族群筆記" else tags + [base]
    ev_crumb = f"｜事件:{a.event}" if a.event else ""
    h1 = a.h1 or f"族群｜{a.topic}"
    fm = ("---\n" "type: sector\n" f"sector_name: {a.topic}\n" f"baton: {a.baton}\n"
          f"confidence: {a.confidence}\n" f"tags: {yaml_flow(tags)}\n"
          f"created: {created}\n" f"data_date: {dd}\n" "---\n")
    body = (f"\n# {h1}\n\n"
            f"> 索引:{INDEX}{ev_crumb}\n"
            f"> 資料日 {dd}(taiwan-stock MCP,TWSE/TPEX 官方;月營收 MOPS;產業 WebSearch 可靠度?)。{DISCLAIMER}\n\n"
            "## 一句話定位\n\n"
            "## 輪動位階\n- 位階(第幾棒)+信心度;對應輪動規律 R?。【事實/推測】\n\n"
            "## 產業瓶頸與催化〔源C,可靠度?〕\n\n"
            "## 代表股\n"
            "| 標的 | 定位 | 月營收(YYYY-MM)〔源B〕 | 籌碼(至 YYYY-MM-DD)〔源A〕 | 真受惠? |\n"
            "|---|---|---|---|---|\n"
            "|  |  |  |  |  |\n\n"
            "## 進場觀察 / 否證\n\n"
            "## 待查證\n- [ ] \n")
    return f"族群/族群_{a.topic}.md", fm + body


def build_event(a):
    d = parse_date(a.date)
    ds, dd = d.isoformat(), a.data_date or (a.date or today())
    ev = a.event_name or a.title
    tags = a.tag if "事件筆記" in a.tag else ["事件筆記"] + a.tag
    fm = ("---\n" f"date: {ds}\n" f"data_date: {dd}\n" "type: event\n"
          f"event_name: {ev}\n" + yaml_block("related", a.related)
          + f"tags: {yaml_flow(tags)}\n" "---\n")
    body = (f"\n# {ds} {a.title}\n\n"
            f"> 索引:{INDEX}。資料日 {dd}(taiwan-stock MCP,TWSE/TPEX 官方;產業 WebSearch 可靠度?)。{DISCLAIMER}\n\n"
            "## 已證實事實(逐項附官方來源+日期)\n\n"
            "## 未證實傳聞(明確標示未證實)\n\n"
            "## 對相關標的的影響評估(【事實】/【推測】+信心度)\n\n"
            "## 後續觀察點(一次性驚嚇 vs 基本面質變的關鍵訊號)\n")
    return f"{week_folder(d)}/{ds}_事件_{a.title}.md", fm + body


def build_analysis(a):
    d = parse_date(a.date)
    ds, dd = d.isoformat(), a.data_date or (a.date or today())
    tags = list(a.tag) or ["市場分析", "族群輪動", "AI供應鏈"]
    fm = ("---\n" "type: analysis\n" f"title: AI 供應鏈資金輪動 — {a.title}\n"
          f"date: {ds}\n" f"data_date: {dd}\n" f"horizon: {a.horizon}\n"
          + yaml_block("tags", tags).replace('  - "', '  - ').replace('"\n', '\n') + "---\n")
    body = (f"\n# {a.title}\n\n"
            f"> **投資時間框架**:{a.horizon},以「哪個族群最可能成為資金新主流」為核心。\n"
            "> **資料誠實聲明**:族群輪動的產業與籌碼邏輯研究,非投資建議。判斷標【事實】/【推測】+信心度;數字附來源與日期,查不到標待撈。\n"
            f"> **相關筆記**:{INDEX}\n\n"
            "## 資料來源代號\n〔源A〕MCP 行情+三大法人;〔源B〕MCP 月營收(MOPS);〔源C〕WebSearch 新聞(標可靠度)。\n\n"
            "# STEP 1｜背景確認(壓縮,600 字內)\n## 1A. 全球 AI 產業周期定位\n## 1B. 美股與總經環境\n\n"
            "# STEP 2｜資金輪動路徑回顧與交棒邏輯\n## 2A. 過去 3~6 個月輪動序列\n## 2B. 每次交棒的驅動邏輯\n## 2C. 本輪輪動規律(篩下一棒)\n\n"
            "# STEP 3｜下一棒候選族群推演\n## 3A. 目前主流的位階(初升/主升/末升段)\n## 3B. 候選族群評估(接棒四條件:基期/基本面/供應鏈邏輯/籌碼)\n## 3C. 結論:最可能的下一棒 2~3 族群(排序+觸發事件+信心度)\n\n"
            "# STEP 4｜族群內代表股(真受惠 vs 概念炒作)\n\n"
            "# STEP 5｜追蹤清單、進場條件與否證條件\n## 5A. TOP 3 追蹤標的\n## 5B. 條件式進場策略(以訊號而非價位)\n## 5C. 否證條件(每族群必附)\n## 5D. AI 行情整體反轉訊號\n\n"
            "## 一句話總結\n")
    return f"{week_folder(d)}/{ds}_市場分析_{a.title}.md", fm + body


def build_report(a):
    d = parse_date(a.date)
    ds, dd = d.isoformat(), a.data_date or (a.date or today())
    tags = list(a.tag)
    for base in ("收盤報告", "族群輪動", "AI供應鏈"):
        if base not in tags:
            tags.append(base)
    main_crumb = f"｜主分析:{a.main_analysis}" if a.main_analysis else ""
    fm = ("---\n" "type: report\n" "report_kind: 收盤報告\n" f"date: {ds}\n"
          f"data_date: {dd}\n" + yaml_block("tracks", a.tracks)
          + f"tags: {yaml_flow(tags)}\n" f"created: {ds}\n" "---\n")
    body = (f"\n# {ds} 收盤報告｜大盤 + TOP 追蹤\n\n"
            f"> 索引:{INDEX}{main_crumb}\n"
            f"> 資料日 {dd}(taiwan-stock MCP,TWSE/TPEX 官方)。籌碼單位為張(股÷1000)。{DISCLAIMER}\n\n"
            "## 一、大盤〔源A〕\n\n"
            "## 二、追蹤個股盤後〔源A〕\n### 逐檔解讀\n\n"
            "## 三、綜合判讀\n\n"
            "## 四、否證條件檢核(對照主分析 5C)\n\n"
            "## 五、明日觀察點\n\n"
            "## 待查證\n- [ ] \n")
    tail = f"_{a.title}" if a.title else ""
    return f"{week_folder(d)}/{ds}_收盤報告{tail}.md", fm + body


def build_decision(a):
    d = parse_date(a.date)
    ds = d.isoformat()
    label = a.name or a.ticker
    link = a.stock_link or (f"[[個股_{a.ticker}_{a.name}]]" if a.name else f"[[個股_{a.ticker}]]")
    tags = a.tag if "決策日誌" in a.tag else ["決策日誌"] + a.tag
    title = f"{a.name}({a.ticker})" if a.name else a.ticker
    fm = ("---\n" f"date: {ds}\n" "type: decision\n" f'ticker: "{a.ticker}"\n'
          f"action: {a.action}\n" f"tags: {yaml_flow(tags)}\n" "---\n")
    body = (f"\n# {ds} {title} 決策紀錄\n\n"
            f"> 索引:{INDEX}｜標的:{link}\n\n"
            f"- **動作**:{a.action}\n"
            "- **當時價格**:(來源+日期)\n"
            "- **決策理由**:(為什麼現在做這個決定)\n"
            "- **對應輪動邏輯**:(連回對應族群與規律 R?)\n"
            "- **當時的預期**:\n"
            "- **否證條件**:(出現什麼訊號代表判斷錯了)\n"
            "- **信心度**:高/中/低\n"
            "- **情緒檢查**:(基於分析,還是恐慌/貪婪?)\n")
    return f"{week_folder(d)}/{ds}_決策_{label}.md", fm + body


def build_news(a):
    d = parse_date(a.date)
    ds, dd = d.isoformat(), a.data_date or (a.date or today())
    tags = list(a.tag)
    for base in ("新聞彙整", "AI供應鏈"):
        if base not in tags:
            tags = ([base] + tags) if base == "新聞彙整" else (tags + [base])
    fm = ("---\n" "type: report\n" "report_kind: 新聞彙整\n" f"date: {ds}\n"
          f"data_date: {dd}\n" + yaml_block("tracks", a.tracks)
          + f"tags: {yaml_flow(tags)}\n" f"created: {ds}\n" "---\n")
    body = (f"\n# {ds} {a.title}\n\n"
            f"> 索引:{INDEX}。資料日 {dd}(taiwan-stock MCP 官方;產業 WebSearch)。"
            f"來源〔源C〕:標帳號/券商+可靠度。**券商=意見,EPS/目標價/需求數字待官方覆核。**{DISCLAIMER}\n\n"
            "## 一、券商評等 / 重點\n"
            "| 標的 | 券商 | 重點〔源C〕 | EPS / PE |\n|---|---|---|---|\n|  |  |  |  |\n\n"
            "## 二、產業 / 主題觀察\n\n"
            "## 三、官方籌碼對照〔源A〕\n"
            "| 標的 | 收盤 | 當日 | 外資 | 估值 |\n|---|--:|--:|--:|--:|\n|  |  |  |  |  |\n\n"
            "## 四、真受惠 vs 概念(信心度?)\n\n"
            "## 待查證\n- [ ] \n")
    return f"{week_folder(d)}/{ds}_新聞彙整_{a.title}.md", fm + body


BUILDERS = {"stock": build_stock, "etf": build_etf, "sector": build_sector,
            "event": build_event, "analysis": build_analysis,
            "report": build_report, "decision": build_decision, "news": build_news}


def main():
    p = argparse.ArgumentParser(description="vault 筆記骨架產生器(7 種模板)")
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--force", action="store_true", help="覆蓋既有檔")
    common.add_argument("--created", default="", help="建立日(常青筆記用;預設今天)")
    common.add_argument("--data-date", dest="data_date", default="", help="資料日(預設今天或 --date)")
    common.add_argument("--out", default="", help="覆寫輸出路徑(相對 vault 根或絕對)")
    common.add_argument("--tag", action="append", default=[], help="額外 tag,可重複")
    dated = argparse.ArgumentParser(add_help=False)
    dated.add_argument("--date", default="", help="事件/報告日 YYYY-MM-DD(預設今天;決定週資料夾與檔名)")

    sub = p.add_subparsers(dest="type", required=True)

    ps = sub.add_parser("stock", parents=[common], help="個股筆記")
    ps.add_argument("--ticker", required=True); ps.add_argument("--name", required=True)
    ps.add_argument("--sector", default=""); ps.add_argument("--en", default="")
    ps.add_argument("--alias", action="append", default=[])

    pe = sub.add_parser("etf", parents=[common], help="ETF 筆記")
    pe.add_argument("--ticker", required=True); pe.add_argument("--name", required=True)
    pe.add_argument("--en", default=""); pe.add_argument("--alias", action="append", default=[])
    pe.add_argument("--held", action="store_true", help="持有中(加持股 tag+麵包屑)")

    pc = sub.add_parser("sector", parents=[common], help="族群筆記")
    pc.add_argument("--topic", required=True, help="主題(檔名+sector_name+H1)")
    pc.add_argument("--baton", default="觀察"); pc.add_argument("--confidence", default="中")
    pc.add_argument("--event", default=""); pc.add_argument("--h1", default="")

    pv = sub.add_parser("event", parents=[common, dated], help="事件筆記")
    pv.add_argument("--title", required=True, help="主題(檔名+H1)")
    pv.add_argument("--event-name", dest="event_name", default="")
    pv.add_argument("--related", action="append", default=[])

    pa = sub.add_parser("analysis", parents=[common, dated], help="市場分析(STEP 1~5)")
    pa.add_argument("--title", required=True); pa.add_argument("--horizon", default="1~3 個月")

    pr = sub.add_parser("report", parents=[common, dated], help="收盤報告")
    pr.add_argument("--title", default="", help="副題(選填);空則 檔名_收盤報告.md")
    pr.add_argument("--tracks", action="append", default=[])
    pr.add_argument("--main-analysis", dest="main_analysis", default="")

    pd = sub.add_parser("decision", parents=[common, dated], help="決策日誌")
    pd.add_argument("--ticker", required=True); pd.add_argument("--name", default="")
    pd.add_argument("--action", default="觀望", help="買進/加碼/減碼/賣出/觀望")
    pd.add_argument("--stock-link", dest="stock_link", default="")

    pn = sub.add_parser("news", parents=[common, dated], help="新聞彙整/券商評等")
    pn.add_argument("--title", required=True, help="主題(檔名+H1)")
    pn.add_argument("--tracks", action="append", default=[], help="追蹤個股連結,可重複")

    a = p.parse_args()
    relpath, content = BUILDERS[a.type](a)
    write_note(resolve_out(relpath, a.out), content, a.force)


if __name__ == "__main__":
    main()
