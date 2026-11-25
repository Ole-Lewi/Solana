from datetime import datetime
from solana_ai.registry import Risk, registry

@registry.register(risk=Risk.AUTO)
def get_time() -> str:
    """Return the current local date and time on the user's laptop."""
    return datetime.now().isoformat(timespec="seconds")