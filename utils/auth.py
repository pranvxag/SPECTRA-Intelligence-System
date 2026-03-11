"""
utils/auth.py — Lightweight RBAC authentication for SPECTRA
Supports:
  - Local username / bcrypt-hashed-password from secrets.toml
  - Google OAuth 2.0 (when client_id + client_secret are configured)
"""
from __future__ import annotations
import streamlit as st
import bcrypt
from typing import Optional


# ── Helpers ───────────────────────────────────────────────────────────────

def _local_users() -> dict:
    try:
        return dict(st.secrets.get("local_users", {}))
    except Exception:
        return {}


def _google_cfg() -> dict:
    try:
        return dict(st.secrets.get("google_oauth", {}))
    except Exception:
        return {}


def _admin_emails() -> list:
    try:
        return list(st.secrets.get("roles", {}).get("admin_emails", []))
    except Exception:
        return []


# ── Core Auth ─────────────────────────────────────────────────────────────

def login_with_password(username: str, password: str) -> bool:
    """
    Validate username/password against secrets.toml hashes.
    On success, sets session state and returns True.
    """
    users = _local_users()
    user_cfg = users.get(username)
    if not user_cfg:
        return False
    stored_hash = user_cfg.get("password_hash", "")
    try:
        valid = bcrypt.checkpw(password.encode(), stored_hash.encode())
    except Exception:
        valid = False
    if valid:
        st.session_state["auth_user"]        = username
        st.session_state["auth_display_name"]= user_cfg.get("display_name", username)
        st.session_state["auth_role"]        = user_cfg.get("role", "student")
        st.session_state["auth_method"]      = "password"
    return valid


def google_oauth_callback(token_email: str):
    """
    Called after Google OAuth callback resolves an email.
    Assigns admin role if email is in allowlist, else student.
    """
    admin_emails = _admin_emails()
    role = "admin" if token_email in admin_emails else "student"
    st.session_state["auth_user"]         = token_email
    st.session_state["auth_display_name"] = token_email.split("@")[0]
    st.session_state["auth_role"]         = role
    st.session_state["auth_method"]       = "google"


def logout():
    for key in ["auth_user", "auth_display_name", "auth_role", "auth_method"]:
        st.session_state.pop(key, None)
    st.rerun()


def is_authenticated() -> bool:
    return bool(st.session_state.get("auth_user"))


def get_role() -> str:
    return st.session_state.get("auth_role", "student")


def get_display_name() -> str:
    return st.session_state.get("auth_display_name", "User")


def is_admin() -> bool:
    return get_role() == "admin"


# ── Page Guards ───────────────────────────────────────────────────────────

def require_login():
    """
    Call at the top of every page.
    Blocks execution and shows login UI if not authenticated.
    """
    if not is_authenticated():
        _render_login_wall()
        st.stop()


def require_admin():
    """
    Call on admin-only pages.
    Shows Access Denied to non-admins and stops execution.
    """
    require_login()
    if not is_admin():
        _render_access_denied()
        st.stop()


# ── Login Wall UI ─────────────────────────────────────────────────────────

