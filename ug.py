# app_enhanced.py
import streamlit as st
from cryptography.fernet import Fernet
import os, json, time, hashlib
from pathlib import Path
import base64
import datetime
import bcrypt

# -----------------------
# Configuration / folders
# -----------------------
BASE = Path.cwd()
USERS_FILE = BASE / "users.json"       # demo user DB (hashed passwords)
KEYS_DIR = BASE / "keys"
DATA_DIR = BASE / "data"               # encrypted files per user
LOGS_FILE = BASE / "logs.json"         # action logs
for p in (KEYS_DIR, DATA_DIR):
    p.mkdir(exist_ok=True)

# -----------------------
# Utilities
# -----------------------
def load_json(path):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}

def save_json(path, obj):
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")

def log_action(user, action, details=""):
    logs = load_json(LOGS_FILE)
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "user": user,
        "action": action,
        "details": details
    }
    logs.setdefault("entries", []).insert(0, entry)
    save_json(LOGS_FILE, logs)

# -----------------------
# Auth (demo: local hashed storage)
# -----------------------
def register_user(username, password):
    users = load_json(USERS_FILE)
    if username in users:
        return False, "Username already exists."
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt).decode()
    users[username] = {"password": hashed}
    save_json(USERS_FILE, users)
    # generate per-user fernet key
    key = Fernet.generate_key()
    (KEYS_DIR / f"{username}.key").write_bytes(key)
    log_action(username, "register")
    return True, "Account created."

def verify_user(username, password):
    users = load_json(USERS_FILE)
    if username not in users:
        return False
    hashed = users[username]["password"].encode()
    return bcrypt.checkpw(password.encode(), hashed)

# -----------------------
# Encryption helpers
# -----------------------
def load_key_for_user(username):
    key_path = KEYS_DIR / f"{username}.key"
    if not key_path.exists():
        # generate one if missing (shouldn't for registered users)
        key_path.write_bytes(Fernet.generate_key())
    return key_path.read_bytes()

def encrypt_and_save(username, uploaded_file, original_filename):
    key = load_key_for_user(username)
    f = Fernet(key)
    data = uploaded_file.getvalue()
    enc = f.encrypt(data)
    ts = int(time.time())
    outfname = f"{username}__{ts}__{original_filename}.enc"
    outpath = DATA_DIR / outfname
    outpath.write_bytes(enc)
    log_action(username, "upload_encrypt", outfname)
    return outpath

def search_user_files(username, keyword):
    key = load_key_for_user(username)
    f = Fernet(key)
    matches = []
    for path in DATA_DIR.glob(f"{username}__*.enc"):
        try:
            data = path.read_bytes()
            dec = f.decrypt(data).decode(errors="ignore")
            if keyword.lower() in dec.lower():
                matches.append({"file": path.name, "decrypted": dec})
        except Exception as e:
            # skip files that can't be decrypted
            pass
    log_action(username, "search", keyword)
    return matches

def list_user_files(username):
    return sorted([p.name for p in DATA_DIR.glob(f"{username}__*.enc")], reverse=True)

# -----------------------
# Optional Cloud Hooks (placeholders)
# -----------------------
# TODO: swap local storage for Firebase Storage / Firestore or AWS S3 & Cognito
# Example placeholders:
def upload_to_s3_placeholder(local_path, bucket_name):
    """Replace with boto3 upload code."""
    pass

def upload_to_firebase_placeholder(local_path, firebase_config):
    """Replace with pyrebase/firebase_admin code to upload file."""
    pass

# -----------------------
# Streamlit UI
# -----------------------
st.set_page_config(page_title="Encrypted Search - Enhanced", layout="wide")
st.title("🔐 Encrypted Search — Enhanced Web App")

# --- Sidebar: Auth / Navigation ---
if "auth_user" not in st.session_state:
    st.session_state.auth_user = None

with st.sidebar:
    st.header("Account")
    if st.session_state.auth_user:
        st.write("Signed in as:", st.session_state.auth_user)
        if st.button("Sign out"):
            st.session_state.auth_user = None
            st.experimental_rerun()
    else:
        auth_mode = st.radio("Action", ["Sign in", "Register"])
        uname = st.text_input("Username", key="uname")
        pwd = st.text_input("Password", type="password", key="pwd")
        if auth_mode == "Register":
            if st.button("Create account"):
                if not uname or not pwd:
                    st.error("Provide username & password")
                else:
                    ok, msg = register_user(uname, pwd)
                    if ok:
                        st.success(msg + " You can sign in now.")
                    else:
                        st.error(msg)
        else:
            if st.button("Sign in"):
                if verify_user(uname, pwd):
                    st.session_state.auth_user = uname
                    log_action(uname, "login")
                    st.success("Signed in.")
                    st.rerun()


                else:
                    st.error("Invalid credentials")

    st.markdown("---")
    st.header("Options")
    page = st.radio("Go to", ["Upload & Encrypt", "Search", "Dashboard", "Logs", "Settings"])

