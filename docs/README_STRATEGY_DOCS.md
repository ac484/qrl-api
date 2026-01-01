# 策略設計文檔導航

> **Navigation Guide**: 如何使用策略設計文檔

## 📚 文檔概覽

本項目包含完整的策略設計文檔，涵蓋所有數學公式、計算步驟和實現細節。

### 文檔層次結構

```
策略文檔架構
├── README_STRATEGY_DOCS.md (本文件) - 導航指南
├── STRATEGY_QUICK_REFERENCE.md - 快速參考
├── STRATEGY_DESIGN_FORMULAS.md - 完整公式
└── STRATEGY_CALCULATION_EXAMPLES.md - 計算實例
```

---

## 🎯 使用指南

### 根據角色選擇閱讀順序

#### 開發者 (首次閱讀)
1. **STRATEGY_QUICK_REFERENCE.md** - 快速了解核心概念
2. **STRATEGY_DESIGN_FORMULAS.md** - 深入理解數學基礎
3. **STRATEGY_CALCULATION_EXAMPLES.md** - 通過實例學習
4. **代碼實現** - 查看 `src/app/domain/strategies/` 和 `src/app/domain/risk/`

#### 產品經理 / 策略分析師
1. **STRATEGY_QUICK_REFERENCE.md** - 了解策略邏輯
2. **STRATEGY_DESIGN_FORMULAS.md (第 3、4 節)** - 信號生成與倉位管理
3. **STRATEGY_CALCULATION_EXAMPLES.md (實例 4、5)** - 買賣流程

#### 測試工程師
1. **STRATEGY_CALCULATION_EXAMPLES.md** - 獲取測試用例
2. **STRATEGY_DESIGN_FORMULAS.md (第 8 節)** - 邊界條件
3. **STRATEGY_QUICK_REFERENCE.md** - 驗證計算

#### 技術支持 / 運維
1. **STRATEGY_QUICK_REFERENCE.md** - 快速排查問題
2. **STRATEGY_DESIGN_FORMULAS.md (第 6 節)** - 風險控制規則
3. **STRATEGY_CALCULATION_EXAMPLES.md (實例 7)** - 常見問題

---

## 📖 文檔詳細說明

### 1. STRATEGY_QUICK_REFERENCE.md
**適合**: 需要快速查找公式或流程的人

**內容**:
- 核心公式速查表
- 常用計算範例
- 決策流程圖
- 檢查清單
- 代碼使用示例

**何時使用**:
- ✅ 需要快速確認某個公式
- ✅ 忘記某個參數的預設值
- ✅ 需要快速判斷買賣信號
- ✅ 開發時需要代碼參考

**閱讀時間**: ~10 分鐘

---

### 2. STRATEGY_DESIGN_FORMULAS.md
**適合**: 需要深入理解策略設計的人

**內容** (10 個主要章節):
1. 核心策略公式
2. 移動平均線計算
3. 信號生成邏輯
4. 倉位管理公式
5. 成本計算公式
6. 風險控制公式
7. 完整計算範例
8. 公式速查表
9. 實現檢查清單
10. 參考資料

**重點章節**:
- **第 2 節**: MA 計算的完整推導
- **第 3 節**: BUY/SELL 信號的詳細條件
- **第 4 節**: 三層倉位架構設計
- **第 6 節**: 所有風險控制規則
- **第 7 節**: 完整的交易週期模擬

**何時使用**:
- ✅ 設計新策略或修改現有策略
- ✅ 需要理解策略的數學基礎
- ✅ 撰寫技術文檔或規格說明
- ✅ 進行策略回測或分析

**閱讀時間**: ~45-60 分鐘 (完整閱讀)

**快速查找**:
- 公式定義: 查看章節 1-6
- 實際應用: 查看章節 7
- 速查: 查看章節 8

---

### 3. STRATEGY_CALCULATION_EXAMPLES.md
**適合**: 通過實例學習的人

