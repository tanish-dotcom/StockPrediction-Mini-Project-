from flask import Flask, render_template, request, redirect, session
import yfinance as yf
import random
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import os
import requests
import json

app = Flask(__name__)
app.secret_key = "trademind-secret-key"

USD_INR = 83.0


# ======================
# HELPER FUNCTIONS
# ======================
##def get_index_price(symbol, fallback):
##    try:
##        data = yf.Ticker(symbol).history(period="1d")
##        if data.empty:
##            return fallback
##        return round(data["Close"].iloc[-1], 2)
##    except:
##        return fallback
##
##
##def get_gold_10gm():
##    try:
##        gold_usd_oz = yf.Ticker("GC=F").history(period="1d")["Close"].iloc[-1]
##        return round((gold_usd_oz * USD_INR / 31.1035) * 10, 2)
##    except:
##        return 62000
##
##
##def get_silver_kg():
##    try:
##        silver_usd_oz = yf.Ticker("SI=F").history(period="1d")["Close"].iloc[-1]
##        return round((silver_usd_oz * USD_INR) / 0.0311035, 2)
##    except:
##        return 72000
##
##
### ======================
### LANDING
### ======================
##@app.route("/")
##def landing():
##    # Fetch live market data for landing page
##    nifty_price = get_index_price("^NSEI", 22450)
##    sensex_price = get_index_price("^BSESN", 74000)
##    banknifty_price = get_index_price("^NSEBANK", 47800)
##    
##    gold_price = get_gold_10gm()
##    silver_price = get_silver_kg()
##    
##    try:
##        df_dates = yf.download("^NSEI", period="5d", interval="1d", progress=False)
##        dates = df_dates.index.strftime("%a, %b %d").tolist()
##        nifty_data = df_dates["Close"].round(2).tolist()
##    except:
##        dates = ["Day 1","Day 2","Day 3","Day 4","Day 5"]
##        nifty_data = [nifty_price - 200, nifty_price - 120, nifty_price - 60, nifty_price - 30, nifty_price]
##    
##    return render_template(
##        "welcome.html",
##        nifty_price=nifty_price,
##        sensex_price=sensex_price,
##        banknifty_price=banknifty_price,
##        gold_price=gold_price,
##        silver_price=silver_price,
##        dates=dates,
##        nifty_data=nifty_data
##    )
##
##
### ======================
### SIGNUP
### ======================
##@app.route("/signup", methods=["GET", "POST"])
##def signup():
##
##    error = None
##
##    if request.method == "POST":
##
##        fullname = request.form["fullname"]
##        username = request.form["username"]
##        email = request.form["email"]
##        password = request.form["password"]
##        confirm = request.form["confirm_password"]
##        risk = request.form["risk"]
##
##        if password != confirm:
##            error = "Passwords do not match ❌"
##            return render_template("signup.html", error=error)
##
##        hashed_password = generate_password_hash(password)
##
##        try:
##            conn = sqlite3.connect("trademind.db")
##            c = conn.cursor()
##
##            c.execute("""
##                INSERT INTO users (fullname, username, email, password, risk_profile)
##                VALUES (?, ?, ?, ?, ?)
##            """, (fullname, username, email, hashed_password, risk))
##
##            conn.commit()
##            conn.close()
##
##            return redirect("/login")
##
##        except sqlite3.IntegrityError:
##            error = "Username or Email already exists ❌"
##
##    return render_template("signup.html", error=error)
##
##
### ======================
### LOGIN
### ======================
##@app.route("/login", methods=["GET", "POST"])
##def login():
##
##    error = None
##
##    if "captcha" not in session:
##        session["captcha"] = str(random.randint(1000, 9999))
##
##    if request.method == "POST":
##
##        username = request.form.get("username")
##        password = request.form.get("password")
##        user_captcha = request.form.get("captcha_input")
##
##        if user_captcha != session["captcha"]:
##            error = "Captcha incorrect ❌"
##            session["captcha"] = str(random.randint(1000, 9999))
##
##        else:
##            conn = sqlite3.connect("trademind.db")
##            c = conn.cursor()
##            c.execute("SELECT * FROM users WHERE username=?", (username,))
##            user = c.fetchone()
##            conn.close()
##
##            if user and check_password_hash(user[4], password):
##                session["authenticated"] = True
##                session["user"] = username
##                session.pop("captcha", None)
##                return redirect("/market")
##            else:
##                error = "Invalid username or password ❌"
##
##    return render_template(
##        "user_info.html",
##        captcha=session["captcha"],
##        error=error
##    )
##
##
### ======================
### MARKET DASHBOARD
### ======================
##@app.route("/market")
##def market():
##
##    if not session.get("authenticated"):
##        return redirect("/login")
##
##    try:
##        df = yf.download("^NSEI", period="5d", interval="1d")
##        dates = df.index.strftime("%Y-%m-%d").tolist()
##        nifty = df["Close"].round(2).tolist()
##        nifty_kpi = nifty[-1]
##    except:
##        dates = ["D1","D2","D3","D4","D5"]
##        nifty = [22400,22450,22500,22600,22700]
##        nifty_kpi = nifty[-1]
##
##    try:
##        sensex = yf.download("^BSESN", period="5d")["Close"].round(2).tolist()
##        sensex_kpi = sensex[-1]
##    except:
##        sensex = [73000,73200,73400,73500,73600]
##        sensex_kpi = sensex[-1]
##
##    try:
##        banknifty = yf.download("^NSEBANK", period="5d")["Close"].round(2).tolist()
##        banknifty_kpi = banknifty[-1]
##    except:
##        banknifty = [47000,47200,47400,47500,47600]
##        banknifty_kpi = banknifty[-1]
##
##    # GOLD
##    try:
##        gold_usd = yf.Ticker("GC=F").history(period="1d")["Close"].iloc[-1]
##        gold_kpi = round((gold_usd * USD_INR / 31.1035) * 10, 2)
##        gold = [gold_kpi*0.97, gold_kpi*0.98, gold_kpi*0.99, gold_kpi*1.01, gold_kpi]
##    except:
##        gold_kpi = 62000
##        gold = [61000,61500,61800,62000,62200]
##
##    # SILVER
##    try:
##        silver_usd = yf.Ticker("SI=F").history(period="1d")["Close"].iloc[-1]
##        silver_kpi = round((silver_usd * USD_INR) / 0.0311035, 2)
##        silver = [silver_kpi*0.97, silver_kpi*0.98, silver_kpi*0.99, silver_kpi*1.01, silver_kpi]
##    except:
##        silver_kpi = 72000
##        silver = [71000,71500,71800,72000,72200]
##
##    stock_names = ["RELIANCE","TCS","INFY","HDFCBANK","ICICI"]
##    stock_prices = [2900,3850,1620,1500,1100]
##
##
##    conn = sqlite3.connect("trademind.db")
##    c = conn.cursor() 
##    c.execute("""
##    SELECT stock, action, present, target, stop_loss, timeframe, created_at
##    FROM prediction_history
##    WHERE username=?
##    ORDER BY created_at DESC
##    LIMIT 10
##    """,(session["user"],))
##    
##    history = c.fetchall()
##    
##    conn.close()
##
##    return render_template(
##    "market.html",
##    dates=dates,
##    nifty=nifty,
##    sensex=sensex,
##    banknifty=banknifty,
##    gold=gold,
##    silver=silver,
##    stock_names=stock_names,
##    stock_prices=stock_prices,
##    nifty_kpi=nifty_kpi,
##    sensex_kpi=sensex_kpi,
##    banknifty_kpi=banknifty_kpi,
##    gold_kpi=gold_kpi,
##    silver_kpi=silver_kpi,
##    history=history
##    )
##
##
### ======================
### PREDICTION
### ======================
##@app.route("/predict", methods=["GET", "POST"])
##def predict():
##
##    if not session.get("authenticated"):
##        return redirect("/login")
##
##    result = None
##    error = None
##
##    form = {
##        "risk": "",
##        "horizon": "",
##        "capital": "",
##        "sector": "",
##        "mood": "",
##        "timeframe": ""
##    }
##
##    if request.method == "POST":
##
##        for key in form:
##            form[key] = request.form.get(key)
##
##        stocks_by_sector = {}
##
##        with open("stocks.csv", newline='') as csvfile:
##            reader = csv.DictReader(csvfile)
##            for row in reader:
##                sector = row["sector"].strip()
##                symbol = row["symbol"].strip()
##
##                stocks_by_sector.setdefault(sector, []).append(symbol)
##
##        selected_sector = form["sector"]
##
##        if selected_sector not in stocks_by_sector:
##            error = "No stocks found for selected sector ❌"
##            return render_template("predict.html", result=result, form=form, error=error)
##
##        stock = random.choice(stocks_by_sector[selected_sector])
##
##        ticker_symbol = stock + ".NS"
##
##        try:
##            ticker = yf.Ticker(ticker_symbol)
##            hist = ticker.history(period="5d")
##            present = round(hist["Close"].iloc[-1], 2)
##        except:
##            present = 500
##
##        if form["timeframe"] == "1M":
##            target = round(present * 1.05, 2)
##        elif form["timeframe"] == "3M":
##            target = round(present * 1.12, 2)
##        else:
##            target = round(present * 1.20, 2)
##
##        stop_loss = round(present * 0.95, 2)
##
##        action = "BUY" if form["risk"] == "High" else "HOLD"
##
##        result = {
##            "stock": stock,
##            "sector": selected_sector,
##            "action": action,
##            "present": present,
##            "target": target,
##            "stop_loss": stop_loss,
##            "timeframe": form["timeframe"]
##        }
##
##        # Save prediction to history
##        conn = sqlite3.connect("trademind.db")
##        c = conn.cursor()
##        c.execute("""
##        INSERT INTO prediction_history
##        (username, stock, sector, action, present, target, stop_loss, timeframe)
##        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
##        """,(
##        session["user"],
##        stock,
##        selected_sector,
##        action,
##        present,
##        target,
##        stop_loss,
##        form["timeframe"]
##        ))
##        
##        conn.commit()
##        conn.close()
##        
##    return render_template("predict.html", result=result, form=form, error=error)
##
##
### ======================
### LOGOUT
### ======================
##@app.route("/logout")
##def logout():
##    session.clear()
##    return redirect("/")
##
##
### ======================
### RUN
### ======================
##if __name__ == "__main__":
##    app.run(debug=True)##



