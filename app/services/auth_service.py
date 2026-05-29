from supabase import Client, create_client


def create_auth_client(url: str, key: str) -> Client:
    return create_client(url, key)


def sign_in_with_password(url: str, key: str, email: str, password: str) -> dict:
    client = create_auth_client(url, key)
    response = client.auth.sign_in_with_password({"email": email, "password": password})
    if not response.session or not response.user:
        raise ValueError("Login failed.")
    return {
        "access_token": response.session.access_token,
        "refresh_token": response.session.refresh_token,
        "user_id": response.user.id,
        "email": response.user.email,
    }


def sign_up_with_password(url: str, key: str, email: str, password: str) -> dict:
    client = create_auth_client(url, key)
    response = client.auth.sign_up({"email": email, "password": password})
    if not response.user:
        raise ValueError("Sign-up failed.")
    return {
        "user_id": response.user.id,
        "email": response.user.email,
    }
