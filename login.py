import streamlit as st
from datetime import datetime
import base64
import time
from streamlit.components.v1 import html

def play_sound(file):
    with open(file, "rb") as f:
        sound = base64.b64encode(f.read()).decode()

    html(f"""
    <audio autoplay>
        <source src="data:audio/mp3;base64,{sound}" type="audio/mp3">
    </audio>
    """, height=0)

def verify_passkey(cred_id):
    """Simple verification: Check if the credential ID matches the registered one."""
    registered_cred = st.session_state.get('registered_passkey_cred', None)
    return registered_cred == cred_id and cred_id is not None

def login_page():
    st.markdown("""
    <style>
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}

    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, 
            #0a0e17 0%, 
            #121828 25%, 
            #0f172a 50%, 
            #0a0e17 100%);
        min-height: 100vh;
    }

    /* Center everything */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Futuristic scan lines overlay */
    .scanlines {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            transparent 50%,
            rgba(0, 150, 255, 0.03) 50%
        );
        background-size: 100% 4px;
        pointer-events: none;
        z-index: 1;
        opacity: 0.4;
    }

    /* Main login container */
    .login-container {
        position: relative;
        background: rgba(10, 14, 23, 0.85);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 150, 255, 0.2);
        border-radius: 16px;
        padding: 40px;
        width: 420px;
        margin: 0 auto;
        box-shadow: 
            0 0 60px rgba(0, 100, 255, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        z-index: 2;
        margin-bottom: 30px;  /* Added spacing between login card and logo card */
    }

    /* Glowing border effect */
    .login-container::before {
        content: '';
        position: absolute;
        top: -1px;
        left: -1px;
        right: -1px;
        bottom: -1px;
        background: linear-gradient(45deg, 
            #0066ff, 
            #00ccff, 
            #0066ff);
        border-radius: 17px;
        z-index: -1;
        opacity: 0.3;
        filter: blur(8px);
    }

    /* Header styles */
    .system-header {
        text-align: center;
        margin-bottom: 30px;
        position: relative;
    }

    .system-title {
        background: linear-gradient(90deg, 
            #00ccff 0%, 
            #0066ff 50%, 
            #00ccff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 22px;
        font-weight: 700;
        letter-spacing: 1px;
        margin-bottom: 8px;
        font-family: 'Arial', sans-serif;
    }

    .system-subtitle {
        color: #8892b0;
        font-size: 12px;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 20px;
    }

    /* Logo container */
    .logo-container {
        width: 80px;
        height: 80px;
        margin: 0 auto 20px;
        background: linear-gradient(135deg, 
            rgba(0, 102, 255, 0.1) 0%, 
            rgba(0, 204, 255, 0.1) 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid rgba(0, 150, 255, 0.3);
        box-shadow: 0 0 30px rgba(0, 150, 255, 0.2);
    }

    .logo-container img {
        width: 50px;
        height: 50px;
        filter: drop-shadow(0 0 10px rgba(0, 150, 255, 0.5));
    }

    /* Status indicator */
    .status-indicator {
        position: relative;
        display: inline-block;
        width: 8px;
        height: 8px;
        background: #00ff88;
        border-radius: 50%;
        margin-right: 8px;
        box-shadow: 0 0 10px #00ff88;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(0, 255, 136, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(0, 255, 136, 0); }
        100% { box-shadow: 0 0 0 0 rgba(0, 255, 136, 0); }
    }

    /* Input fields */
    .stTextInput > div > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(0, 150, 255, 0.3) !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }

    .stTextInput > div > div:hover {
        border-color: rgba(0, 200, 255, 0.5) !important;
        background: rgba(255, 255, 255, 0.08) !important;
    }

    .stTextInput > div > div:focus-within {
        border-color: #00ccff !important;
        box-shadow: 0 0 15px rgba(0, 200, 255, 0.3) !important;
        background: rgba(255, 255, 255, 0.1) !important;
    }

    .stTextInput input {
        color: #ffffff !important;
        font-size: 14px !important;
        padding: 14px !important;
        background: transparent !important;
    }

    .stTextInput input::placeholder {
        color: rgba(255, 255, 255, 0.5) !important;
    }

    /* Labels */
    .input-label {
        color: #8892b0;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 6px;
        display: block;
    }

    /* Button styling */
    .stButton > button {
        width: 100% !important;
        background: linear-gradient(90deg, 
            #0066ff 0%, 
            #00ccff 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 16px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        margin-top: 10px !important;
        transition: all 0.3s ease !important;
        position: relative !important;
        overflow: hidden !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 25px rgba(0, 150, 255, 0.4) !important;
    }

    /* Time display */
    .time-display {
        background: rgba(0, 102, 255, 0.1);
        border: 1px solid rgba(0, 150, 255, 0.2);
        border-radius: 6px;
        padding: 10px 15px;
        margin: 20px 0;
        text-align: center;
    }

    .time-text {
        color: #00ccff;
        font-family: 'Courier New', monospace;
        font-size: 13px;
        letter-spacing: 1px;
    }

    /* Security badge */
    .security-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: linear-gradient(90deg, 
            rgba(255, 77, 77, 0.1), 
            rgba(255, 77, 77, 0.2));
        border: 1px solid rgba(255, 77, 77, 0.3);
        color: #ff4d4d;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 15px 0;
    }

    /* Footer */
    .footer {
        text-align: center;
        margin-top: 0px !important;
        padding-top: 20px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        color: #8892b0;
        font-size: 11px;
        letter-spacing: 1px;
    }

    /* Warning message */
    .warning {
        background: rgba(255, 77, 77, 0.1);
        border: 1px solid rgba(255, 77, 77, 0.3);
        border-radius: 8px;
        padding: 12px;
        margin-top: 15px;
    }

    .warning-text {
        color: #ff4d4d;
        font-size: 12px;
        text-align: center;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }

    /* Success message */
    .success {
        background: rgba(0, 255, 136, 0.1);
        border: 1px solid rgba(0, 255, 136, 0.3);
        border-radius: 8px;
        padding: 12px;
        margin-top: 15px;
    }

    .success-text {
        color: #00ff88;
        font-size: 12px;
        text-align: center;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }

    /* Form container */
    .form-container {
        margin-top: 20px;
    }

    </style>

    <!-- Scanlines overlay -->
    <div class="scanlines"></div>
    """, unsafe_allow_html=True)

    # Create the main container with columns for centering
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Load logo - try different methods
        logo_html = ""
        logo_paths = ["logo.png", "Logo.png", "LOGO.png", "./logo.png"]

        for path in logo_paths:
            try:
                with open(path, "rb") as f:
                    logo_data = base64.b64encode(f.read()).decode()
                logo_html = f'<img src="data:image/png;base64,{logo_data}" alt="CSMS Logo">'
                break
            except:
                continue

        if not logo_html:
            # Fallback if no logo found
            logo_html = '<div style="color: #00ccff; font-size: 32px;">🚀</div>'

        st.markdown(f"""
        <div class="login-container">
          <div class="system-header">
            <div class="logo-container">
              {logo_html}
            </div>
            <div class="system-title">CRITICAL SPACE MONITORING SYSTEM</div>
            <div class="system-subtitle">CSMS v2.1.7</div>
          </div>

          <div class="time-display">
            <div class="time-text">🕒 {datetime.utcnow().strftime("%Y-%m-%d | %H:%M:%S")} UTC</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Passkey registration button
        if st.button("Register Passkey (Fingerprint)", use_container_width=True):
            html("""
            <script>
            async function registerPasskey() {
              if (!window.PublicKeyCredential) {
                alert("Passkeys not supported in this browser!");
                return;
              }
              try {
                const challenge = new Uint8Array(32);  // Random challenge (generate securely in production)
                const credential = await navigator.credentials.create({
                  publicKey: {
                    challenge: challenge,
                    rp: { name: "CSMS", id: window.location.hostname },
                    user: {
                      id: new Uint8Array(16),  // Unique user ID (generate per user)
                      name: "admin",
                      displayName: "Admin User"
                    },
                    pubKeyCredParams: [{ alg: -7, type: "public-key" }],  // ES256 algorithm
                    authenticatorSelection: {
                      authenticatorAttachment: "platform",  // Prefer built-in (fingerprint)
                      userVerification: "required"  // Require biometric verification
                    },
                    timeout: 60000
                  }
                });
                // Store credential ID in sessionStorage (simulate backend storage)
                const credentialId = btoa(String.fromCharCode(...new Uint8Array(credential.rawId)));
                sessionStorage.setItem('passkey_credential_id', credentialId);
                alert("✅ Passkey Registered! You can now sign in with fingerprint.");
              } catch (err) {
                alert("❌ Registration Failed: " + err.message);
              }
            }
            registerPasskey();
            </script>
            """)

        # Login form
        USER = "admin"
        PASS = "CSMS@2024"
        params = st.query_params or {}

        cred = params.get("auth", None)

        if cred:
            if verify_passkey(cred):
                st.session_state.logged_in = True
                st.session_state.username = "admin"
                st.query_params.clear()
                st.rerun()
            else:
                st.error("❌ Fingerprint matched but device unauthorized!")

        with st.form("login_form", clear_on_submit=False):
            # Create a container for the form
            form_container = st.container()

            with form_container:
                # USER IDENTIFICATION
                st.markdown('<div class="input-label">USER IDENTIFICATION</div>', unsafe_allow_html=True)
                username = st.text_input(
                    label="Username",
                    placeholder="ENTER USERNAME",
                    label_visibility="collapsed",
                    key="username_input"
                )

                # SECURITY PASSPHRASE
                st.markdown('<div class="input-label">SECURITY PASSPHRASE</div>', unsafe_allow_html=True)
                password = st.text_input(
                    label="Password",
                    type="password",
                    placeholder="ENTER ENCRYPTED KEY",
                    label_visibility="collapsed",
                    key="password_input"
                )

                # Submit button
                submitted = st.form_submit_button("⚡ INITIATE SYSTEM ACCESS", use_container_width=True)

        # Fingerprint button - NO SPACING BEFORE IT
        html("""
        <div style="text-align:center; margin:0; padding:0;">
          <button onclick="authenticate()" style="
            background: linear-gradient(90deg,#00ccff,#0066ff);
            border:none;
            border-radius:10px;
            padding:14px 20px;
            color:white;
            font-size:14px;
            cursor:pointer;
            width:100%;
            margin:0 0 0 0;
          ">
            🆔 Authenticate with Fingerprint
          </button>
        </div>

        <script>
        async function authenticate() {
          if (!window.PublicKeyCredential) {
            alert("Fingerprint not supported in this browser!");
            return;
          }
          const storedCredentialId = sessionStorage.getItem('passkey_credential_id');
          if (!storedCredentialId) {
            alert("No passkey registered. Please register first.");
            return;
          }
          try {
            const challenge = new Uint8Array(32);  // Same challenge as registration
            const credential = await navigator.credentials.get({
              publicKey: {
                challenge: challenge,
                allowCredentials: [{
                  id: Uint8Array.from(atob(storedCredentialId), c => c.charCodeAt(0)),
                  type: 'public-key'
                }],
                timeout: 60000,
                userVerification: "required"  // Require biometric verification
              }
            });
            alert("✅ Fingerprint Verified!");
            // Trigger login by reloading with a query param
            window.location.href = window.location.href.split('?')[0] + '?fingerprint_auth=1';
          } catch (err) {
            alert("❌ Authentication Failed: " + err.message);
          }
        }
        </script>
        """)

        # Handle login submission
        if submitted:
            if username == USER and password == PASS:
                play_sound("success.mp3")  # 🔊 SOUND PLAY HERE