**內容** (9 個詳細實例):
1. 基礎計算 (MA、成本、倉位)
2. 完整買入流程
3. 完整賣出流程
4. 連續交易追蹤
5. 風險觸發處理
6. 數據異常處理
7. 性能優化示例

**實例特點**:
- 每個步驟都有詳細說明
- 使用真實的數字進行計算
- 包含中間結果驗證
- 展示完整的決策過程

**何時使用**:
- ✅ 想通過實例理解策略
- ✅ 需要驗證自己的計算
- ✅ 設計測試用例
- ✅ 排查計算錯誤

**閱讀時間**: ~40-50 分鐘 (完整閱讀)

**推薦學習路徑**:
1. 實例 1-3: 基礎計算 (15 分鐘)
2. 實例 4-5: 完整流程 (20 分鐘)
3. 實例 6-9: 高級場景 (15 分鐘)

---

## 🔍 快速查找指南

### 按主題查找

#### 移動平均線 (MA)
- **公式**: STRATEGY_DESIGN_FORMULAS.md - 第 2.1 節
- **計算步驟**: STRATEGY_DESIGN_FORMULAS.md - 第 2 節
- **實例**: STRATEGY_CALCULATION_EXAMPLES.md - 實例 1
- **代碼**: `trading_strategy.py::calculate_moving_average`

#### 買入信號
- **公式**: STRATEGY_DESIGN_FORMULAS.md - 第 3.1 節
- **完整流程**: STRATEGY_CALCULATION_EXAMPLES.md - 實例 4
- **快速參考**: STRATEGY_QUICK_REFERENCE.md - 買入條件
- **代碼**: `trading_strategy.py::generate_signal`

#### 賣出信號
- **公式**: STRATEGY_DESIGN_FORMULAS.md - 第 3.2 節
- **完整流程**: STRATEGY_CALCULATION_EXAMPLES.md - 實例 5
- **快速參考**: STRATEGY_QUICK_REFERENCE.md - 賣出條件
- **代碼**: `trading_strategy.py::generate_signal`

#### 平均成本
- **公式**: STRATEGY_DESIGN_FORMULAS.md - 第 5 節
- **計算範例**: STRATEGY_CALCULATION_EXAMPLES.md - 實例 2
- **快速參考**: STRATEGY_QUICK_REFERENCE.md - 平均成本
- **更新規則**: STRATEGY_DESIGN_FORMULAS.md - 第 5.2、5.3 節

#### 倉位管理
- **公式**: STRATEGY_DESIGN_FORMULAS.md - 第 4 節
- **計算範例**: STRATEGY_CALCULATION_EXAMPLES.md - 實例 3
- **快速參考**: STRATEGY_QUICK_REFERENCE.md - 倉位分層
- **動態調整**: STRATEGY_DESIGN_FORMULAS.md - 第 4.2 節

#### 風險控制
- **公式**: STRATEGY_DESIGN_FORMULAS.md - 第 6 節
- **觸發場景**: STRATEGY_CALCULATION_EXAMPLES.md - 實例 7
- **快速參考**: STRATEGY_QUICK_REFERENCE.md - 風險控制
- **代碼**: `risk/limits.py::RiskManager`

---

## 🛠️ 開發工作流程

### 實現新功能
1. 閱讀相關章節的公式定義
2. 查看計算實例了解具體步驟
3. 參考現有代碼實現
4. 根據實例設計測試用例
5. 實現並驗證功能

### 排查問題
1. 使用快速參考定位問題類型
2. 查看公式文檔了解預期行為
3. 參考計算實例驗證邏輯
4. 檢查代碼實現是否符合公式

### 修改策略
1. 理解當前策略的數學基礎
2. 識別需要修改的公式
3. 更新公式文檔
4. 更新計算實例
5. 修改代碼實現
6. 更新測試用例

---

## 📝 文檔維護

### 何時需要更新文檔