from flask import Flask, render_template, request, redirect, session, url_for
import yfinance as yf
import random
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import os
import secrets
from urllib.parse import urlencode
import json
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
try:
    import requests
except ImportError:
    requests = None


app = Flask(__name__)
app.secret_key = "trademind-secret-key"

# Session Configuration for OAuth
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

USD_INR = 83.0

# ======================
# DATABASE INIT
# ======================
def init_db():
    with sqlite3.connect("trademind.db", timeout=10) as conn:
        c = conn.cursor()

        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fullname TEXT,
                username TEXT UNIQUE,
                email TEXT UNIQUE,
                password TEXT,
                risk_profile TEXT,
                google_id TEXT,
                oauth_provider TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS prediction_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                stock TEXT,
                sector TEXT,
                action TEXT,
                present REAL,
                target REAL,
                stop_loss REAL,
                timeframe TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

init_db()


# ======================
# HELPER FUNCTIONS
# ======================

def get_stock_price(symbol, fallback=None):
    try:
        data = yf.Ticker(symbol).history(period="1d")

        if data.empty:
            return fallback

        return round(data["Close"].iloc[-1], 2)

    except:
        return fallback


# 🟡 INDICES → Yahoo
def get_index_price(symbol, fallback):
    try:
        data = yf.Ticker(symbol).history(period="1d")
        if data.empty:
            return fallback
        return round(data["Close"].iloc[-1], 2)
    except:
        return fallback


