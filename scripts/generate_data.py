from __future__ import annotations

import argparse
import math
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd


EVENT_TYPES = ["page_view", "product_view", "add_to_cart", "checkout", "purchase"]


def _rand_choice_weighted(options: list[str], weights: list[float]) -> str:
    return random.choices(options, weights=weights, k=1)[0]


def generate(
    *,
    days: int,
    users: int,
    avg_sessions_per_user: float,
    avg_events_per_session: float,
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    random.seed(seed)

    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    start = now - timedelta(days=days)

    user_ids = [f"u_{i:05d}" for i in range(1, users + 1)]
    product_ids = [f"p_{i:04d}" for i in range(1, 101)]
    product_names = [f"Product {i:03d}" for i in range(1, 101)]
    product_prices = {pid: float(rng.uniform(9.0, 199.0)) for pid in product_ids}

    # Sessions per user (Poisson-like)
    sessions_per_user = rng.poisson(lam=max(avg_sessions_per_user, 0.1), size=users)
    sessions_per_user = np.clip(sessions_per_user, 1, None)

    events_rows: list[dict] = []
    orders_rows: list[dict] = []

    order_counter = 1

    for uid, n_sessions in zip(user_ids, sessions_per_user):
        for s in range(int(n_sessions)):
            session_id = f"s_{uid}_{s:03d}"
            session_start = start + timedelta(
                seconds=int(rng.integers(0, int((now - start).total_seconds())))
            )

            # Events per session
            n_events = int(max(3, rng.poisson(lam=max(avg_events_per_session, 1.0))))

            # Choose a "primary product" for the session
            prod_idx = int(rng.integers(0, len(product_ids)))
            product_id = product_ids[prod_idx]
            product_name = product_names[prod_idx]
            price = product_prices[product_id]

            # Simulate a rough funnel: more views than carts; more carts than checkouts; more checkouts than purchases.
            # We’ll always include page_view + product_view; then probabilistically include downstream steps.
            include_add = rng.random() < 0.35
            include_checkout = include_add and (rng.random() < 0.55)
            include_purchase = include_checkout and (rng.random() < 0.60)

            base_sequence = ["page_view", "product_view"]
            if include_add:
                base_sequence.append("add_to_cart")
            if include_checkout:
                base_sequence.append("checkout")
            if include_purchase:
                base_sequence.append("purchase")

            # Fill remaining events with extra page/product views to make sessions feel realistic.
            while len(base_sequence) < n_events:
                base_sequence.insert(
                    1,
                    _rand_choice_weighted(
                        ["page_view", "product_view"], weights=[0.45, 0.55]
                    ),
                )

            # Timestamp each event within a 10–20 minute window.
            session_duration_sec = int(rng.integers(8 * 60, 22 * 60))
            offsets = sorted(rng.integers(0, session_duration_sec, size=len(base_sequence)))

            for event_type, offset in zip(base_sequence, offsets):
                ts = session_start + timedelta(seconds=int(offset))
                events_rows.append(
                    {
                        "event_id": f"e_{uid}_{session_id}_{int(ts.timestamp())}",
                        "event_ts": ts.isoformat(),
                        "event_date": ts.date().isoformat(),
                        "user_id": uid,
                        "session_id": session_id,
                        "event_type": event_type,
                        "product_id": product_id,
                        "product_name": product_name,
                        "device": _rand_choice_weighted(
                            ["mobile", "desktop", "tablet"], weights=[0.62, 0.33, 0.05]
                        ),
                        "country": _rand_choice_weighted(
                            ["US", "IN", "CA", "UK", "AU"], weights=[0.35, 0.30, 0.12, 0.13, 0.10]
                        ),
                        "traffic_source": _rand_choice_weighted(
                            ["organic", "paid", "referral", "email", "direct"],
                            weights=[0.40, 0.22, 0.14, 0.08, 0.16],
                        ),
                    }
                )

            if include_purchase:
                quantity = int(max(1, rng.poisson(lam=1.2)))
                revenue = round(price * quantity * float(rng.uniform(0.9, 1.05)), 2)
                orders_rows.append(
                    {
                        "order_id": f"o_{order_counter:07d}",
                        "order_ts": (session_start + timedelta(seconds=session_duration_sec)).isoformat(),
                        "order_date": (session_start + timedelta(seconds=session_duration_sec)).date().isoformat(),
                        "user_id": uid,
                        "session_id": session_id,
                        "product_id": product_id,
                        "product_name": product_name,
                        "quantity": quantity,
                        "unit_price": round(price, 2),
                        "revenue": revenue,
                        "currency": "USD",
                    }
                )
                order_counter += 1

    events = pd.DataFrame(events_rows)
    orders = pd.DataFrame(orders_rows)

    # Make types nicer for BI tools
    if not events.empty:
        events.loc[:, "event_ts"] = pd.to_datetime(events["event_ts"], utc=True)
        events.loc[:, "event_date"] = pd.to_datetime(events["event_date"])
    if not orders.empty:
        orders.loc[:, "order_ts"] = pd.to_datetime(orders["order_ts"], utc=True)
        orders.loc[:, "order_date"] = pd.to_datetime(orders["order_date"])

    return events, orders


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate synthetic product analytics data.")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--users", type=int, default=800)
    parser.add_argument("--avg-sessions-per-user", type=float, default=3.2)
    parser.add_argument("--avg-events-per-session", type=float, default=8.5)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    data_dir = project_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    events, orders = generate(
        days=args.days,
        users=args.users,
        avg_sessions_per_user=args.avg_sessions_per_user,
        avg_events_per_session=args.avg_events_per_session,
        seed=args.seed,
    )

    # Keep files small (free-tier friendly)
    events.to_csv(data_dir / "events.csv", index=False)
    orders.to_csv(data_dir / "orders.csv", index=False)

    # Parquet is optional (requires pyarrow; on some Python versions it may not install easily).
    wrote_parquet = False
    try:
        events.to_parquet(data_dir / "events.parquet", index=False)
        orders.to_parquet(data_dir / "orders.parquet", index=False)
        wrote_parquet = True
    except Exception as e:  # noqa: BLE001
        print("Skipping Parquet output (optional). Reason:", str(e))

    print(f"Wrote {len(events):,} events -> data/events.csv")
    print(f"Wrote {len(orders):,} orders -> data/orders.csv")
    if wrote_parquet:
        print("Also wrote Parquet -> data/(events|orders).parquet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

