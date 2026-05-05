# envchain

> Manage and chain environment variable profiles across projects with support for secret injection from local vaults.

---

## Installation

```bash
pip install envchain
```

Or with [pipx](https://pypa.github.io/pipx/) for isolated installs:

```bash
pipx install envchain
```

---

## Usage

Define a profile in `envchain.toml`:

```toml
[profiles.dev]
DATABASE_URL = "postgres://localhost/mydb"
DEBUG = "true"

[profiles.dev.secrets]
API_KEY = { vault = "~/.local/share/envchain/vault", key = "my_api_key" }
```

Activate a profile and run a command:

```bash
envchain run --profile dev python app.py
```

Chain multiple profiles together:

```bash
envchain run --profile base --profile dev python app.py
```

Export variables to your current shell session:

```bash
eval "$(envchain export --profile dev)"
```

List all available profiles:

```bash
envchain list
```

---

## How It Works

`envchain` reads layered profiles from a `envchain.toml` file, merges them in order, injects secrets from a local encrypted vault, and exposes the resulting environment to any subprocess — without ever writing secrets to disk in plain text.

---

## License

MIT © [envchain contributors](https://github.com/yourname/envchain)