# 🟡 5-Day Chart → Yahoo
def get_5day_series(symbol, fallback_prices):
    try:
        df = yf.download(symbol, period="5d", interval="1d", progress=False)
        if df.empty:
            return ["D1","D2","D3","D4","D5"], fallback_prices

        dates = df.index.strftime("%a").tolist()
        prices = df["Close"].round(2).tolist()

        return dates, prices
    except:
        return ["D1","D2","D3","D4","D5"], fallback_prices


# GOLD / SILVER
def get_gold_10gm():
    try:
        gold = yf.Ticker("GC=F").history(period="1d")["Close"].iloc[-1]
        return round((gold * USD_INR / 31.1035) * 10, 2)
    except:
        return 62000


def get_silver_kg():
    try:
        silver = yf.Ticker("SI=F").history(period="1d")["Close"].iloc[-1]
        return round((silver * USD_INR) / 0.0311035, 2)
    except:
        return 72000


# ======================
# ROUTES
# ======================

@app.route("/")
def landing():
    nifty_price = get_index_price("^NSEI", 22450)
    sensex_price = get_index_price("^BSESN", 74000)
    banknifty_price = get_index_price("^NSEBANK", 47800)

    gold_price = get_gold_10gm()
    silver_price = get_silver_kg()

    dates, nifty_data = get_5day_series("^NSEI", [22400,22450,22500,22600,22700])

    return render_template(
        "welcome.html",
        nifty_price=nifty_price,
        sensex_price=sensex_price,
        banknifty_price=banknifty_price,
        gold_price=gold_price,
        silver_price=silver_price,
        dates=dates,
        nifty_data=nifty_data
    )


