from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
import yfinance as yf

from database import engine, get_db, Base
from models import Alert

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Stock Price Alert Service")


class AlertRequest(BaseModel):
    stock_symbol: str
    target_price: float
    condition: str


def get_live_price(symbol: str) -> float:
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="1d", interval="1m")
    if data.empty:
        raise HTTPException(status_code=404, detail=f"Could not fetch price for {symbol}")
    return round(float(data["Close"].iloc[-1]), 2)


@app.get("/")
def root():
    return {"message": "Stock Alert Service is running ✅"}


@app.get("/price/{symbol}")
def get_price(symbol: str):
    price = get_live_price(symbol.upper())
    return {
        "symbol": symbol.upper(),
        "current_price": price,
        "fetched_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    }


# --- NEW ROUTE: 5-day price history for chart ---
@app.get("/history/{symbol}")
def get_history(symbol: str):
    ticker = yf.Ticker(symbol.upper())
    data = ticker.history(period="5d", interval="1h")
    if data.empty:
        raise HTTPException(status_code=404, detail=f"No history for {symbol}")

    history = [
        {
            "time": str(ts.strftime("%d %b %H:%M")),
            "price": round(float(row["Close"]), 2)
        }
        for ts, row in data.iterrows()
    ]
    return {
        "symbol": symbol.upper(),
        "history": history,
        "high": round(float(data["Close"].max()), 2),
        "low": round(float(data["Close"].min()), 2),
        "change_pct": round(
            ((data["Close"].iloc[-1] - data["Close"].iloc[0]) / data["Close"].iloc[0]) * 100, 2
        )
    }


@app.post("/alerts/")
def create_alert(request: AlertRequest, db: Session = Depends(get_db)):
    if request.condition not in ["above", "below"]:
        raise HTTPException(status_code=400, detail="Condition must be 'above' or 'below'")
    alert = Alert(
        stock_symbol=request.stock_symbol.upper(),
        target_price=request.target_price,
        condition=request.condition
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return {"message": "Alert created ✅", "alert_id": alert.id, "details": request}


@app.get("/alerts/check")
def check_alerts(db: Session = Depends(get_db)):
    alerts = db.query(Alert).filter(Alert.triggered == False).all()
    if not alerts:
        return {"message": "No active alerts to check."}
    results = []
    for alert in alerts:
        try:
            current_price = get_live_price(alert.stock_symbol)
            triggered = False
            if alert.condition == "above" and current_price > alert.target_price:
                triggered = True
            elif alert.condition == "below" and current_price < alert.target_price:
                triggered = True
            if triggered:
                alert.triggered = True
                db.commit()
            results.append({
                "alert_id": alert.id,
                "symbol": alert.stock_symbol,
                "target_price": alert.target_price,
                "current_price": current_price,
                "condition": alert.condition,
                "status": "🔔 TRIGGERED" if triggered else "⏳ Watching"
            })
        except Exception as e:
            results.append({"alert_id": alert.id, "symbol": alert.stock_symbol, "error": str(e)})
    return {"checked_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"), "alerts": results}


@app.get("/alerts/")
def get_all_alerts(db: Session = Depends(get_db)):
    alerts = db.query(Alert).all()
    return {"total": len(alerts), "alerts": alerts}

def calculate_rsi(prices, period=14):
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    rsi_values = []
    for i in range(period, len(deltas)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        rs = avg_gain / avg_loss if avg_loss != 0 else 100
        rsi_values.append(round(100 - (100 / (1 + rs)), 2))

    return rsi_values


@app.get("/rsi/{symbol}")
def get_rsi(symbol: str):
    ticker = yf.Ticker(symbol.upper())
    data = ticker.history(period="1mo", interval="1d")
    if len(data) < 15:
        raise HTTPException(status_code=400, detail="Not enough data for RSI")

    prices = list(data["Close"])
    dates = [str(ts.strftime("%d %b")) for ts in data.index]
    rsi_values = calculate_rsi(prices)
    rsi_dates = dates[15:]  # align with RSI output

    current_rsi = rsi_values[-1]
    if current_rsi >= 70:
        signal = "🔴 Overbought — potential sell signal"
    elif current_rsi <= 30:
        signal = "🟢 Oversold — potential buy signal"
    else:
        signal = "🟡 Neutral"

    return {
        "symbol": symbol.upper(),
        "current_rsi": current_rsi,
        "signal": signal,
        "rsi_history": [{"date": d, "rsi": r} for d, r in zip(rsi_dates, rsi_values)]
    }
app.mount("/", StaticFiles(directory="static", html=True), name="static")