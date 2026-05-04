import yfinance as yf
import pandas as pd
from datetime import datetime
from pyxirr import xirr

# ── CONFIG ────────────────────────────────────────────────────────────────────
START_DATE          = "2018-01-01"   # simulation start date
START_VOO           = 10_000          # initial VOO dollars
START_UPRO          = 000          # initial UPRO dollars

MONTHLY_CONTRIBUTION = 1_000         # base monthly reinvestment ($)
CONTRIBUTION_GROWTH  = 0.00          # annual growth rate on contribution (0.10 = 10%)

UP_FLOOR   = 0.50   # fraction of contribution auto-invested in VOO on up months
UP_CAP     = 0.04   # VOO return at which 100% goes to VOO (6%)

DOWN_FLOOR = 0.25   # fraction of contribution auto-invested in UPRO on down months
DOWN_CAP   = 0.08   # |VOO return| at which 100% goes to UPRO (8%)

MAX_UPRO_FRACTION = 0.0  # UPRO can never exceed this share of total portfolio
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
    df = yf.download(ticker, start=start, interval="1mo", auto_adjust=True, progress=False)
    return df["Close"].squeeze()


def allocate(contribution: float, voo_return: float,
             voo_value: float, upro_value: float) -> tuple[float, float]:
    """
    Returns (voo_invest, upro_invest) for a given month's VOO return.
    Enforces the 50% UPRO cap on total portfolio after investment.
    """
    total = voo_value + upro_value

    if voo_return >= 0:
        # up month
        if voo_return >= UP_CAP:
            voo_invest  = contribution
            upro_invest = 0.0
        else:
            voo_invest  = UP_FLOOR * contribution + (voo_return / UP_CAP) * (1 - UP_FLOOR) * contribution
            upro_invest = (1 - voo_return / UP_CAP) * (1 - UP_FLOOR) * contribution
    else:
        # down month
        abs_ret = abs(voo_return)
        if abs_ret >= DOWN_CAP:
            voo_invest  = 0.0
            upro_invest = contribution
        else:
            upro_invest = DOWN_FLOOR * contribution + (abs_ret / DOWN_CAP) * (1 - DOWN_FLOOR) * contribution
            voo_invest  = (1 - abs_ret / DOWN_CAP) * (1 - DOWN_FLOOR) * contribution

    # enforce 50% UPRO cap
    new_total      = total + contribution
    max_upro       = MAX_UPRO_FRACTION * new_total
    allowed_upro   = max(0.0, max_upro - upro_value)
    if upro_invest > allowed_upro:
        overflow    = upro_invest - allowed_upro
        upro_invest = allowed_upro
        voo_invest += overflow

    return voo_invest, upro_invest


def run_simulation():
    print(f"Fetching price data from {START_DATE}…")
    voo_prices  = fetch_monthly_prices("VOO",  START_DATE)
    upro_prices = fetch_monthly_prices("UPRO", START_DATE)

    # align on common dates
    prices = pd.DataFrame({"VOO": voo_prices, "UPRO": upro_prices}).dropna()
    prices.index = pd.to_datetime(prices.index).tz_localize(None)

    # monthly returns
    voo_ret  = prices["VOO"].pct_change()
    upro_ret = prices["UPRO"].pct_change()

    # initial share counts at first available close
    first_date  = prices.index[0]
    voo_shares  = START_VOO  / prices.loc[first_date, "VOO"]
    upro_shares = START_UPRO / prices.loc[first_date, "UPRO"]

    records = []
    contribution = MONTHLY_CONTRIBUTION
    year_tracker = first_date.year

    # before the loop
    cash_flows = [-(START_VOO + START_UPRO)]
    cash_dates = [prices.index[0].date()]

    for i, date in enumerate(prices.index[1:], start=1):
        # apply annual contribution growth at year boundary
        if date.year != year_tracker:
            contribution *= (1 + CONTRIBUTION_GROWTH)
            year_tracker  = date.year

        voo_price   = prices.loc[date, "VOO"]
        upro_price  = prices.loc[date, "UPRO"]
        ret         = voo_ret.loc[date]

        voo_value   = voo_shares  * voo_price
        upro_value  = upro_shares * upro_price

        cash_flows.append(-contribution)
        cash_dates.append(date.date())

        total_before = voo_value + upro_value

        voo_invest, upro_invest = allocate(contribution, ret, voo_value, upro_value)

        voo_shares  += voo_invest  / voo_price
        upro_shares += upro_invest / upro_price

        voo_value_after  = voo_shares  * voo_price
        upro_value_after = upro_shares * upro_price
        total_after      = voo_value_after + upro_value_after

        records.append({
            "date":            date.strftime("%Y-%m"),
            "voo_return_pct":  round(ret * 100, 2),
            "voo_invest":      round(voo_invest, 2),
            "upro_invest":     round(upro_invest, 2),
            "contribution":    round(contribution, 2),
            "voo_value":       round(voo_value_after, 2),
            "upro_value":      round(upro_value_after, 2),
            "total_value":     round(total_after, 2),
            "upro_pct":        round(upro_value_after / total_after * 100, 2),
        })

    df = pd.DataFrame(records)
    """
    # ── print summary ─────────────────────────────────────────────────────────
    pd.set_option("display.max_rows", None)
    pd.set_option("display.float_format", "{:,.2f}".format)
    print("\n── Monthly Detail ───────────────────────────────────────────────")
    print(df.to_string(index=False))
    """
    total_contributed = START_VOO + START_UPRO + MONTHLY_CONTRIBUTION * (len(df))
    final_value = df.iloc[-1]["total_value"]
    print("\n── Summary ──────────────────────────────────────────────────────")
    print(f"  Period:               {df.iloc[0]['date']} → {df.iloc[-1]['date']}")
    print(f"  Total contributed:    ${total_contributed:>12,.2f}")
    print(f"  Final portfolio:      ${final_value:>12,.2f}")
    print(f"  Net gain:             ${final_value - total_contributed:>12,.2f}")
    print(f"  Final UPRO share:     {df.iloc[-1]['upro_pct']}%")
    print(f"  Max UPRO % (any mo):  {df['upro_pct'].max()}%")
    cash_flows.append(final_value)
    cash_dates.append(prices.index[-1].date())

    annualized_return = xirr(cash_dates, cash_flows) * 100
    print(f"  Annualized return (XIRR): {annualized_return:.2f}%")


if __name__ == "__main__":
    run_simulation()