import os
import sys
import time
import json
import logging
import threading
from queue import Queue
from datetime import datetime, timezone
from collections import deque
import websocket
import numpy as np
from scipy.signal import hilbert
from scipy.stats import entropy
import requests

# =====================================================================
# CONFIGURATION & ADVANCED HYPERPARAMETERS
# =====================================================================
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID")

SYMBOL = "frxXAUUSD"
# GANTI angka 1089 di bawah ini dengan APP_ID milikmu dari https://api.deriv.com/apps
DERIV_APP_ID = os.environ.get("DERIV_APP_ID", "1089") 
DERIV_WS_URL = f"wss://ws.derivws.com/websockets/v3?app_id={DERIV_APP_ID}"

DATA_WINDOW = 500       
ANTI_SPAM_COOLDOWN = 180 
MIN_TP_POINTS = 5.0     

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] ASI Core: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# =====================================================================
# ANTI-BLOCK TELEGRAM QUEUE ENGINE
# =====================================================================
class AntiBlockTelegramDispatcher(threading.Thread):
    def __init__(self, token, chat_id):
        super().__init__(daemon=True)
        self.token = token
        self.chat_id = chat_id
        self.queue = Queue()
        self.last_sent_time = 0
        self.api_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def enqueue_signal(self, data):
        current_time = time.time()
        if current_time - self.last_sent_time < ANTI_SPAM_COOLDOWN:
            logging.info("Sinyal ditahan oleh sistem Anti-Spam Cooldown.")
            return
        self.queue.put(data)

    def run(self):
        while True:
            data = self.queue.get()
            if data is None:
                break
            
            direction = "🟢 BUY (SNIPER INSTANT)" if data["signal"] == "BUY" else "🔴 SELL (SNIPER INSTANT)"
            
            message = (
                f"⚡ **ASI PERFECTED QUANTUM SIGNAL** ⚡\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📊 **Instrument:** XAUUSD (Gold)\n"
                f"🎯 **Action:** {direction}\n"
                f"💵 **Entry Price:** `{data['price']:.2f}`\n"
                f"🛡️ **Stop Loss (Dynamic Tight):** `{data['sl']:.2f}` (~{data['sl_pips']:.2f} pts)\n"
                f"🚀 **Take Profit (Min 50 Poin):** `{data['tp']:.2f}` (~{data['tp_pips']:.2f} pts)\n"
                f"⚖️ **Risk-Reward Ratio:** `1 : {data['rr_ratio']:.1f}`\n"
                f"🧠 **Model Accuracy Confidence:** `{data['confidence']:.2f}%`\n"
                f"🌀 **Topo-Entropy Index:** `{data['entropy']:.4f}`\n"
                f"📐 **Macro Alignment Vector:** `{data['macro_vector']:.2f}`\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"⚠️ *Model Execution: Multi-Scale Topo-Behavioral Alignment.*"
            )
            
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }

            try:
                res = requests.post(self.api_url, json=payload, timeout=8)
                if res.status_code == 200:
                    logging.info("Sinyal Telegram berhasil dikirim!")
                    self.last_sent_time = time.time()
                else:
                    logging.error(f"Gagal Mengirim Telegram: {res.text}")
            except Exception as e:
                logging.error(f"Error Telegram Dispatcher: {e}")
            
            self.queue.task_done()
            time.sleep(2.0)

