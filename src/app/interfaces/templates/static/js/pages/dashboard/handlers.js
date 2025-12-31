import { refreshAll } from "../../refresh.js";
import { setText } from "../../shared/time.js";

const WS_BASE = "wss://wbs-api.mexc.com/ws";
const WS_CHANNELS = [
    "spot@public.aggre.bookTicker.v3.api.pb@100ms@QRLUSDT",
    "spot@public.aggre.deals.v3.api.pb@100ms@QRLUSDT",
    "spot@public.kline.v3.api.pb@QRLUSDT@Min1",
];

let ws;

function setWsStatus(text, ok = false) {
    const el = document.getElementById("ws-status");
    if (!el) return;
    el.textContent = text;
    el.style.background = ok ? "rgba(34,197,94,0.12)" : "rgba(239,68,68,0.12)";
    el.style.color = ok ? "var(--success)" : "var(--danger)";
}

function parseProtoLike(data) {
    if (typeof data === "string") {
        try {
            return JSON.parse(data);
        } catch {
            return null;
        }
    }
    if (data instanceof ArrayBuffer) {
        try {
            const text = new TextDecoder().decode(data);
            return JSON.parse(text);
        } catch {
            return null;
        }
    }
    return null;
}

function handleWsMessage(msg) {
    if (!msg || typeof msg !== "object") return;
    if (msg.publicbookticker) {
        const t = msg.publicbookticker;
        setText("best-bid", `${t.bidprice || "--"} / ${t.bidquantity || "--"}`);
        setText("best-ask", `${t.askprice || "--"} / ${t.askquantity || "--"}`);
    }
    if (msg.publicdeals && Array.isArray(msg.publicdeals.dealsList)) {
        const [first] = msg.publicdeals.dealsList;
        if (first) {
            const tbody = document.getElementById("agg-body");
            if (tbody) {
                tbody.innerHTML = `<tr><td>${new Date(first.time).toLocaleString("zh-TW")}</td><td>${first.tradetype || "--"}</td><td>${first.price}</td><td>${first.quantity}</td></tr>`;
            }
        }
    }
}

function startWebsocket() {
    if (ws) ws.close();
    ws = new WebSocket(WS_BASE);
    ws.binaryType = "arraybuffer";
    ws.onopen = () => {
        setWsStatus("WS: 已連線", true);
        ws.send(JSON.stringify({ method: "SUBSCRIPTION", params: WS_CHANNELS }));
    };
    ws.onmessage = (ev) => {
        const parsed = parseProtoLike(ev.data);
        if (parsed && parsed.method === "PING") {
            ws.send(JSON.stringify({ method: "PONG" }));
            return;
        }
        handleWsMessage(parsed);
    };
    ws.onclose = () => {
        setWsStatus("WS: 連線中斷");
        setTimeout(startWebsocket, 5000);
    };
    ws.onerror = () => setWsStatus("WS: 錯誤");
}

export function setupDashboard() {
    const refreshBtn = document.getElementById("refresh-btn");
    if (refreshBtn) {
        refreshBtn.addEventListener("click", refreshAll);
    }
    refreshAll();
    startWebsocket();
}

export default setupDashboard;
