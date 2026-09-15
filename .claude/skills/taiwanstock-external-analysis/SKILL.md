---
name: taiwanstock-external-analysis
description: 驗證並統整使用者提供的外部網址或資訊(X 貼文、新聞、券商報告、外電),用內建瀏覽器/WebSearch 讀取原文,以 taiwan-stock MCP 官方數據對帳驗證屬實與否,分【事實/未證實/來源所述】後寫成事件筆記。當使用者輸入 /taiwanstock-external-analysis、/外部資訊分析,或貼上網址/內容要求「驗證、核實、分析、統整」時使用。
---

# 外部資訊分析(/外部資訊分析)— 讀取→驗證→統整

> 遵循 [`CLAUDE.md`](CLAUDE.md) 資料誠實原則。模板見 分析師角色Prompt.md 模板 **D**(事件筆記)。

## 步驟
1. **讀取原文**:
   - **X / Twitter**:用**內建瀏覽器** `navigate` 到該 status URL → `get_page_text`(未登入即可讀貼文本體)。⚠️ `WebFetch` 對 x.com 會回 **402**,勿用;不登入、不過驗證。
   - 一般新聞/網頁:`WebFetch` 或瀏覽器皆可。
   - 多則可用 `browser_batch`(navigate+get_page_text 串接)一次讀。
2. **判斷類型**:①個股財務(可對帳)②產業事實/市占③總經/監管④forward 預估/評等。
3. **對帳驗證**:
   - **個股財務**〔源B〕:`get_quarterly_financials`、`get_monthly_revenue`、`get_company_profile` 逐項比對(季損益回傳為**累計**,單季=本期累計−前期)。標【事實·吻合/不符】。
   - **產業事實/市占/國外公司**〔源C〕:`WebSearch` 獨立佐證(多家)。國外股(日韓美)**不在 MCP**,財務標「來源所述、未經 MCP」。
   - **forward 預估/目標價/評等**:一律標 **【未證實·觀點】**,不背書。
4. **來源品質分層**(重要):轉述「**已公布事實/過去財報**」→ 對帳後可信;轉述「**forward 估值**」→ 未證實。同一帳號兩者要分開評。
5. **產骨架再填**(勿手打):外電/券商彙整用 `python scripts/new_note.py news --title 主題 --date <日> --tracks '[[個股_代碼_名]]'`;單一事件用 `python scripts/new_note.py event --title 主題 --date <日> --related '[[..]]'` → 自動建於週資料夾;再填。**確認 tags 含「分析報告」**(必要時 `--tag 分析報告 --tag 外電驗證`)。related/tracks 僅連**已存在**的完整檔名。
6. 若驗證出**新標的**且值得追蹤 → 主動詢問是否補建個股筆記(依模板 A)。commit/push 依使用者指示。

## 鐵則
- **先有原文再驗證**;讀不到就明說(如登入牆),請使用者貼原文,不臆測內容。
- 明確區分 **【事實】/【未證實】/【來源所述】** + 信心度;查不到寫待撈,禁虛構。
- **不做**:不給個人化投資建議(非持牌投顧);forward 預估/目標價/評等只標未證實、不背書、不臆測讀不到的內容。
