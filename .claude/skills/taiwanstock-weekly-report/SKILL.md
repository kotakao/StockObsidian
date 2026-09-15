---
name: taiwanstock-weekly-report
description: 產生完整 STEP 1~5 週報(AI 供應鏈資金輪動、功率元件之後的下一棒),整合本週新聞/大盤/族群漲幅/法人買賣超排行/月營收財報,填入模板 E、寫成筆記、更新索引後 commit。當使用者輸入 /taiwanstock-weekly-report、/週報,或說「寫週報、完整輪動分析、這週的輪動報告」時使用。
---

# 週報(/週報)— 完整 STEP 1~5

> 遵循 [`CLAUDE.md`](CLAUDE.md)。模板見 分析師角色Prompt.md 模板 **E**;篇幅權重 **STEP 2+3 合計 ≥50%**;STEP 1 嚴格壓縮(600 字內)。

## 步驟
0. **資料健檢(先做)**〔源A/B;7 檢查=完整/陳舊/量級/時序/重複/彙總/對帳〕:`list_available_dates` 確認本週交易日 daily_quotes/institutional/market_daily 已同步(缺 → `refetch_date` 補,補不齊標「待同步」);**月營收/財報先確認 `get_monthly_revenue` 目標月已同步**、未同步標「待同步」不對帳(見 memory `mcp-revenue-data-lag`);法人 股÷1000=張、`data_date` 誠實填。任一不過 → 先修或明標,不硬寫。
1. **新聞掃描(必做)**〔源C〕:`WebSearch` — 全球 AI 週期(NVIDIA/capex/HBM/CoWoS)、美股總經(SOX/Fed/利率/油價)、地緣、當週重大事件。標來源+日期+可靠度。
2. **本週資金流向**〔源A〕:
   - `get_market_history`(days=6)——一週指數/外資投信自營/量能軌跡。
   - `get_sector_performance`(days=5)——族群漲幅(誰領漲/資金去哪)。
   - `get_institutional_ranking`(days=5, buy & sell)——外資+投信買/賣超排行(資金明確方向)。
3. **候選族群基本面/籌碼**〔源A/B〕:對關鍵代表股 `get_monthly_revenue`、必要時 `get_quarterly_financials`、`get_institutional_history`(近 5~6 日)。⚠️ 月營收先確認 MCP 是否已同步目標月。
4. **填模板 E**:STEP 1(1A 週期定位/1B 美股總經,壓縮)→ STEP 2(2A 序列/2B 交棒邏輯/2C 規律 R1~R4)→ STEP 3(3A 主流位階/3B 候選四條件評估/3C 下一棒排序+觸發+信心)→ STEP 4(代表股 真受惠vs概念)→ STEP 5(5A Top3/5B 訊號式進場/5C 各族群否證/5D AI 反轉訊號)→ 一句話總結。
5. **與前次週報比對**:載入上一份 `..._市場分析_..._週報`,明寫「本週相對變化」(排序升降、新訊號)。
6. **產骨架再填**(勿手打):`python scripts/new_note.py analysis --title 功率元件之後的下一棒_週報 --date <日> --tag 市場分析 --tag 週報 --tag 族群輪動 --tag AI供應鏈 --tag 分析報告` → 自動建於週資料夾、STEP 1~5 骨架就緒(⚠️ analysis 傳 --tag 會覆蓋預設,故一次帶齊、務必含「分析報告」「週報」);再逐段填入。
7. **更新** `族群輪動索引_AI供應鏈`:下一棒排序 + Top5 + 週報麵包屑。
8. **commit**(`add: YYYY-MM-DD 週報`);push 需先問。`SendUserFile` 交付。

## 鐵則
- STEP 1 壓縮、STEP 2+3 為主體;每判斷附推論鏈 + 【事實/推測】+信心;數據標來源+日期。
- 排序變動必須有籌碼/營收/新聞依據,不憑感覺;不虛構漲幅/價位。
- 追蹤清單維持上限 5;要換檔先說明汰換邏輯。
- **不做**:不給買賣/個人化投資建議(非持牌投顧)、不預測點位/漲幅%、不憑感覺調排序。
