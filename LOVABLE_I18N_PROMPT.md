# LiveaLittle DeFi - 多語言支持 Lovable 提示詞

## 🌍 Lovable 提示詞

```
為 LiveaLittle DeFi 添加多語言國際化（i18n）支持。

## 技術要求

### 安裝依賴
- react-i18next
- i18next
- i18next-browser-languagedetector

### 支持的語言
1. 英文（English）- en（默認）
2. 繁體中文（Traditional Chinese）- zh-TW
3. 簡體中文（Simplified Chinese）- zh-CN
4. 日文（Japanese）- ja
5. 韓文（Korean）- ko
6. 西班牙文（Spanish）- es
7. 法文（French）- fr
8. 德文（German）- de

## 實現步驟

### 1. 創建 i18n 配置文件

在 `src/i18n/config.ts` 創建配置：

```typescript
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// 導入翻譯文件
import enTranslations from './locales/en.json';
import zhTWTranslations from './locales/zh-TW.json';
import zhCNTranslations from './locales/zh-CN.json';
import jaTranslations from './locales/ja.json';
import koTranslations from './locales/ko.json';
import esTranslations from './locales/es.json';
import frTranslations from './locales/fr.json';
import deTranslations from './locales/de.json';

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: enTranslations },
      'zh-TW': { translation: zhTWTranslations },
      'zh-CN': { translation: zhCNTranslations },
      ja: { translation: jaTranslations },
      ko: { translation: koTranslations },
      es: { translation: esTranslations },
      fr: { translation: frTranslations },
      de: { translation: deTranslations },
    },
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false,
    },
  });

export default i18n;
```

### 2. 語言切換器組件

在導航欄添加語言切換器，位於 "Connect Wallet" 按鈕左側：

**設計要求**：
- 使用下拉菜單
- 顯示當前語言的國旗圖標 + 語言名稱
- 點擊展開顯示所有語言選項
- 每個選項顯示國旗 + 語言名稱（本地化）

**示例**：
```
當前: 🇺🇸 English ▼

下拉菜單:
🇺🇸 English
🇹🇼 繁體中文
🇨🇳 简体中文
🇯🇵 日本語
🇰🇷 한국어
🇪🇸 Español
🇫🇷 Français
🇩🇪 Deutsch
```

**組件代碼結構**：
```typescript
import { useTranslation } from 'react-i18next';

