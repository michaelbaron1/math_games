import yfinance as yf
import pandas as pd
from datetime import datetime
from pyxirr import xirr

# ── CONFIG ────────────────────────────────────────────────────────────────────
START_DATE          = "2015-02-01"   # simulation start date
START_VOO           = 25_000         # initial VOO dollars
START_UPRO          = 2_000              # initial UPRO dollars

MONTHLY_CONTRIBUTION = 1_000         # base monthly reinvestment ($)
CONTRIBUTION_GROWTH  = 0.15           # annual growth rate on contribution (0.10 = 10%)

UP_FLOOR   = 0.50   # fraction of contribution auto-invested in VOO on up months
UP_CAP     = 0.04   # VOO return at which 100% goes to VOO

DOWN_FLOOR = 0.5   # fraction of contribution auto-invested in UPRO on down months
DOWN_CAP   = 0.08   # |VOO return| at which 100% goes to UPRO

MAX_UPRO_FRACTION = 0.5  # UPRO can never exceed this share of total portfolio

END_DATE = "2025-02-01"   # set to "2023-01-01" to cap simulation, None = run to present
# ─────────────────────────────────────────────────────────────────────────────

print(f"""
── Config ───────────────────────────────────────────────────────
  Start date:           {START_DATE}
  Initial investment:   ${START_VOO + START_UPRO:>10,.2f}  (VOO: ${START_VOO:,.2f} / UPRO: ${START_UPRO:,.2f})
  Monthly contribution: ${MONTHLY_CONTRIBUTION:>10,.2f}
  Contribution growth:  {CONTRIBUTION_GROWTH*100:.1f}% / year
  Up floor/cap:         {UP_FLOOR*100:.0f}% floor / {UP_CAP*100:.0f}% cap
  Down floor/cap:       {DOWN_FLOOR*100:.0f}% floor / {DOWN_CAP*100:.0f}% cap
  Max UPRO:             {MAX_UPRO_FRACTION*100:.0f}%
─────────────────────────────────────────────────────────────────
""")


def fetch_monthly_prices(ticker: str, start: str) -> pd.Series:
    df = yf.download(ticker, start=start, end=END_DATE, interval="1mo", auto_adjust=True, progress=False)
    result = df["Close"]
    if isinstance(result, pd.DataFrame):
        result = result.iloc[:, 0]
    return result


def fetch_latest_price(ticker: str) -> float:
    if END_DATE:
        end = pd.to_datetime(END_DATE)
        start = (end - pd.Timedelta(days=7)).strftime("%Y-%m-%d")
        df = yf.download(ticker, start=start, end=END_DATE, interval="1d", auto_adjust=True, progress=False)
    else:
        df = yf.download(ticker, period="5d", interval="1d", auto_adjust=True, progress=False)
    result = df["Close"]
    if isinstance(result, pd.DataFrame):
        result = result.iloc[:, 0]
    return float(result.iloc[-1])


def allocate(contribution: float, voo_return: float,
             voo_value: float, upro_value: float) -> tuple[float, float]:
    """
    Returns (voo_invest, upro_invest) for a given month's VOO return.
    Enforces the MAX_UPRO_FRACTION cap on total portfolio after investment.
    """
    total = voo_value + upro_value

    if voo_return >= 0:
        if voo_return >= UP_CAP:
            voo_invest  = contribution
            upro_invest = 0.0
        else:
            voo_invest  = UP_FLOOR * contribution + (voo_return / UP_CAP) * (1 - UP_FLOOR) * contribution
            upro_invest = (1 - voo_return / UP_CAP) * (1 - UP_FLOOR) * contribution
    else:
        abs_ret = abs(voo_return)
        if abs_ret >= DOWN_CAP:
            voo_invest  = 0.0
            upro_invest = contribution
        else:
            upro_invest = DOWN_FLOOR * contribution + (abs_ret / DOWN_CAP) * (1 - DOWN_FLOOR) * contribution
            voo_invest  = (1 - abs_ret / DOWN_CAP) * (1 - DOWN_FLOOR) * contribution

    new_total    = total + contribution
    max_upro     = MAX_UPRO_FRACTION * new_total
    allowed_upro = max(0.0, max_upro - upro_value)
    if upro_invest > allowed_upro:
        overflow    = upro_invest - allowed_upro
        upro_invest = allowed_upro
        voo_invest += overflow

    return voo_invest, upro_invest


def run_benchmark(ticker: str, prices: pd.DataFrame, start_total: float) -> float:
    first_date = prices.index[0]
    shares = start_total / prices.loc[first_date, ticker]

    cash_flows = [-start_total]
    cash_dates = [first_date.date()]
    contribution = MONTHLY_CONTRIBUTION
    year_tracker = first_date.year

    for date in prices.index[1:]:
        if date.year != year_tracker:
            contribution *= (1 + CONTRIBUTION_GROWTH)
            year_tracker = date.year
        shares += contribution / prices.loc[date, ticker]
        cash_flows.append(-contribution)
        cash_dates.append(date.date())

    final_value = shares * prices.iloc[-1][ticker]
    cash_flows.append(final_value)
    cash_dates.append(prices.index[-1].date())

    return xirr(cash_dates, cash_flows) * 100


