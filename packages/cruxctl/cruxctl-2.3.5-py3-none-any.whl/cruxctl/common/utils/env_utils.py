import os
from cruxctl.common.utils.gcp_secrets_manager import get_secret_value


def set_openai_token(console):
    token = os.environ.get("OPENAI_API_KEY", None)
    if not token:
        secret_proj = "crux-data-science"
        secret_key = "OPENAI_API_KEY"
        console.rule("[bold red]Remove before public release", style="red")
        console.print(f"Fetching GCP secret: {secret_proj}/{secret_key}")
        console.rule(style="red")
        token = get_secret_value(secret_proj, secret_key)
        os.environ["OPENAI_API_KEY"] = token
    return token
