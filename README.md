# 逆向分析 Skill（Reverse Engineering Analysis，REA）使用說明書

讓 AI Agent 透過 **computer use 實際操作**一套網頁或桌面軟體，邊操作邊留下證據，最後產出三份文件：

- **SDD 規格書**：這套軟體做什麼
- **TDD 實作計畫**：先寫測試、再寫程式的開發順序
- **DESIGN.md 設計系統**：色彩、字型、間距、元件樣式

另一個 Agent 只要讀這些文件，就能從零做出功能相同的應用程式，完全不需要看到原系統。支援 **Claude Code** 與 **Codex**。

---

## 目錄
1. 適合用在哪裡
2. 安裝
3. 快速開始
4. 三種來源模式
5. 分析流程
6. 產出檔案說明
7. 交給建置 Agent
8. 常見問題
9. 進階：工具與指令參考
10. 授權與使用規範

---

## 一、適合用在哪裡

| 情境 | 範例 |
|---|---|
| 舊系統重寫 | 自家舊網站要用新技術重做，但沒有完整規格文件 |
| 競品功能研究 | 了解某平台有哪些功能與流程（只分析行為，不抄程式碼和品牌） |
| 補齊規格 | 系統上線了，卻沒有人寫過需求與測試 |
| 復刻介面風格 | 把自家系統的設計風格整理成 DESIGN.md，讓新專案沿用 |

**不適合：** 破解授權、繞過付費、反編譯商業軟體、複製別人的品牌外觀。這個 Skill 的規則會主動擋下這些做法。

---

## 二、安裝

### 1. 下載
```bash
git clone https://github.com/FW1201/reverse-engineering-analysis-skill.git
```
```bash
cd reverse-engineering-analysis-skill
```

### 2. 先檢查環境（不會改動任何東西）
```bash
bash install.sh --check
```

安裝程式會逐項檢查，缺什麼就告訴你怎麼補：

| 檢查項目 | 等級 | 缺少時 |
|---|---|---|
| Python 3.9 以上 | 必要 | 提示安裝指令（macOS：`brew install python`） |
| Claude Code 或 Codex（至少一個） | 必要 | 提示安裝連結 |
| Node.js 20.19 以上、Google Chrome | 分析網頁時需要 | 提示安裝指令 |
| chrome-devtools MCP（每個 Agent 各自設定） | 分析網頁時需要 | 顯示設定指令，可選擇讓它直接幫你執行 |
| Claude 桌面版／Codex Computer Use | 分析桌面軟體時需要 | 說明如何啟用（macOS 限定） |
| Skill 腳本自我測試 | 必要 | 停止安裝 |

### 3. 正式安裝
```bash
bash install.sh
```

所有必要項目都通過才會安裝。裝完請**重新啟動** Claude Code／Codex。

| 選項 | 用途 |
|---|---|
| `--check` | 只檢查，不安裝 |
| `--mode copy` | 複製一份進 skills 資料夾（預設是連結到這個 clone，`git pull` 就能更新） |
| `--yes` | 全部使用預設值，不逐項詢問 |
| `--uninstall` | 移除已安裝的 Skill |

安裝位置會自動判斷：有 `~/.agents/skills` 就裝在那裡，否則裝在 `~/.codex/skills` 或 `~/.claude/skills`；其他 Agent 只建 symlink，不會重複安裝。

---

## 三、快速開始

在 Claude Code 或 Codex 裡直接說：

> 用 reverse-engineering-analysis 分析 https://example.com ，產出 SDD／TDD 計畫和 DESIGN.md。

如果是自己的系統，而且有原始碼，請一併說明：

> 這是我自己的系統，原始碼在 ~/dev/my-app，可以讀。請用 REA 分析並產出計畫。

Agent 開始前會先一次問清楚這幾件事：

1. 要分析哪個目標
2. **來源模式**：能不能讀原始碼（見第四節）
3. 有沒有測試帳號或隔離環境
4. 重建的 App 要放在專案資料夾的哪裡
5. 能不能下載系統匯出的檔案

---

## 四、三種來源模式（先決定這個）

| 模式 | 適用 | Agent 可以做的事 | DESIGN.md |
|---|---|---|---|
| `ui-only`（預設） | 第三方、商業軟體，或不確定有沒有權限 | 只透過介面操作；可看網路請求、瀏覽器儲存、主控台訊息。**不讀原始碼、不反編譯** | **中性版**：保留間距、字級、版面結構，品牌色、字型、logo 換成原創 |
| `authorized-source` | 自家系統，或你有權限讀程式碼 | UI 分析完後，再讀原始碼找隱藏規則 | **精確版**：數值原樣記錄 |
| `open-source` | 有授權條款的開源專案 | 同上，但要記錄授權，且不搬程式碼 | 精確版 |