@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = None

    if request.method == "POST":
        fullname = request.form["fullname"]
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm = request.form["confirm_password"]
        risk = request.form["risk"]

        if password != confirm:
            return render_template("signup.html", error="Passwords do not match ❌")

        hashed_password = generate_password_hash(password)

        try:
            with sqlite3.connect("trademind.db", timeout=10) as conn:
                c = conn.cursor()
                c.execute("""
                    INSERT INTO users (fullname, username, email, password, risk_profile)
                    VALUES (?, ?, ?, ?, ?)
                """, (fullname, username, email, hashed_password, risk))
                conn.commit()
            return redirect("/login")
        except sqlite3.IntegrityError:
            error = "Username or Email already exists ❌"

    return render_template("signup.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if "captcha" not in session:
        session["captcha"] = str(random.randint(1000, 9999))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user_captcha = request.form.get("captcha_input")

        if user_captcha != session["captcha"]:
            error = "Captcha incorrect ❌"
        else:
            with sqlite3.connect("trademind.db", timeout=10) as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM users WHERE username=?", (username,))
                user = c.fetchone()

            if user and check_password_hash(user[4], password):
                session["authenticated"] = True
                session["user"] = username
                session.pop("captcha", None)
                return redirect("/market")
            else:
                error = "Invalid credentials ❌"

    return render_template("user_info.html", captcha=session["captcha"], error=error)


@app.route("/market")
def market():

    if not session.get("authenticated"):
        return redirect("/login")

    dates, nifty = get_5day_series("^NSEI", [22400,22450,22500,22600,22700])
    nifty_kpi = nifty[-1] if nifty else 22450

    _, sensex = get_5day_series("^BSESN", [73000,73200,73400,73500,73600])
    sensex_kpi = sensex[-1] if sensex else 74000

    _, banknifty = get_5day_series("^NSEBANK", [47000,47200,47400,47500,47600])
    banknifty_kpi = banknifty[-1] if banknifty else 47800

    gold_kpi = get_gold_10gm()
    gold = [gold_kpi*0.97, gold_kpi*0.98, gold_kpi*0.99, gold_kpi*1.01, gold_kpi]

    silver_kpi = get_silver_kg()
    silver = [silver_kpi*0.97, silver_kpi*0.98, silver_kpi*0.99, silver_kpi*1.01, silver_kpi]

    # Use Indian stocks for dashboard
    stock_names = ["RELIANCE","TCS","INFY","HDFCBANK","ICICIBANK"]
    stock_prices = []
    for s in stock_names:
        price = get_stock_price(s+".NS", fallback=1000)
        stock_prices.append(price)

    with sqlite3.connect("trademind.db", timeout=10) as conn:
        c = conn.cursor()
        c.execute("""
        SELECT stock, action, present, target, stop_loss, timeframe, created_at
        FROM prediction_history
        WHERE username=?
        ORDER BY created_at DESC
        LIMIT 10
        """, (session["user"],))
        history = c.fetchall()

    return render_template(
        "market.html",
        dates=dates,
        nifty=nifty,
        sensex=sensex,
        banknifty=banknifty,
        gold=gold,
        silver=silver,
        stock_names=stock_names,
        stock_prices=stock_prices,
        nifty_kpi=nifty_kpi,
        sensex_kpi=sensex_kpi,
        banknifty_kpi=banknifty_kpi,
        gold_kpi=gold_kpi,
        silver_kpi=silver_kpi,
        history=history
    )


@app.route("/predict", methods=["GET", "POST"])
def predict():

    if not session.get("authenticated"):
        return redirect("/login")

    result = None
    error = None

    form = {
        "risk": "",
        "horizon": "",
        "capital": "",
        "sector": "",
        "mood": "",
        "timeframe": ""
    }

    if request.method == "POST":
        for key in form:
            form[key] = request.form.get(key)

        stocks_by_sector = {}
        try:
            with open("stocks.csv", newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    stocks_by_sector.setdefault(row["sector"], []).append(row["symbol"])
        except Exception as e:
            return render_template("predict.html", error="Stock list not found ❌", form=form, result=None)

        sector = form["sector"]
        if not sector or sector not in stocks_by_sector:
            return render_template("predict.html", error="No stocks found for selected sector ❌", form=form, result=None)

        stock = random.choice(stocks_by_sector[sector])
        present = get_stock_price(stock, fallback=None)
        if present is None:
            return render_template("predict.html", error="Stock data not available ❌", form=form, result=None)

        # Realistic prediction logic
        change = random.uniform(1.03, 1.15)
        target = round(present * change, 2)
        stop_loss = round(present * random.uniform(0.90, 0.97), 2)
        action = "BUY" if form["risk"] == "High" else "HOLD"

        result = {
            "stock": stock,
            "sector": sector,
            "action": action,
            "present": present,
            "target": target,
            "stop_loss": stop_loss,
            "timeframe": form["timeframe"]
        }

        try:
            with sqlite3.connect("trademind.db", timeout=10) as conn:
                c = conn.cursor()
                c.execute("""
                    INSERT INTO prediction_history
                    (username, stock, sector, action, present, target, stop_loss, timeframe)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (session["user"], stock, sector, action, present, target, stop_loss, form["timeframe"]))
                conn.commit()
        except Exception as e:
            return render_template("predict.html", error="Could not save prediction ❌", form=form, result=result)

    return render_template("predict.html", result=result, form=form, error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ======================
# GOOGLE OAUTH
# ======================

# Google OAuth Configuration
# Set these environment variables in your system:
# GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "YOUR_GOOGLE_CLIENT_ID_HERE")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "YOUR_GOOGLE_CLIENT_SECRET_HERE")
GOOGLE_REDIRECT_URI = "http://127.0.0.1:5000/auth/google/callback"

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


@app.route("/auth/google")
def auth_google():
    """Redirect to Google OAuth consent screen"""
    
    # Generate state to prevent CSRF attacks
    state = secrets.token_urlsafe(32)
    session["oauth_state"] = state
    session.modified = True  # Ensure session is saved
    
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state
    }
    
    return redirect(f"{GOOGLE_AUTH_URL}?{urlencode(params)}")


@app.route("/auth/google/callback")
def auth_google_callback():
    """Handle Google OAuth callback"""
    
    # Verify state to prevent CSRF
    state = request.args.get("state")
    stored_state = session.get("oauth_state")
    
    if not state or not stored_state or state != stored_state:
        return redirect("/login?error=csrf_validation_failed"), 400
    
    code = request.args.get("code")
    error = request.args.get("error")
    
    if error:
        return redirect(f"/login?error={error}")
    
    if not code:
        return redirect("/login?error=no_authorization_code"), 400
    
    # Exchange code for token
    if not requests:
        return redirect("/login?error=requests_library_not_available"), 500
    
    try:
        token_data = {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code"
        }
        
        token_response = requests.post(GOOGLE_TOKEN_URL, data=token_data)
        token_json = token_response.json()
        
        print(f"Token Response: {token_json}")  # DEBUG
        
        if "access_token" not in token_json:
            error_desc = token_json.get("error_description", "Unknown error")
            print(f"Token Error: {error_desc}")  # DEBUG
            return redirect(f"/login?error=invalid_token_response"), 400
        
        access_token = token_json["access_token"]
        
        # Get user info from Google
        headers = {"Authorization": f"Bearer {access_token}"}
        user_response = requests.get(GOOGLE_USER_INFO_URL, headers=headers)
        user_data = user_response.json()
        
        print(f"User Data: {user_data}")  # DEBUG
        
        if "error" in user_data:
            print(f"User Info Error: {user_data.get('error_description')}")  # DEBUG
            return redirect(f"/login?error=failed_to_get_user_info"), 400
        
        google_id = user_data.get("id")
        email = user_data.get("email")
        name = user_data.get("name", email.split("@")[0] if email else "User")
        
        if not google_id or not email:
            return redirect(f"/login?error=missing_user_data"), 400
        
        # Check if user exists
        with sqlite3.connect("trademind.db", timeout=10) as conn:
            c = conn.cursor()
            c.execute("SELECT username FROM users WHERE google_id=?", (google_id,))
            existing_user = c.fetchone()
            
            if existing_user:
                # User exists, log them in
                username = existing_user[0]
            else:
                # Create new user
                # Generate username from email
                base_username = email.split("@")[0]
                username = base_username
                counter = 1
                
                while True:
                    c.execute("SELECT id FROM users WHERE username=?", (username,))
                    if not c.fetchone():
                        break
                    username = f"{base_username}{counter}"
                    counter += 1
                
                # Insert new user with Google OAuth
                try:
                    c.execute("""
                        INSERT INTO users (fullname, username, email, password, risk_profile, google_id, oauth_provider)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (name, username, email, None, "Medium", google_id, "google"))
                    conn.commit()
                except sqlite3.IntegrityError as e:
                    return redirect(f"/login?error=user_creation_failed"), 400
        
        # Log user in
        session["authenticated"] = True
        session["user"] = username
        session.pop("oauth_state", None)
        
        return redirect("/market")
        
    except Exception as e:
        print(f"Google OAuth Error: {str(e)}")
        return redirect(f"/login?error=oauth_processing_error"), 500


if __name__ == "__main__":
    app.run(debug=True)