def run_simulation():
    print(f"Fetching price data from {START_DATE}…")
    voo_prices  = fetch_monthly_prices("VOO",  START_DATE)
    upro_prices = fetch_monthly_prices("UPRO", START_DATE)

    prices = pd.DataFrame({"VOO": voo_prices, "UPRO": upro_prices}).dropna()
    prices.index = pd.to_datetime(prices.index).tz_localize(None)

    voo_ret  = prices["VOO"].pct_change()

    first_date  = prices.index[0]
    voo_shares  = START_VOO  / prices.loc[first_date, "VOO"]
    upro_shares = START_UPRO / prices.loc[first_date, "UPRO"] if START_UPRO > 0 else 0.0

    records = []
    contribution = MONTHLY_CONTRIBUTION
    year_tracker = first_date.year

    cash_flows = [-(START_VOO + START_UPRO)]
    cash_dates = [first_date.date()]

    for i, date in enumerate(prices.index[1:], start=1):
        if date.year != year_tracker:
            contribution *= (1 + CONTRIBUTION_GROWTH)
            year_tracker  = date.year

        voo_price  = prices.loc[date, "VOO"]
        upro_price = prices.loc[date, "UPRO"]
        ret        = voo_ret.loc[date]

        voo_value  = voo_shares  * voo_price
        upro_value = upro_shares * upro_price

        cash_flows.append(-contribution)
        cash_dates.append(date.date())

        voo_invest, upro_invest = allocate(contribution, ret, voo_value, upro_value)

        voo_shares  += voo_invest  / voo_price
        upro_shares += upro_invest / upro_price

        voo_value_after  = voo_shares  * voo_price
        upro_value_after = upro_shares * upro_price
        total_after      = voo_value_after + upro_value_after
        
        records.append({
            "date":           date.strftime("%Y-%m"),
            "voo_return_pct": round(ret * 100, 2),
            "voo_invest":     round(voo_invest, 2),
            "upro_invest":    round(upro_invest, 2),
            "contribution":   round(contribution, 2),
            "voo_value":      round(voo_value_after, 2),
            "upro_value":     round(upro_value_after, 2),
            "total_value":    round(total_after, 2),
            "upro_pct":       round(upro_value_after / total_after * 100, 2),
        })
        

    df = pd.DataFrame(records)

    pd.set_option("display.max_rows", None)
    pd.set_option("display.float_format", "{:,.2f}".format)
   # print("\n── Monthly Detail ───────────────────────────────────────────────")
   # print(df.to_string(index=False))

    # current prices: daily close on/before END_DATE, or latest if no END_DATE
    voo_current  = fetch_latest_price("VOO")
    upro_current = fetch_latest_price("UPRO")

    final_value    = voo_shares * voo_current + upro_shares * upro_current
    upro_final_pct = (upro_shares * upro_current) / final_value * 100 if final_value > 0 else 0.0
    total_contributed = START_VOO + START_UPRO + MONTHLY_CONTRIBUTION * len(df)

    cash_flows.append(final_value)
    cash_dates.append(pd.to_datetime(END_DATE).date() if END_DATE else datetime.today().date())

    print("\n── Summary ──────────────────────────────────────────────────────")
    print(f"  Period:               {df.iloc[0]['date']} → {df.iloc[-1]['date']}")
    print(f"  Total contributed:    ${total_contributed:>12,.2f}")
    print(f"  Final portfolio:      ${final_value:>12,.2f}")
    print(f"  Net gain:             ${final_value - total_contributed:>12,.2f}")
    print(f"  Final UPRO share:     {upro_final_pct:.2f}%")
    print(f"  Max UPRO % (any mo):  {df['upro_pct'].max()}%")

    annualized_return = xirr(cash_dates, cash_flows) * 100
    print(f"  Annualized return (XIRR): {annualized_return:.2f}%")
    print(f"  Total return:         {((final_value - total_contributed) / total_contributed) * 100:.2f}%")

    print(f"------- BENCHMARKS ----------")
    voo_only_xirr  = run_benchmark("VOO",  prices, START_VOO + START_UPRO)
    upro_only_xirr = run_benchmark("UPRO", prices, START_VOO + START_UPRO)
    print(f"  Benchmark VOO only (XIRR):  {voo_only_xirr:.2f}%")
    print(f"  Benchmark UPRO only (XIRR): {upro_only_xirr:.2f}%")

    voo_raw_return  = (voo_current  / prices.loc[prices.index[0], "VOO"]  - 1) * 100
    upro_raw_return = (upro_current / prices.loc[prices.index[0], "UPRO"] - 1) * 100
    print(f"  VOO % return:           {voo_raw_return:.2f}%")
    print(f"  UPRO % return:          {upro_raw_return:.2f}%")


if __name__ == "__main__":
    run_simulation()