### 雙軌：UI 主軌、程式碼輔軌

- **UI 軌**決定規格：每一條需求都要有實際操作的觀察紀錄。
- **程式碼軌**只提出「假設」：例如讀到「標題上限 40 字」，Agent 必須回到介面輸入 41 個字確認，才算成立。
- UI 測不到的（音效、計時器、檔案格式）會標成 `[CODE-ONLY]`。
- 程式碼與實際行為衝突時，以 UI 為準。

這樣能拿到程式碼「找得快、找得全」的好處，規格又不會變成抄寫原始碼。

---

## 五、分析流程（Agent 會做什麼）

1. **界定範圍**：填寫 `00-scope.md`，包含來源模式、隔離環境與動作規則。
2. **建立工作區**：所有產出都放在 `docs/reverse-engineering/<名稱>/`。
3. **探索介面**：先走遍所有畫面，再深入每個流程，包括空白、錯誤、邊界值、正常輸入、取消、重新整理後的狀態。
4. **逐筆記錄**：每個動作都記一筆觀察（OBS-001、OBS-002…）並截圖。
5. **程式碼軌**（僅限可讀碼模式）：讀碼找線索，再回 UI 驗證。
6. **設計系統**：量測色彩、字型、間距與元件狀態（hover／focus／disabled），整理成 DESIGN.md。
7. **撰寫文件**：盤點清單 → 規格 → 架構 → TDD 計畫 → 交接說明。
8. **品質閘門**：驗證腳本必須顯示 `READY FOR HANDOFF` 才算完成。

### 安全規則（Agent 一定遵守）

| 動作類型 | 規則 |
|---|---|
| 瀏覽、搜尋、開關對話框 | 可以直接做 |
| 在測試資料上新增、編輯、切換設定 | 可以做，盡量還原 |
| 刪除真實資料、全部重設、寄信、發布、付款、改帳號 | **一定先問你**；沒同意就標成 `[UNKNOWN]` |
| 輸入密碼 | 不代填，由你自己登入 |

發現的 bug（例如 XSS、資料遺失）會寫進「已觀察缺陷」，**規格裡寫的是修正後的正確行為**，不會照抄 bug。

---

## 六、產出檔案說明

位置：`docs/reverse-engineering/<名稱>/`

| 檔案 | 內容 | 誰會看 |
|---|---|---|
| `00-scope.md` | 目標、來源模式、隔離環境、動作規則 | 你 |
| `observations.jsonl` + `evidence/` | 每個動作的紀錄，加上截圖、網路資料、設計量測 | 需要查證時 |
| `01-inventory.md` | 畫面 SCR、元件 CMP、流程 FLW、資料 ENT、介面 API、規則 RUL | 你／建置 Agent |
| `02-spec.md` | **SDD 規格**：需求 FR + Given/When/Then 驗收條件、已觀察缺陷、未決問題 | 建置 Agent（主要依據） |
| `mechanism-notes.md` | 程式碼軌的發現與驗證結果（僅可讀碼模式） | 建置 Agent |
| `DESIGN.md` | **設計系統**（Google design.md 格式）：色彩、字型、圓角、間距、元件與狀態 | 建置 Agent |
| `03-design.md` | 重建版的技術架構 | 建置 Agent |
| `04-tdd-plan.md` | **TDD 計畫**：每個任務都是 RED（先寫會失敗的測試）→ GREEN（最少程式碼）→ REFACTOR | 建置 Agent |
| `05-traceability.md` | 追溯表：需求 → 證據 → 測試任務（自動產生） | 你（驗收用） |
| `AGENT-HANDOFF.md` | 給建置 Agent 的入口說明 | 建置 Agent |

### 需求標記

| 標記 | 意思 |
|---|---|
| （引用 OBS 編號） | 實際觀察到 |
| `[INFERRED]` | 推論得出，未直接看到 |
| `[UNKNOWN]` | 無法測試（例如沒被允許的危險動作） |
| `[CODE-ONLY]` | 只能從程式碼得知，UI 看不到 |
| `[DEFECT-FIX]` | 為修正原系統缺陷而新增的行為 |

---

## 七、交給建置 Agent 開始做 App

確認驗證通過後，開一個新的 Agent 對話，貼上：

```text
Read docs/reverse-engineering/<名稱>/AGENT-HANDOFF.md and implement the app task by task.
```