**必須更新**:
- ✅ 修改任何策略公式
- ✅ 調整風險控制參數
- ✅ 改變倉位分配邏輯
- ✅ 修改成本計算方式

**建議更新**:
- 📝 添加新的交易場景
- 📝 優化計算性能
- 📝 增加新的檢查項目

### 更新流程
1. 確定修改影響的文檔章節
2. 更新公式定義和說明
3. 添加或修改相關實例
4. 更新快速參考
5. 更新代碼文檔字符串

---

## 🎓 學習路徑推薦

### 初學者路徑 (4-5 小時)
1. **第 1 天** (2 小時):
   - 閱讀 STRATEGY_QUICK_REFERENCE.md
   - 理解核心概念和公式
   - 嘗試手動計算幾個範例

2. **第 2 天** (2-3 小時):
   - 閱讀 STRATEGY_DESIGN_FORMULAS.md (第 1-4 節)
   - 深入理解 MA 和信號生成
   - 學習倉位管理規則

3. **第 3 天** (1 小時):
   - 閱讀 STRATEGY_CALCULATION_EXAMPLES.md (實例 1-5)
   - 跟隨步驟驗證計算
   - 理解完整交易流程

### 進階路徑 (2-3 小時)
1. **深入公式** (1 小時):
   - STRATEGY_DESIGN_FORMULAS.md (第 5-6 節)
   - 成本計算和風險控制
   - 邊界條件和約束

2. **複雜場景** (1-2 小時):
   - STRATEGY_CALCULATION_EXAMPLES.md (實例 6-9)
   - 多交易場景
   - 錯誤處理和優化

### 開發者快速上手 (1 小時)
1. STRATEGY_QUICK_REFERENCE.md (15 分鐘)
2. 代碼實現和文檔字符串 (30 分鐘)
3. STRATEGY_CALCULATION_EXAMPLES.md - 選讀相關實例 (15 分鐘)

---

## 💡 最佳實踐

### 閱讀建議
1. **不要跳過基礎**: 即使你熟悉交易策略，也要閱讀 MA 計算部分
2. **動手計算**: 用計算器驗證文檔中的數字
3. **對照代碼**: 邊看文檔邊查看代碼實現
4. **做筆記**: 記錄重要公式和關鍵點

### 使用建議
1. **書簽常用章節**: 在瀏覽器中標記常用頁面
2. **打印快速參考**: 將 STRATEGY_QUICK_REFERENCE.md 打印出來
3. **定期復習**: 每月回顧一次核心公式
4. **分享知識**: 向團隊成員解釋公式以加深理解

---

## 🔗 相關資源

### 項目文檔
- [QRL 屯幣策略](./1-qrl-accumulation-strategy.md)
- [策略與數據源](./05-Strategies-and-Data.md)
- [架構設計](./ADR-001-Architecture-Diagrams.md)

### 代碼實現
- `src/app/domain/strategies/trading_strategy.py` - 策略實現
- `src/app/domain/risk/limits.py` - 風險管理
- `src/app/domain/position/calculator.py` - 倉位計算

### 外部參考
- 技術指標: 移動平均線理論
- 風險管理: 倉位管理最佳實踐
- 交易策略: 趨勢跟隨策略

---

## 📞 獲取幫助

### 常見問題
**Q: 我應該從哪個文檔開始?**
A: 如果是首次閱讀，從 STRATEGY_QUICK_REFERENCE.md 開始。

**Q: 公式看不懂怎麼辦?**
A: 先看 STRATEGY_CALCULATION_EXAMPLES.md 中的實例，然後再回到公式。

**Q: 如何驗證我的理解?**
A: 使用文檔中的範例數字，自己計算一遍並對比結果。

**Q: 文檔有錯誤怎麼辦?**
A: 提交 Issue 或直接在代碼中修正並更新文檔。

---

**版本**: 1.0.0  
**最後更新**: 2025-12-27  
**維護者**: QRL Trading Bot Development Team
