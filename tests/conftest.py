#importing the tools package runs every @registry.register decorator,
#so the real tools exist in the registry for all tests.
import solana_ai.tools #noqa: F401