# =====================================================================
# MAXIMAL PRECISION ASI CORE ENGINE
# =====================================================================
class QuantumTopoBehavioralEngine:
    def __init__(self, window_size=DATA_WINDOW):
        self.prices = deque(maxlen=window_size)
        self.adaptive_threshold_modifier = 0.0
        
    def push_tick(self, price):
        self.prices.append(float(price))

    def _compute_topological_entropy(self, data):
        if len(data) < 50:
            return 0.5
        tau, m = 2, 3
        N = len(data) - (m - 1) * tau
        if N <= 0:
            return 0.5
        embedded = np.array([data[i:i + m * tau:tau] for i in range(N)])
        distances = np.linalg.norm(embedded[:, np.newaxis] - embedded, axis=2)
        r = 0.2 * np.std(data)
        cm = np.sum(distances < r) / (N * N)
        return float(-cm * np.log(cm + 1e-12))

    def _compute_macro_trend_vector(self, data):
        analytic_signal = hilbert(data - np.mean(data))
        phase = np.unwrap(np.angle(analytic_signal))
        short_phase_diff = phase[-1] - phase[-20]
        long_phase_diff = phase[-1] - phase[-100]
        return float(short_phase_diff + long_phase_diff)

    def _compute_thermodynamic_state(self, data):
        hist, _ = np.histogram(data, bins=10, density=True)
        hist = hist[hist > 0]
        sys_entropy = entropy(hist)
        
        k_max = 5
        L = []
        for k in range(1, k_max + 1):
            Lk = 0
            for m in range(k):
                idxs = np.arange(m, len(data), k)
                if len(idxs) > 1:
                    diffs = np.abs(np.diff(data[idxs]))
                    Lk += np.sum(diffs) * (len(data) - 1) / (len(idxs) * k)
            L.append(np.log(Lk + 1e-12))
        
        x = np.log(1.0 / np.arange(1, k_max + 1))
        fractal_dim, _ = np.polyfit(x, L, 1)
        return sys_entropy, fractal_dim

    def analyze_market_state(self):
        if len(self.prices) < 200:
            return None

        prices_arr = np.array(self.prices)
        
        recent_diff = np.abs(np.diff(prices_arr[-5:]))
        if np.max(recent_diff) > 3.5:
            return None

        topo_entropy = self._compute_topological_entropy(prices_arr)
        sys_entropy, fractal_dim = self._compute_thermodynamic_state(prices_arr)
        macro_vector = self._compute_macro_trend_vector(prices_arr)
        
        curr_price = prices_arr[-1]
        std_price = np.std(prices_arr[-40:])
        
        local_atr = np.mean(np.abs(np.diff(prices_arr[-15:])))
        dynamic_sl_dist = float(np.clip(local_atr * 2.5, 0.40, 1.20))

        micro_momentum = (curr_price - prices_arr[-15]) / (std_price + 1e-5)
        
        signal = "HOLD"
        confidence = 0.0
        strict_entropy_threshold = 0.25 - self.adaptive_threshold_modifier
        
        if topo_entropy < strict_entropy_threshold and sys_entropy < 1.05:
            if micro_momentum > 1.95 and macro_vector > 1.5 and fractal_dim < 1.40:
                signal = "BUY"
                confidence = float(min(99.9, (micro_momentum / 2.0) * 80 + (1.40 - fractal_dim) * 20))
            elif micro_momentum < -1.95 and macro_vector < -1.5 and fractal_dim < 1.40:
                signal = "SELL"
                confidence = float(min(99.9, (abs(micro_momentum) / 2.0) * 80 + (1.40 - fractal_dim) * 20))

        if signal == "HOLD":
            return None

        calculated_tp_dist = max(MIN_TP_POINTS, dynamic_sl_dist * 6.0 * (confidence / 50.0))
        rr_ratio = calculated_tp_dist / dynamic_sl_dist

        return {
            "signal": signal,
            "confidence": confidence,
            "price": curr_price,
            "sl": curr_price - dynamic_sl_dist if signal == "BUY" else curr_price + dynamic_sl_dist,
            "tp": curr_price + calculated_tp_dist if signal == "BUY" else curr_price - calculated_tp_dist,
            "sl_pips": dynamic_sl_dist,
            "tp_pips": calculated_tp_dist,
            "rr_ratio": rr_ratio,
            "entropy": topo_entropy,
            "macro_vector": macro_vector,
            "fractal": fractal_dim
        }

# =====================================================================
# AUTONOMOUS RUNNER & WATCHDOG
# =====================================================================
class ASIXauusdBot:
    def __init__(self):
        self.engine = QuantumTopoBehavioralEngine()
        self.dispatcher = AntiBlockTelegramDispatcher(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
        self.dispatcher.start()
        self.ws = None
        self.last_tick_time = time.time()

    def is_market_open(self):
        now = datetime.now(timezone.utc)
        day = now.weekday()
        if day in [5, 6]:
            return False
        if day == 4 and now.hour >= 22:
            return False
        return True

    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            self.last_tick_time = time.time()
            
            if "history" in data and "prices" in data["history"]:
                prices = data["history"]["prices"]
                for p in prices:
                    self.engine.push_tick(p)
                logging.info(f"Warm-up selesai. {len(prices)} history ticks dimuat.")

            if "tick" in data and "quote" in data["tick"]:
                price = data["tick"]["quote"]
                self.engine.push_tick(price)
                
                if not self.is_market_open():
                    return

                result = self.engine.analyze_market_state()
                if result and result["signal"] in ["BUY", "SELL"]:
                    logging.info(f"SIAP EKSEKUSI: {result['signal']} @ {result['price']}")
                    self.dispatcher.enqueue_signal(result)
        except Exception as e:
            logging.error(f"Error Message Process: {e}")

    def on_error(self, ws, error):
        logging.error(f"WebSocket Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        logging.warning("Koneksi terputus! Reconnecting...")

    def on_open(self, ws):
        logging.info("Terhubung ke Real-Time Data Stream Deriv (frxXAUUSD).")
        # Request subscribe terpisah setelah koneksi stabil
        ws.send(json.dumps({"ticks_history": SYMBOL, "end": "latest", "count": 300, "style": "ticks"}))
        time.sleep(0.5)
        ws.send(json.dumps({"ticks": SYMBOL, "subscribe": 1}))

    def run(self):
        while True:
            try:
                self.ws = websocket.WebSocketApp(
                    DERIV_WS_URL,
                    on_open=self.on_open,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close
                )
                
                ws_thread = threading.Thread(target=lambda: self.ws.run_forever(ping_interval=10, ping_timeout=5))
                ws_thread.daemon = True
                ws_thread.start()

                while ws_thread.is_alive():
                    time.sleep(10)
                    # Kirim manual Ping untuk menjaga alur WebSocket Deriv tetap hidup
                    try:
                        if self.ws and self.ws.sock and self.ws.sock.connected:
                            self.ws.send(json.dumps({"ping": 1}))
                    except Exception:
                        pass

                    if time.time() - self.last_tick_time > 30 and self.is_market_open():
                        logging.warning("Watchdog Alert: Data tick membeku >30 detik! Restocking socket...")
                        self.ws.close()
                        break

            except Exception as e:
                logging.error(f"System Failure: {e}. Auto-restart dalam 5 detik...")
                time.sleep(5)

if __name__ == "__main__":
    bot = ASIXauusdBot()
    bot.run()
