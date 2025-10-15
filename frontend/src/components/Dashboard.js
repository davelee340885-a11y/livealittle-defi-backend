import React, { useState, useEffect } from 'react';

// 模擬從後端 API 獲取數據
const fetchTopPools = async () => {
    // 在實際應用中，這裡會是一個 fetch("/api/top-pools") 調用
    // 為了演示，我們直接使用後端生成的 CSV 文件內容（簡化版）
    const mockData = [
        { "鏈": "Base", "協議": "aerodrome-slipstream", "代幣": "AVNT-USDC", "總鎖倉量 (USD)": "$1.83M", "總年化收益率 (%)": "73501.39%" },
        { "鏈": "Base", "協議": "aerodrome-slipstream", "代幣": "USDC-VFY", "總鎖倉量 (USD)": "$2.02M", "總年化收益率 (%)": "63276.48%" },
        { "鏈": "Base", "協議": "aerodrome-slipstream", "代幣": "WETH-USDC", "總鎖倉量 (USD)": "$1.26M", "總年化收益率 (%)": "32724.76%" },
        { "鏈": "Ethereum", "協議": "pendle", "代幣": "HWHLP", "總鎖倉量 (USD)": "$2.22M", "總年化收益率 (%)": "8703.91%" },
        { "鏈": "Ethereum", "協議": "uniswap-v3", "代幣": "WETH-ADO", "總鎖倉量 (USD)": "$2.86M", "總年化收益率 (%)": "1727.64%" },
        { "鏈": "Base", "協議": "aerodrome-slipstream", "代幣": "USDC-CBBTC", "總鎖倉量 (USD)": "$6.45M", "總年化收益率 (%)": "1524.84%" },
    ];
    return mockData;
};

const Dashboard = () => {
    const [pools, setPools] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            const data = await fetchTopPools();
            setPools(data);
            setLoading(false);
        };
        loadData();
    }, []);

    if (loading) {
        return <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>正在加載數據...</div>;
    }

    return (
        <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>
            <h1 style={{ marginBottom: "1.5rem", borderBottom: "2px solid #eee", paddingBottom: "0.5rem" }}>
                DeFi 數據監控儀表板 (MVP)
            </h1>
            <h2 style={{ fontSize: "1.2rem", marginBottom: "1rem" }}>Top 高收益池 (TVL > $1M)</h2>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                    <tr style={{ backgroundColor: "#f8f8f8" }}>
                        {pools.length > 0 && Object.keys(pools[0]).map(key => (
                            <th key={key} style={{ padding: "0.75rem", border: "1px solid #ddd", textAlign: "left" }}>{key}</th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {pools.map((pool, index) => (
                        <tr key={index}>
                            {Object.values(pool).map((value, i) => (
                                <td key={i} style={{ padding: "0.75rem", border: "1px solid #ddd" }}>{value}</td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default Dashboard;