建置 Agent 會依照 TDD 計畫逐項開發，每個任務都要先看到測試失敗、再讓它通過。完成後會依需求編號回報測試結果。

---

## 八、常見問題

**Q：一定要有原始碼嗎？**
不用。預設的 `ui-only` 模式只靠介面操作，就能產出完整計畫。

**Q：分析第三方網站會不會有法律問題？**
`ui-only` 模式只做一般使用者看得到的行為分析，不讀程式碼、不複製品牌外觀（DESIGN.md 會自動中性化）。但請你自行確認目標網站的服務條款允許這類測試，並且使用測試帳號。

**Q：驗證一直顯示 `NOT READY`？**
照它列出的 ERROR 逐項修正。常見原因：需求沒有引用證據、TDD 任務沒寫 RED 測試、DESIGN.md 缺必要欄位、規格裡出現程式碼。

**Q：要登入的系統怎麼辦？**
Agent 不會代填密碼。請你在它開的瀏覽器裡自己登入，或提供專用的測試帳號環境。

**Q：分析資料會不會被推上 GitHub？**
本 repo 的 `.gitignore` 預設排除 `docs/reverse-engineering/` 下的實際分析結果，只保留示範範例 `demo-target-dual`。

**Q：怎麼更新 Skill？**
連結模式安裝的話，`git pull` 就好；複製模式要重新執行 `bash install.sh --mode copy`。

---

## 九、進階：工具與指令參考

### 腳本（在 Skill 資料夾內執行）

| 指令 | 用途 |
|---|---|
| `python3 scripts/init_workspace.py <專案> <名稱> --target <網址> --source-mode ui-only` | 建立工作區 |
| `python3 scripts/log_observation.py <工作區> --shot --screen SCR-01 --action click --target "儲存" --result "…"` | 記錄一筆觀察，並指定截圖存放路徑 |
| `python3 scripts/sample_colors.py <截圖.png> --top 12` | 取得截圖主要色彩 |
| `python3 scripts/sample_colors.py --contrast "#111111" "#FFFFFF"` | 計算 WCAG 對比度 |
| `python3 scripts/validate_artifacts.py <工作區> --write-matrix` | 品質閘門，並產生追溯表 |
| `scripts/design_tally.js` | 貼到瀏覽器工具執行，唯讀量測頁面樣式數值 |

### 各 Agent 使用的操作工具

| 目標 | Claude Code | Codex |
|---|---|---|
| 網頁（建議） | chrome-devtools MCP | chrome-devtools MCP |
| 網頁（替代） | 內建瀏覽器、Claude in Chrome | `cua_repl` 內建瀏覽器 |
| 桌面軟體 | `mcp__computer-use__*` | `cua_repl` Computer Use |

詳細對照請見 `reverse-engineering-analysis/references/tool-adapters.md`。

### 專案結構

```text
reverse-engineering-analysis/   Skill 本體（SKILL.md、scripts、templates、references）
install.sh                      環境檢查 + 引導設定 + 安裝
docs/reverse-engineering/       分析產出（示範：demo-target-dual）
fixtures/demo-target/           本地示範 App
tests/                          示範 App 的標準答案（回歸測試用）
```

### 回歸測試

先啟動示範 App：

```bash
cd fixtures/demo-target && python3 -m http.server 8765 --bind 127.0.0.1
```

再對 `http://127.0.0.1:8765/` 執行 Skill，把結果和 `tests/demo-target-ground-truth.md` 比對。

### 測試紀錄（2026-11-27）

| 測試 | 結果 |
|---|---|
| 無 Skill 的對照組 | 直接抓原始碼、規格抄 DOM id 與 CSS、用 JS 模擬點擊、打算照抄 XSS、跳過新增／編輯、只有一份大文件 |
| UI-only（第三方網頁） | 全程真實操作；43 筆觀察／26 條需求／19 個任務；11 個缺陷轉為修正後的需求 |
| 雙軌（示範 App，授權讀碼） | 答案卷 9 項行為全部找到；程式碼軌另外抓到重複標題、標籤上限、全形逗號、時間排序 bug |
| DESIGN.md（中性＋精確） | 中性版保留結構、換掉品牌配色並修正 2 處對比不足；精確版原值記錄；共找到 5 個視覺缺陷 |

---

## 十、授權與使用規範

本專案採用 **MIT 授權**，詳見 [LICENSE](LICENSE)。

請只對你有權分析的軟體使用本 Skill。它的設計是黑箱、clean-room 式的行為分析，不會複製原系統的程式碼或品牌。