# --- Main area ---
user = st.session_state.auth_user
if not user:
    st.info("Please sign in or register from the left sidebar to continue.")
    st.stop()

if page == "Upload & Encrypt":
    st.subheader("☁️ Upload & Encrypt (per-user)")
    st.write("Upload a text or CSV file. The file will be encrypted with your per-user key.")
    uploaded = st.file_uploader("Choose a file to encrypt (txt/csv)", type=["txt", "csv"])
    if uploaded is not None:
        st.write("Filename:", uploaded.name, "| size:", uploaded.size)
        if st.button("Encrypt & Save"):
            outpath = encrypt_and_save(user, uploaded, uploaded.name)
            st.success(f"Encrypted and saved: {outpath.name}")
            st.write("You can download the encrypted file below:")
            with open(outpath, "rb") as f:
                btn = st.download_button("Download Encrypted File", f.read(), file_name=outpath.name)
            # optional: upload to cloud here
            st.info("TIP: To persist files across machines, enable cloud storage in Settings.")
elif page == "Search":
    st.subheader("🔎 Search Your Encrypted Files")
    kw = st.text_input("Keyword to search inside your encrypted files")
    if st.button("Search"):
        if not kw:
            st.warning("Enter a keyword.")
        else:
            results = search_user_files(user, kw)
            if not results:
                st.warning("No matches found.")
            else:
                st.success(f"{len(results)} match(es) found:")
                for r in results:
                    st.write("**File:**", r["file"])
                    st.code(r["decrypted"][:1000] + ("..." if len(r["decrypted"]) > 1000 else ""))
elif page == "Dashboard":
    st.subheader("📊 User Dashboard")
    user_files = list_user_files(user)
    st.metric("Encrypted files (you)", len(user_files))
    st.write("Files (recent first):")
    for f in user_files[:20]:
        st.write("-", f)
    # show key info
    key_path = KEYS_DIR / f"{user}.key"
    if key_path.exists():
        st.info("Your encryption key is stored locally. (For demo only.)")
        if st.checkbox("Show key (not recommended)"):
            st.code(key_path.read_text())
    st.markdown("---")
    st.write("Want to download your key or all encrypted data?")
    if st.button("Download my key"):
        key_bytes = load_key_for_user(user)
        st.download_button("Download key file", key_bytes, file_name=f"{user}.key")
    if st.button("Download all my encrypted files as ZIP (demo)"):
        # create in-memory zip
        import io, zipfile
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            for fname in user_files:
                z.writestr(fname, (DATA_DIR / fname).read_bytes())
        st.download_button("Download ZIP", buf.getvalue(), file_name=f"{user}_encrypted_files.zip")
elif page == "Logs":
    st.subheader("📋 Action Logs (admin / user history)")
    logs = load_json(LOGS_FILE).get("entries", [])
    st.write(f"Total events: {len(logs)}")
    # show recent logs
    for entry in logs[:200]:
        if entry["user"] == user or st.checkbox("Show all logs (admin)", key=f"alllogs_{entry['timestamp']}"):
            st.write(f"- {entry['timestamp']} — **{entry['user']}** — {entry['action']} — {entry['details']}")
elif page == "Settings":
    st.subheader("⚙️ Settings & Cloud Options (demo)")
    st.write("By default this demo stores data & keys locally. To use cloud storage or managed auth, follow the instructions below.")
    st.markdown("""
**Cloud integration options (choose one for production):**
- Firebase (Auth, Firestore, Storage) — recommended for small apps  
- AWS (Cognito for auth, S3 for storage) — recommended for enterprise
""")
    st.write("Demo toggles:")
    cloud_choice = st.selectbox("Persist files to", ["Local only", "Upload to Firebase (placeholder)", "Upload to AWS S3 (placeholder)"])
    st.write("If you pick Firebase/AWS you must implement server-side secure credentials and swap upload hooks in the code (`upload_to_firebase_placeholder` / `upload_to_s3_placeholder`).")
    st.markdown("**Security notes:**")
    st.write("""
- This demo uses local hashed passwords (bcrypt). For production, use Firebase Auth or AWS Cognito.  
- Never store raw keys or passwords in plaintext. Use KMS / Secrets Manager.  
- Ensure HTTPS, CSRF protections, and proper access control.
""")

# -----------------------
# End of app
# -----------------------


