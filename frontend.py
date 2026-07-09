import streamlit as st
import requests
import base64
import urllib.parse
import os
from dotenv import load_dotenv

load_dotenv()


def _get_config(key: str, default: str = "") -> str:
    """Read config from st.secrets (Streamlit Cloud) then fall back to env / .env."""
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError):
        return os.getenv(key, default)


API_URL = _get_config("API_URL", "http://localhost:8000").rstrip("/")

REQUEST_TIMEOUT = 15  # seconds

st.set_page_config(page_title="Simple Social", layout="wide")

if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None


def get_headers() -> dict:
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}


def _api_request(method: str, path: str, **kwargs):
    """
    Thin wrapper around requests that applies a timeout and converts
    connection / timeout errors into a (None, error_message) tuple so
    callers never crash on network failures.

    Returns (response, None) on success, (None, error_str) on failure.
    """
    kwargs.setdefault("timeout", REQUEST_TIMEOUT)
    url = f"{API_URL}{path}"
    try:
        resp = getattr(requests, method)(url, **kwargs)
        return resp, None
    except requests.exceptions.ConnectionError:
        return None, f"Cannot reach the server at {API_URL}. Check that the backend is running and API_URL is correct."
    except requests.exceptions.Timeout:
        return None, "Request timed out. The server took too long to respond."
    except requests.exceptions.RequestException as exc:
        return None, f"Network error: {exc}"


def login_page():
    st.title("Welcome to Simple Social")

    email = st.text_input("Email:")
    password = st.text_input("Password:", type="password")

    if email and password:
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Login", type="primary", use_container_width=True):
                resp, err = _api_request(
                    "post",
                    "/auth/jwt/login",
                    data={"username": email, "password": password},
                )
                if err:
                    st.error(err)
                    return
                if resp.status_code == 200:
                    st.session_state.token = resp.json()["access_token"]
                    user_resp, user_err = _api_request("get", "/users/me", headers=get_headers())
                    if user_err:
                        st.error(user_err)
                        return
                    if user_resp.status_code == 200:
                        st.session_state.user = user_resp.json()
                        st.rerun()
                    else:
                        st.error("Logged in but failed to fetch user info.")
                else:
                    st.error("Invalid email or password.")

        with col2:
            if st.button("Sign Up", type="secondary", use_container_width=True):
                resp, err = _api_request(
                    "post",
                    "/auth/register",
                    json={"email": email, "password": password},
                )
                if err:
                    st.error(err)
                    return
                if resp.status_code == 201:
                    st.success("Account created! Click Login now.")
                else:
                    try:
                        detail = resp.json().get("detail", "Registration failed")
                    except Exception:
                        detail = "Registration failed"
                    st.error(f"Registration failed: {detail}")
    else:
        st.info("Enter your email and password above.")


def upload_page():
    st.title("Share Something")

    uploaded_file = st.file_uploader(
        "Choose media",
        type=["png", "jpg", "jpeg", "mp4", "avi", "mov", "mkv", "webm"],
    )
    caption = st.text_area("Caption:", placeholder="What's on your mind?")

    if uploaded_file and st.button("Share", type="primary"):
        with st.spinner("Uploading..."):
            resp, err = _api_request(
                "post",
                "/upload",
                files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
                data={"caption": caption},
                headers=get_headers(),
                timeout=60,  # uploads can take longer
            )
            if err:
                st.error(err)
                return
            if resp.status_code == 200:
                st.success("Posted!")
                st.rerun()
            else:
                try:
                    detail = resp.json().get("detail", "Upload failed")
                except Exception:
                    detail = resp.text or "Upload failed"
                st.error(f"Upload failed: {detail}")


def encode_text_for_overlay(text: str) -> str:
    if not text:
        return ""
    base64_text = base64.b64encode(text.encode("utf-8")).decode("utf-8")
    return urllib.parse.quote(base64_text)


def create_transformed_url(original_url: str, transformation_params: str, caption: str = "") -> str:
    if caption:
        encoded_caption = encode_text_for_overlay(caption)
        transformation_params = f"l-text,ie-{encoded_caption},ly-N20,lx-20,fs-50,co-white,bg-000000A0,l-end"

    if not transformation_params:
        return original_url

    parts = original_url.split("/")
    base_url = "/".join(parts[:4])
    file_path = "/".join(parts[4:])
    return f"{base_url}/tr:{transformation_params}/{file_path}"


def feed_page():
    st.title("Feed")

    resp, err = _api_request("get", "/feed", headers=get_headers())
    if err:
        st.error(err)
        return

    if resp.status_code != 200:
        st.error("Failed to load feed.")
        return

    posts = resp.json().get("posts", [])
    if not posts:
        st.info("No posts yet! Be the first to share something.")
        return

    for post in posts:
        st.markdown("---")

        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{post['email']}** • {post['created_at'][:10]}")
        with col2:
            if post.get("is_owner", False):
                if st.button("Delete", key=f"delete_{post['id']}", help="Delete post"):
                    del_resp, del_err = _api_request(
                        "delete",
                        f"/post/{post['id']}",
                        headers=get_headers(),
                    )
                    if del_err:
                        st.error(del_err)
                    elif del_resp.status_code == 200:
                        st.success("Post deleted!")
                        st.rerun()
                    else:
                        try:
                            detail = del_resp.json().get("detail", "Delete failed")
                        except Exception:
                            detail = "Delete failed"
                        st.error(f"Failed to delete post: {detail}")

        caption = post.get("caption", "")
        if post["file_type"] == "image":
            uniform_url = create_transformed_url(post["url"], "", caption)
            st.image(uniform_url, width=300)
        else:
            uniform_video_url = create_transformed_url(
                post["url"], "w-400,h-200,cm-pad_resize,bg-blurred"
            )
            st.video(uniform_video_url, width=300)
            if caption:
                st.caption(caption)

        st.markdown("")


# -------------------- Main --------------------
if st.session_state.user is None:
    login_page()
else:
    st.sidebar.title(f"Hi {st.session_state.user['email']}!")

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.token = None
        st.rerun()

    st.sidebar.markdown("---")
    page = st.sidebar.radio("Navigate:", ["Feed", "Upload"])

    if page == "Feed":
        feed_page()
    else:
        upload_page()
