import { setText } from "../../shared/time.js";
import { logError } from "../../shared/errors.js";

export async function loadDepth() {
    const body = document.getElementById("depth-body");
    try {
        const res = await fetch("/market/orderbook/QRLUSDT?limit=10");
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        const bids = data.bids || data.data?.bids || [];
        const asks = data.asks || data.data?.asks || [];
        const rows = [];
        for (let i = 0; i < 5; i++) {
            const b = bids[i] || [];
            const a = asks[i] || [];
            rows.push(
                `<tr><td>${i + 1}</td><td>${b.price ?? b[0] ?? "--"}</td><td>${b.quantity ?? b[1] ?? "--"}</td><td>${a.price ?? a[0] ?? "--"}</td><td>${a.quantity ?? a[1] ?? "--"}</td></tr>`
            );
        }
        body.innerHTML = rows.join("");
    } catch (err) {
        body.innerHTML = '<tr><td colspan="5" class="error">深度載入失敗</td></tr>';
        logError("Depth failed", err);
    }
}

export default loadDepth;
