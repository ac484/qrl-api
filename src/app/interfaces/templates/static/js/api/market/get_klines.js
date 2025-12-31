import { formatTime } from "../../shared/time.js";
import { logError } from "../../shared/errors.js";

export async function loadKlines() {
    const body = document.getElementById("kline-body");
    try {
        const res = await fetch("/market/klines/QRLUSDT?interval=1m&limit=5");
        if (res.status === 404) {
            body.innerHTML = '<tr><td colspan="5" class="hint">僅支援 QRLUSDT</td></tr>';
            return;
        }
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        const klines = data.data || [];
        if (!klines.length) {
            body.innerHTML = '<tr><td colspan="5" class="hint">無K線資料</td></tr>';
            return;
        }
        body.innerHTML = klines
            .slice(-5)
            .map((k) => {
                const openTime = k.open_time ?? k[0];
                const open = k.open ?? k[1];
                const high = k.high ?? k[2];
                const low = k.low ?? k[3];
                const close = k.close ?? k[4];
                return `<tr><td>${formatTime(openTime)}</td><td>${open}</td><td>${high}</td><td>${low}</td><td>${close}</td></tr>`;
            })
            .join("");
    } catch (err) {
        body.innerHTML = '<tr><td colspan="5" class="hint">無K線資料</td></tr>';
        logError("Klines failed", err);
    }
}

export default loadKlines;