const LanguageSwitcher = () => {
  const { i18n } = useTranslation();
  
  const languages = [
    { code: 'en', name: 'English', flag: '🇺🇸' },
    { code: 'zh-TW', name: '繁體中文', flag: '🇹🇼' },
    { code: 'zh-CN', name: '简体中文', flag: '🇨🇳' },
    { code: 'ja', name: '日本語', flag: '🇯🇵' },
    { code: 'ko', name: '한국어', flag: '🇰🇷' },
    { code: 'es', name: 'Español', flag: '🇪🇸' },
    { code: 'fr', name: 'Français', flag: '🇫🇷' },
    { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
  ];

  return (
    // 實現下拉菜單
  );
};
```

### 3. 使用翻譯

在所有組件中使用 `useTranslation` hook：

**示例**：
```typescript
import { useTranslation } from 'react-i18next';

const Dashboard = () => {
  const { t } = useTranslation();

  return (
    <div>
      <h1>{t('dashboard.title')}</h1>
      <p>{t('dashboard.totalAssets')}: ${totalAssets}</p>
    </div>
  );
};
```

### 4. 數字和貨幣格式化

使用 `Intl` API 進行本地化格式化：

```typescript
// 貨幣格式化
const formatCurrency = (amount: number, locale: string) => {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
};

// 百分比格式化
const formatPercent = (value: number, locale: string) => {
  return new Intl.NumberFormat(locale, {
    style: 'percent',
    minimumFractionDigits: 2,
  }).format(value / 100);
};

// 日期格式化
const formatDate = (date: Date, locale: string) => {
  return new Intl.DateTimeFormat(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(date);
};
```

### 5. RTL 支持（可選）

為阿拉伯語等 RTL 語言添加支持：

```typescript
useEffect(() => {
  document.dir = i18n.dir();
}, [i18n.language]);
```

## 翻譯文件結構

創建 `src/i18n/locales/en.json` 作為基礎翻譯文件，包含以下結構：

```json
{
  "common": {
    "loading": "Loading...",
    "error": "Error",
    "success": "Success",
    "confirm": "Confirm",
    "cancel": "Cancel",
    "save": "Save",
    "delete": "Delete",
    "edit": "Edit",
    "close": "Close",
    "next": "Next",
    "previous": "Previous",
    "submit": "Submit"
  },
  "nav": {
    "dashboard": "Dashboard",
    "strategy": "Strategy",
    "backtest": "Backtest",
    "subscription": "Subscription",
    "rebalance": "Rebalance",
    "connectWallet": "Connect Wallet",
    "disconnect": "Disconnect"
  },
  "landing": {
    "hero": {
      "title": "Intelligent DeFi Yield Strategy",
      "subtitle": "173.6% Annual Return, Zero Drawdown",
      "cta": "Get Started"
    },
    "features": {
      "highYield": {
        "title": "High Yield",
        "description": "Annual returns over 150%"
      },
      "zeroRisk": {
        "title": "Zero Risk",
        "description": "Delta Neutral strategy protects your capital"
      },
      "automated": {
        "title": "Fully Automated",
        "description": "Smart rebalancing and risk management"
      }
    }
  },
  "dashboard": {
    "title": "Dashboard",
    "totalAssets": "Total Assets",
    "totalProfit": "Total Profit",
    "annualAPY": "Annual APY",
    "currentDelta": "Current Delta",
    "maxDrawdown": "Max Drawdown",
    "sharpeRatio": "Sharpe Ratio",
    "marketRegime": "Market Regime",
    "positions": "Current Positions",
    "type": "Type",
    "protocol": "Protocol",
    "chain": "Chain",
    "pair": "Pair",
    "amount": "Amount",
    "apy": "APY",
    "status": "Status"
  },
  "strategy": {
    "title": "Configure Your Strategy",
    "selectPools": "Select LP Pools",
    "filters": "Filters",
    "minTVL": "Min TVL",
    "minAPY": "Min APY",
    "chains": "Chains",
    "protocols": "Protocols",
    "applyFilters": "Apply Filters",
    "davisScore": "Davis Score",
    "addToStrategy": "Add to Strategy",
    "riskSettings": "Risk Settings",
    "investmentAmount": "Investment Amount",
    "hedgeRatio": "Hedge Ratio",
    "maxDrawdown": "Max Drawdown Tolerance",
    "autoRebalance": "Enable Auto Rebalance",
    "createStrategy": "Create Strategy"
  },
  "rebalance": {
    "title": "Rebalance Opportunities",
    "priority": {
      "high": "HIGH",
      "medium": "MEDIUM",
      "low": "LOW"
    },
    "from": "From",
    "to": "To",
    "apyIncrease": "APY Increase",
    "totalCost": "Total Cost",
    "netProfit": "Net Profit",
    "paybackDays": "Payback Days",
    "executionPlan": "Execution Plan",
    "confirm": "Confirm Execution",
    "reject": "Reject",
    "decideLater": "Decide Later"
  },
  "backtest": {
    "title": "Strategy Backtest Verification",
    "period": "Backtest Period",
    "initialCapital": "Initial Capital",
    "marketCondition": "Market Condition",
    "deltaNeutral": "Delta Neutral Strategy",
    "pureLp": "Pure LP Strategy",
    "finalValue": "Final Value",
    "totalReturn": "Total Return",
    "annualReturn": "Annual Return",
    "maxDrawdown": "Max Drawdown",
    "sharpeRatio": "Sharpe Ratio",
    "advantage": "Advantage"
  },
  "subscription": {
    "title": "Choose Your Plan",
    "basic": {
      "name": "Basic",
      "price": "$29/month",
      "subtitle": "For individual investors",
      "features": [
        "3 strategy pools monitoring",
        "Daily auto rebalancing",
        "Basic risk protection",
        "Community support"
      ]
    },
    "pro": {
      "name": "Professional",
      "price": "$99/month",
      "subtitle": "For professional traders",
      "badge": "Most Popular",
      "features": [
        "Unlimited strategy pools",
        "Real-time auto optimization",
        "Advanced risk management",
        "Priority support",
        "Full backtest reports",
        "Basic API access",
        "Custom alerts"
      ]
    },
    "enterprise": {
      "name": "Enterprise",
      "price": "$499/month",
      "subtitle": "For institutions and teams",
      "features": [
        "All Pro features",
        "Custom strategy development",
        "Full API access",
        "Dedicated account manager",
        "SLA guarantee",
        "White-label solution",
        "Team collaboration"
      ]
    },
    "selectPlan": "Select Plan",
    "contactUs": "Contact Us"
  }
}
```

## 設計要求

1. **語言切換器樣式**：
   - 使用深色背景（#1a1f3a）
   - 青色邊框（#00D9FF）
   - 懸停時高亮
   - 圓角 8px
   - 下拉菜單使用陰影效果

2. **響應式**：
   - 移動端語言切換器顯示為圖標按鈕
   - 點擊展開全屏菜單

3. **動畫**：
   - 語言切換時添加淡入淡出效果
   - 下拉菜單展開/收起動畫

4. **持久化**：
   - 使用 localStorage 保存用戶語言偏好
   - 下次訪問時自動使用上次選擇的語言

5. **SEO 優化**：
   - 添加 `<html lang="xx">` 屬性
   - 為每種語言創建獨立的 meta 標籤

## 測試要求

1. 切換語言後，所有文本應立即更新
2. 數字和日期格式應符合當地習慣
3. 確保所有翻譯文件完整，無遺漏
4. 測試長文本的顯示效果（如德文）
5. 測試移動端的語言切換體驗

請實現完整的多語言支持功能。
```

---

## 📋 完整翻譯文件

### 英文（en.json）- 已在上面提供

### 繁體中文（zh-TW.json）

```json
{
  "common": {
    "loading": "載入中...",
    "error": "錯誤",
    "success": "成功",
    "confirm": "確認",
    "cancel": "取消",
    "save": "儲存",
    "delete": "刪除",
    "edit": "編輯",
    "close": "關閉",
    "next": "下一步",
    "previous": "上一步",
    "submit": "提交"
  },
  "nav": {
    "dashboard": "儀表板",
    "strategy": "策略配置",
    "backtest": "回測驗證",
    "subscription": "訂閱管理",
    "rebalance": "轉倉確認",
    "connectWallet": "連接錢包",
    "disconnect": "斷開連接"
  },
  "landing": {
    "hero": {
      "title": "智能化 DeFi 收益策略",
      "subtitle": "年化收益 173.6%，零回撤",
      "cta": "開始使用"
    },
    "features": {
      "highYield": {
        "title": "高收益",
        "description": "年化收益超過 150%"
      },
      "zeroRisk": {
        "title": "零風險",
        "description": "Delta Neutral 策略保護本金"
      },
      "automated": {
        "title": "全自動",
        "description": "智能轉倉和風險管理"
      }
    }
  },
  "dashboard": {
    "title": "儀表板",
    "totalAssets": "總資產",
    "totalProfit": "總收益",
    "annualAPY": "年化收益率",
    "currentDelta": "當前 Delta",
    "maxDrawdown": "最大回撤",
    "sharpeRatio": "夏普比率",
    "marketRegime": "市場狀態",
    "positions": "當前倉位",
    "type": "類型",
    "protocol": "協議",
    "chain": "鏈",
    "pair": "代幣對",
    "amount": "金額",
    "apy": "年化收益率",
    "status": "狀態"
  },
  "strategy": {
    "title": "配置您的策略",
    "selectPools": "選擇 LP 池",
    "filters": "篩選器",
    "minTVL": "最小 TVL",
    "minAPY": "最小 APY",
    "chains": "區塊鏈",
    "protocols": "協議",
    "applyFilters": "應用篩選",
    "davisScore": "戴維斯評分",
    "addToStrategy": "添加到策略",
    "riskSettings": "風險設置",
    "investmentAmount": "投入金額",
    "hedgeRatio": "對沖比例",
    "maxDrawdown": "最大回撤容忍度",
    "autoRebalance": "啟用自動轉倉",
    "createStrategy": "創建策略"
  },
  "rebalance": {
    "title": "轉倉機會",
    "priority": {
      "high": "高",
      "medium": "中",
      "low": "低"
    },
    "from": "從",
    "to": "到",
    "apyIncrease": "APY 提升",
    "totalCost": "總成本",
    "netProfit": "淨收益",
    "paybackDays": "回本天數",
    "executionPlan": "執行計劃",
    "confirm": "確認執行",
    "reject": "拒絕",
    "decideLater": "稍後決定"
  },
  "backtest": {
    "title": "策略回測驗證",
    "period": "回測期間",
    "initialCapital": "初始資金",
    "marketCondition": "市場環境",
    "deltaNeutral": "Delta Neutral 策略",
    "pureLp": "純 LP 策略",
    "finalValue": "最終價值",
    "totalReturn": "總收益",
    "annualReturn": "年化收益",
    "maxDrawdown": "最大回撤",
    "sharpeRatio": "夏普比率",
    "advantage": "優勢"
  },
  "subscription": {
    "title": "選擇適合您的計劃",
    "basic": {
      "name": "基礎版",
      "price": "$29/月",
      "subtitle": "適合個人投資者",
      "features": [
        "3個策略池監控",
        "每日自動再平衡",
        "基礎風險保護",
        "社區支持"
      ]
    },
    "pro": {
      "name": "專業版",
      "price": "$99/月",
      "subtitle": "適合專業交易者",
      "badge": "最受歡迎",
      "features": [
        "無限策略池",
        "實時自動優化",
        "高級風險管理",
        "優先支持",
        "完整回測報告",
        "基礎 API 訪問",
        "自定義警報"
      ]
    },
    "enterprise": {
      "name": "機構版",
      "price": "$499/月",
      "subtitle": "適合機構和團隊",
      "features": [
        "專業版所有功能",
        "定制策略開發",
        "完整 API 訪問",
        "專屬客戶經理",
        "SLA 服務保障",
        "白標解決方案",
        "團隊協作功能"
      ]
    },
    "selectPlan": "選擇計劃",
    "contactUs": "聯繫我們"
  }
}
```

### 簡體中文（zh-CN.json）

```json
{
  "common": {
    "loading": "加载中...",
    "error": "错误",
    "success": "成功",
    "confirm": "确认",
    "cancel": "取消",
    "save": "保存",
    "delete": "删除",
    "edit": "编辑",
    "close": "关闭",
    "next": "下一步",
    "previous": "上一步",
    "submit": "提交"
  },
  "nav": {
    "dashboard": "仪表板",
    "strategy": "策略配置",
    "backtest": "回测验证",
    "subscription": "订阅管理",
    "rebalance": "转仓确认",
    "connectWallet": "连接钱包",
    "disconnect": "断开连接"
  },
  "landing": {
    "hero": {
      "title": "智能化 DeFi 收益策略",
      "subtitle": "年化收益 173.6%，零回撤",
      "cta": "开始使用"
    },
    "features": {
      "highYield": {
        "title": "高收益",
        "description": "年化收益超过 150%"
      },
      "zeroRisk": {
        "title": "零风险",
        "description": "Delta Neutral 策略保护本金"
      },
      "automated": {
        "title": "全自动",
        "description": "智能转仓和风险管理"
      }
    }
  },
  "dashboard": {
    "title": "仪表板",
    "totalAssets": "总资产",
    "totalProfit": "总收益",
    "annualAPY": "年化收益率",
    "currentDelta": "当前 Delta",
    "maxDrawdown": "最大回撤",
    "sharpeRatio": "夏普比率",
    "marketRegime": "市场状态",
    "positions": "当前仓位",
    "type": "类型",
    "protocol": "协议",
    "chain": "链",
    "pair": "代币对",
    "amount": "金额",
    "apy": "年化收益率",
    "status": "状态"
  },
  "strategy": {
    "title": "配置您的策略",
    "selectPools": "选择 LP 池",
    "filters": "筛选器",
    "minTVL": "最小 TVL",
    "minAPY": "最小 APY",
    "chains": "区块链",
    "protocols": "协议",
    "applyFilters": "应用筛选",
    "davisScore": "戴维斯评分",
    "addToStrategy": "添加到策略",
    "riskSettings": "风险设置",
    "investmentAmount": "投入金额",
    "hedgeRatio": "对冲比例",
    "maxDrawdown": "最大回撤容忍度",
    "autoRebalance": "启用自动转仓",
    "createStrategy": "创建策略"
  },
  "rebalance": {
    "title": "转仓机会",
    "priority": {
      "high": "高",
      "medium": "中",
      "low": "低"
    },
    "from": "从",
    "to": "到",
    "apyIncrease": "APY 提升",
    "totalCost": "总成本",
    "netProfit": "净收益",
    "paybackDays": "回本天数",
    "executionPlan": "执行计划",
    "confirm": "确认执行",
    "reject": "拒绝",
    "decideLater": "稍后决定"
  },
  "backtest": {
    "title": "策略回测验证",
    "period": "回测期间",
    "initialCapital": "初始资金",
    "marketCondition": "市场环境",
    "deltaNeutral": "Delta Neutral 策略",
    "pureLp": "纯 LP 策略",
    "finalValue": "最终价值",
    "totalReturn": "总收益",
    "annualReturn": "年化收益",
    "maxDrawdown": "最大回撤",
    "sharpeRatio": "夏普比率",
    "advantage": "优势"
  },
  "subscription": {
    "title": "选择适合您的计划",
    "basic": {
      "name": "基础版",
      "price": "$29/月",
      "subtitle": "适合个人投资者",
      "features": [
        "3个策略池监控",
        "每日自动再平衡",
        "基础风险保护",
        "社区支持"
      ]
    },
    "pro": {
      "name": "专业版",
      "price": "$99/月",
      "subtitle": "适合专业交易者",
      "badge": "最受欢迎",
      "features": [
        "无限策略池",
        "实时自动优化",
        "高级风险管理",
        "优先支持",
        "完整回测报告",
        "基础 API 访问",
        "自定义警报"
      ]
    },
    "enterprise": {
      "name": "机构版",
      "price": "$499/月",
      "subtitle": "适合机构和团队",
      "features": [
        "专业版所有功能",
        "定制策略开发",
        "完整 API 访问",
        "专属客户经理",
        "SLA 服务保障",
        "白标解决方案",
        "团队协作功能"
      ]
    },
    "selectPlan": "选择计划",
    "contactUs": "联系我们"
  }
}
```

### 日文（ja.json）

```json
{
  "common": {
    "loading": "読み込み中...",
    "error": "エラー",
    "success": "成功",
    "confirm": "確認",
    "cancel": "キャンセル",
    "save": "保存",
    "delete": "削除",
    "edit": "編集",
    "close": "閉じる",
    "next": "次へ",
    "previous": "前へ",
    "submit": "送信"
  },
  "nav": {
    "dashboard": "ダッシュボード",
    "strategy": "戦略設定",
    "backtest": "バックテスト",
    "subscription": "サブスクリプション",
    "rebalance": "リバランス",
    "connectWallet": "ウォレット接続",
    "disconnect": "切断"
  },
  "landing": {
    "hero": {
      "title": "インテリジェント DeFi 収益戦略",
      "subtitle": "年間収益率 173.6%、ドローダウンゼロ",
      "cta": "始める"
    },
    "features": {
      "highYield": {
        "title": "高収益",
        "description": "年間収益率 150% 以上"
      },
      "zeroRisk": {
        "title": "リスクゼロ",
        "description": "Delta Neutral 戦略で資本を保護"
      },
      "automated": {
        "title": "完全自動",
        "description": "スマートリバランスとリスク管理"
      }
    }
  },
  "dashboard": {
    "title": "ダッシュボード",
    "totalAssets": "総資産",
    "totalProfit": "総利益",
    "annualAPY": "年間 APY",
    "currentDelta": "現在の Delta",
    "maxDrawdown": "最大ドローダウン",
    "sharpeRatio": "シャープレシオ",
    "marketRegime": "市場状況",
    "positions": "現在のポジション",
    "type": "タイプ",
    "protocol": "プロトコル",
    "chain": "チェーン",
    "pair": "ペア",
    "amount": "金額",
    "apy": "APY",
    "status": "ステータス"
  },
  "strategy": {
    "title": "戦略を設定",
    "selectPools": "LP プールを選択",
    "filters": "フィルター",
    "minTVL": "最小 TVL",
    "minAPY": "最小 APY",
    "chains": "チェーン",
    "protocols": "プロトコル",
    "applyFilters": "フィルターを適用",
    "davisScore": "デイビススコア",
    "addToStrategy": "戦略に追加",
    "riskSettings": "リスク設定",
    "investmentAmount": "投資額",
    "hedgeRatio": "ヘッジ比率",
    "maxDrawdown": "最大ドローダウン許容度",
    "autoRebalance": "自動リバランスを有効化",
    "createStrategy": "戦略を作成"
  },
  "rebalance": {
    "title": "リバランス機会",
    "priority": {
      "high": "高",
      "medium": "中",
      "low": "低"
    },
    "from": "から",
    "to": "へ",
    "apyIncrease": "APY 増加",
    "totalCost": "総コスト",
    "netProfit": "純利益",
    "paybackDays": "回収日数",
    "executionPlan": "実行計画",
    "confirm": "実行を確認",
    "reject": "拒否",
    "decideLater": "後で決定"
  },
  "backtest": {
    "title": "戦略バックテスト検証",
    "period": "バックテスト期間",
    "initialCapital": "初期資本",
    "marketCondition": "市場状況",
    "deltaNeutral": "Delta Neutral 戦略",
    "pureLp": "純粋な LP 戦略",
    "finalValue": "最終価値",
    "totalReturn": "総収益",
    "annualReturn": "年間収益",
    "maxDrawdown": "最大ドローダウン",
    "sharpeRatio": "シャープレシオ",
    "advantage": "優位性"
  },
  "subscription": {
    "title": "プランを選択",
    "basic": {
      "name": "ベーシック",
      "price": "$29/月",
      "subtitle": "個人投資家向け",
      "features": [
        "3つの戦略プール監視",
        "毎日の自動リバランス",
        "基本的なリスク保護",
        "コミュニティサポート"
      ]
    },
    "pro": {
      "name": "プロフェッショナル",
      "price": "$99/月",
      "subtitle": "プロトレーダー向け",
      "badge": "最も人気",
      "features": [
        "無制限の戦略プール",
        "リアルタイム自動最適化",
        "高度なリスク管理",
        "優先サポート",
        "完全なバックテストレポート",
        "基本的な API アクセス",
        "カスタムアラート"
      ]
    },
    "enterprise": {
      "name": "エンタープライズ",
      "price": "$499/月",
      "subtitle": "機関投資家とチーム向け",
      "features": [
        "プロの全機能",
        "カスタム戦略開発",
        "完全な API アクセス",
        "専任アカウントマネージャー",
        "SLA 保証",
        "ホワイトラベルソリューション",
        "チームコラボレーション"
      ]
    },
    "selectPlan": "プランを選択",
    "contactUs": "お問い合わせ"
  }
}
```

---

## 🎯 使用指南

### 步驟 1: 在 Lovable 中粘貼提示詞
複製上面的完整提示詞，粘貼到 Lovable 對話框。

### 步驟 2: 創建翻譯文件
在 `src/i18n/locales/` 目錄下創建所有語言的 JSON 文件。

### 步驟 3: 更新組件
將所有硬編碼的文本替換為 `t('key')` 函數調用。

### 步驟 4: 測試
切換語言並確保所有文本正確顯示。

---

## 📝 注意事項

1. **完整性**: 確保所有翻譯文件包含相同的鍵
2. **格式化**: 使用 `Intl` API 進行數字、貨幣和日期格式化
3. **SEO**: 為每種語言添加適當的 meta 標籤
4. **性能**: 使用懶加載翻譯文件以減少初始加載時間
5. **維護**: 建立翻譯更新流程，確保新功能的文本及時翻譯

---

**這份多語言支持方案將使 LiveaLittle DeFi 能夠服務全球用戶！** 🌍

