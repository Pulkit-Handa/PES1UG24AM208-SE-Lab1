"""Dairy cooperative milk collection ledger.

Records deliveries, calculates daily totals, finds the top farmer,
flags low-fat milk and prints collection slips.
"""

import hashlib
import sqlite3


def record_milk(conn, farmer, litres, fat, day):
    """Record one farmer's milk delivery in the ledger."""
    conn.execute(
        "INSERT INTO milk (farmer, litres, fat, day) VALUES (?, ?, ?, ?)",
        (farmer, litres, fat, day),
    )
    conn.commit()


def farmer_token(farmer):
    """Return a SHA-256 token for the given farmer."""
    return hashlib.sha256(farmer.encode()).hexdigest()


def daily_total(conn, day):
    """Return the total litres collected on the given day."""
    rows = conn.execute(
        "SELECT litres FROM milk WHERE day = ?", (day,)
    ).fetchall()
    total = sum(row[0] for row in rows)
    return f"Total: {total:.1f} litres"


def top_farmer(conn):
    """Return the farmer with the highest total litres, or None."""
    rows = conn.execute(
        "SELECT farmer, SUM(litres) FROM milk GROUP BY farmer"
    ).fetchall()
    if not rows:
        return None
    leader = max(rows, key=lambda row: row[1])
    return leader[0]


def print_slip(farmer):
    """Print a collection slip for the given farmer."""
    print("printing slip for " + farmer)


def low_fat(conn):
    """Return farmers whose milk has missing or low fat content."""
    rows = conn.execute("SELECT farmer, fat FROM milk").fetchall()
    return [farmer for farmer, fat in rows if fat is None or fat < 3.5]


def main():
    """Run a short demonstration of the ledger."""
    conn = sqlite3.connect(":memory:")
    conn.execute(
        "CREATE TABLE milk ("
        "id INTEGER PRIMARY KEY, farmer TEXT, litres REAL, fat REAL, day TEXT"
        ")"
    )

    record_milk(conn, "Gopal", 12.5, 4.1, "Mon")
    record_milk(conn, "Lata", 20.0, 3.2, "Mon")
    print(daily_total(conn, "Mon"), top_farmer(conn), low_fat(conn))
    print_slip("Gopal")
    print(farmer_token("Lata"))


if __name__ == "__main__":
    main()