def _render_login_wall():
    st.markdown("""
    <style>
    .login-wrap {
        max-width: 480px;
        margin: 3rem auto;
    }
    .login-title {
        font-family: 'Syne', sans-serif;
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ffffff, #00D4FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.3rem;
    }
    .login-sub {
        text-align: center;
        color: #7A90B0;
        font-size: 0.85rem;
        margin-bottom: 2rem;
    }
    </style>
    <div class="login-wrap">
        <div class="login-title">⚡ SPECTRA</div>
        <div class="login-sub">Student Intelligence & Career Guidance System</div>
    </div>
    """, unsafe_allow_html=True)

    # Centre the form
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        tab_pw, tab_google = st.tabs(["🔑 Password Login", "🔵 Sign in with Google"])

        # ── Password tab ──────────────────────────────────────────
        with tab_pw:
            username = st.text_input("Username", placeholder="admin or student1", key="_login_user")
            password = st.text_input("Password", type="password", placeholder="Enter password", key="_login_pass")

            if st.button("Login →", type="primary", use_container_width=True, key="_login_btn"):
                if login_with_password(username, password):
                    st.success(f"Welcome back, {get_display_name()}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password.")

            st.markdown("""
            <div style="margin-top:1rem; font-size:0.78rem; color:#4A5A7A; text-align:center; line-height:1.8;">
                Demo credentials:<br>
                <code>admin</code> / <code>admin123</code> &nbsp;·&nbsp;
                <code>student1</code> / <code>student123</code>
            </div>
            """, unsafe_allow_html=True)

        # ── Google OAuth tab ───────────────────────────────────────
        with tab_google:
            cfg = _google_cfg()
            client_id     = cfg.get("client_id", "")
            client_secret = cfg.get("client_secret", "")
            redirect_uri  = cfg.get("redirect_uri", "http://localhost:8501")

            if not client_id or not client_secret:
                st.info("""
**Google Sign-In is not yet configured.**

To enable it:
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create OAuth 2.0 credentials (Web App)
3. Add `http://localhost:8501` as Redirect URI
4. Paste your Client ID + Secret into `.streamlit/secrets.toml`
""")
            else:
                # Build OAuth URL
                try:
                    from authlib.integrations.requests_client import OAuth2Session
                    import urllib.parse

                    auth_url = (
                        "https://accounts.google.com/o/oauth2/v2/auth?"
                        + urllib.parse.urlencode({
                            "client_id":     client_id,
                            "redirect_uri":  redirect_uri,
                            "response_type": "code",
                            "scope":         "openid email profile",
                            "access_type":   "offline",
                            "prompt":        "select_account",
                        })
                    )

                    # Check if we received a callback code
                    params = st.query_params
                    code   = params.get("code", "")

                    if code:
                        # Exchange code for token
                        import httpx, json as _json
                        resp = httpx.post(
                            "https://oauth2.googleapis.com/token",
                            data={
                                "code":          code,
                                "client_id":     client_id,
                                "client_secret": client_secret,
                                "redirect_uri":  redirect_uri,
                                "grant_type":    "authorization_code",
                            },
                            timeout=10,
                        )
                        token_data = resp.json()
                        id_token   = token_data.get("id_token", "")
                        if id_token:
                            # Decode without verification for display (Google already verified it)
                            import base64
                            payload = id_token.split(".")[1]
                            payload += "=" * (4 - len(payload) % 4)
                            user_info = _json.loads(base64.urlsafe_b64decode(payload))
                            email = user_info.get("email", "")
                            if email:
                                google_oauth_callback(email)
                                st.query_params.clear()
                                st.rerun()
                        else:
                            st.error("Google authentication failed. Please try again.")
                    else:
                        st.link_button("🔵 Sign in with Google", auth_url, use_container_width=True)
                except Exception as e:
                    st.error(f"Google OAuth error: {e}")


def _render_access_denied():
    st.markdown("""
    <div style="text-align:center; padding:4rem 0;">
        <div style="font-size:4rem; margin-bottom:1rem;">🔒</div>
        <div style="font-family:'Syne',sans-serif; font-weight:800; font-size:1.5rem;
                    color:#FF4A6E; margin-bottom:0.5rem;">Access Denied</div>
        <div style="color:#7A90B0; font-size:0.9rem;">
            This page is restricted to <strong style="color:#FFB800;">Admin</strong> users only.
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("← Back to Home", type="primary"):
        st.switch_page("Home.py")


# ── Sidebar Logout Widget ─────────────────────────────────────────────────

def render_auth_sidebar():
    """Call inside `with st.sidebar:` to show user info + logout."""
    if not is_authenticated():
        return
    role  = get_role()
    name  = get_display_name()
    badge = "🛡️ Admin" if role == "admin" else "🎓 Student"
    color = "#FFB800" if role == "admin" else "#00D4FF"

    st.sidebar.markdown(f"""
    <div style="background:rgba(0,0,0,0.3); border:1px solid {color}33;
                border-radius:12px; padding:0.8rem 1rem; margin-bottom:0.8rem;">
        <div style="font-size:0.72rem; color:#4A5A7A; text-transform:uppercase; letter-spacing:1px;">
            Logged in as
        </div>
        <div style="font-weight:700; color:#E2E8F0; font-size:0.9rem; margin-top:0.15rem;">{name}</div>
        <div style="font-size:0.75rem; color:{color}; margin-top:0.2rem;">{badge}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("🚪 Logout", use_container_width=True, key="sidebar_logout_btn"):
        logout()
