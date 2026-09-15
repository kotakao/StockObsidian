---
name: taiwanstock-closing-report
description: 產生當日台股收盤報告(精簡版):新聞掃描+大盤+持股/Top5 價量與三大法人+否證檢核+明日觀察,填入模板 F、寫成 Obsidian 筆記、更新 Portfolio/索引後 commit。當使用者輸入 /taiwanstock-closing-report、/收盤報告,或說「寫收盤報告、今天收盤、收盤簡報」時使用。
---

# 收盤報告(/收盤報告)— 每日精簡版

> 遵循 [`CLAUDE.md`](CLAUDE.md) 資料誠實原則與 Obsidian 全域規則。模板見 分析師角色Prompt.md 模板 **F**。

## 步驟
1. **資料健檢(先做,不過就別往下)**〔源A;7 檢查濃縮=完整/陳舊/量級/時序/重複/彙總/對帳〕:
   - **完整+陳舊**:`list_available_dates` 確認目標交易日的 daily_quotes/institutional/market_daily **皆已同步**;缺 → `refetch_date <日>` 補,補不齊標「待同步/需即時確認」,**不用舊日數據冒充當日**。報告寫「該收盤日」(非今天日曆日);使用者未指定用最新交易日。
   - **量級+重複**:`refetch_date` 回傳的 `sanity`(當日列數 vs 前一交易日)passed=false 或列數暴減=資料不全,勿出;確認無隔日錯位/重複列。
   - **彙總+對帳**:三大法人 股÷1000=張;持股現價資料日 = 目標收盤日;`data_date` 誠實=實際資料日,不為對齊檔名竄改。
2. **新聞掃描(必做)**〔源C〕:`WebSearch` 查 ①國際大廠/AI 半導體 ②當日展會/財報 ③台股市況。標來源+日期+可靠度。
3. **大盤**〔源A〕:`get_market_history`(days=3~6)——加權/漲跌%/成交/漲跌家數/三大法人(股÷1000=張)/融資。
4. **持股 + Top5 追蹤**〔源A〕:對每檔(見 `我的持股_Portfolio` 與 `族群輪動索引_AI供應鏈` §五 Top5)呼叫 `get_stock_history`(days=2)+ `get_institutional_history`(days=2)。ETF 只取價。
5. **填模板 F** → 五段:①新聞 ②大盤 ③持股/Top5(價量+三大法人,逐檔解讀)④否證條件檢核(對照主分析 5C / 索引 §六)⑤明日觀察。
6. **產骨架再填**(勿手打路徑/frontmatter):`python scripts/new_note.py report --date <收盤日> --tracks '[[個股_代碼_名]]' … [--title 主題] [--main-analysis '[[主分析]]']` → 自動建於 `分析報告/YYYY/MM/第N週/`、命名/frontmatter/麵包屑就緒;再把五段數據填入骨架。**確認 tags 含「分析報告」**(不含就 `--tag 分析報告` 或事後補)。
7. **更新**:`我的持股_Portfolio` 現價→該收盤日、重算損益;`族群輪動索引_AI供應鏈` 加一行收盤麵包屑。
8. **commit**:訊息 `add: YYYY-MM-DD 收盤報告 + Portfolio 更新`;**push 需先問使用者**。
9. `SendUserFile` 交付報告檔。

## 鐵則
- 數據全走 MCP〔源A〕、標日期;判斷標【事實/推測】+信心;查不到寫「待撈/需即時確認」,禁虛構價位。
- 若使用者買賣有異動,先更新 `我的持股_Portfolio` 股數/均價 + `交易紀錄_TradeLog`,再算損益。
- **不做**:不給買賣/個人化投資建議(非持牌投顧)、不預測漲跌%、不虛構點位。
