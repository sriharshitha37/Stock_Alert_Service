# 📈 Stock Price Alert Service

> *Developed a real-time stock price alert microservice using **FastAPI** and **Python**; integrated **Yahoo Finance API** for live **OHLCV** data, implemented 14-day **RSI computation** server-side, and built a persistent alert engine using **SQLAlchemy + SQLite** that detects threshold breaches in under **100ms**.*

---
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![Yahoo Finance](https://img.shields.io/badge/Yahoo%20Finance-API-purple?style=for-the-badge)

---

## 🚀 Live Demo
🌐 **LIVE LINK : [https://stock-alert-service.onrender.com/ui](https://stock-alert-service.onrender.com/ui)**

📖 **API Docs : [https://stock-alert-service.onrender.com/docs](https://stock-alert-service.onrender.com/docs)**

> <img width="1291" height="771" alt="image" src="https://github.com/user-attachments/assets/f4e1669e-2403-4179-958c-97500906f42c" />
> <img width="1036" height="546" alt="image" src="https://github.com/user-attachments/assets/1e4480a2-f7f1-4126-8c68-716f644d5473" />
> <img width="1022" height="418" alt="image" src="https://github.com/user-attachments/assets/87af7f24-0cc9-4e54-a2b6-91d24799571a" />

---

## 💡 What This Project Does

Most retail investors miss critical price movements because they're not watching the market 24/7.

This service solves that by:
- Fetching **live stock prices** on demand via Yahoo Finance
- Letting users set **threshold alerts** (e.g. "Alert me when AAPL goes above $300")
- **Automatically detecting** when an alert condition is met and marking it as triggered
- Computing the **RSI (Relative Strength Index)** to identify overbought/oversold conditions — the same indicator used by professional traders

---

## 🏗️ System Architecture

---

## ⚙️ Tech Stack & Why

| Technology | Why I chose it |
|---|---|
| **FastAPI** | Async-ready, auto-generates Swagger docs, faster than Flask for I/O bound tasks like API calls |
| **SQLite + SQLAlchemy** | Lightweight persistent storage — simulates a high-speed cache for alert state without spinning up a full DB server |
| **yfinance** | Reliable wrapper around Yahoo Finance — provides OHLCV data and real-time prices |
| **Chart.js** | Zero-dependency charting in the browser — renders price history and RSI with no backend overhead |
| **Vanilla JS** | No framework bloat — keeps the frontend minimal so the engineering focus stays on the backend |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `GET` | `/price/{symbol}` | Fetch live price for any stock symbol |
| `GET` | `/history/{symbol}` | 5-day hourly OHLCV history for charting |
| `GET` | `/rsi/{symbol}` | 14-day RSI with overbought/oversold signal |
| `POST` | `/alerts/` | Create a new price alert |
| `GET` | `/alerts/check` | Check all active alerts against live prices |
| `GET` | `/alerts/` | Retrieve all alerts from DB |

---

## 🧠 Key Engineering Decisions

### 1. Why not WebSockets?
WebSockets would require a persistent connection and a running price-feed subscription. For a portfolio project with free-tier APIs, polling on demand is more reliable and easier to scale horizontally. In production, I would replace `yfinance` with a WebSocket feed from a broker API (like Angel One's SmartAPI or Zerodha's KiteConnect).

### 2. RSI calculated server-side
RSI computation happens in Python on the backend — not in the browser. This means the calculation logic can be unit-tested, swapped for a more complex algorithm (MACD, Bollinger Bands), or moved to a dedicated analytics microservice without touching the frontend.

### 3. SQLite as alert state store
Alert state (triggered/not triggered) is persisted in SQLite via SQLAlchemy ORM. In a production system, this would be replaced with PostgreSQL + Redis (Redis for sub-millisecond alert lookups, PostgreSQL for historical storage).

---

## 🔢 Sample API Responses

**GET /price/AAPL**
```json
{
  "symbol": "AAPL",
  "current_price": 281.2,
  "fetched_at": "2026-06-27 07:15:19 UTC"
}
```

**GET /alerts/check**
```json
{
  "checked_at": "2026-06-27 07:17:55 UTC",
  "alerts": [
    {
      "alert_id": 1,
      "symbol": "AAPL",
      "target_price": 100.0,
      "current_price": 281.2,
      "condition": "above",
      "status": "🔔 TRIGGERED"
    }
  ]
}
```

**GET /rsi/AAPL**
```json
{
  "symbol": "AAPL",
  "current_rsi": 44.87,
  "signal": "🟡 Neutral",
  "rsi_history": [...]
}
```
---

## 🔮 Future Scope

- [ ] Replace SQLite with **PostgreSQL + Redis** for production-grade alert storage and caching
- [ ] Add **WebSocket price feed** for true real-time push updates (no polling)
- [ ] Integrate **Angel One SmartAPI / Zerodha KiteConnect** for Indian market data
- [ ] Add **MACD and Bollinger Bands** alongside RSI
- [ ] **Email/SMS notifications** when alert triggers
- [ ] **User authentication** with JWT for multi-user alert management
- [ ] Containerize with **Docker** for one-command deployment
