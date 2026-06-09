# Financial Agent

Financial Agent is a modular, multi-provider financial assistant designed to help users interact with financial APIs and services through a single, configurable interface. The agent supports multiple backend providers, lets the user select a preferred provider at startup, and automatically falls back to alternative providers if the chosen provider becomes unavailable.
Key features
- Multi-provider architecture: configure and switch between multiple financial service providers.
- Provider selection: choose the preferred provider at startup.
- Automatic fallback: if a provider fails, the agent transparently routes requests to an available provider.
- Memory: a lightweight conversation memory limited to the last 10 messages to reduce API usage and keep costs predictable.
- Extensible: easy to add new providers and integrations.

When to use
- Building chat-based financial assistants that must remain resilient to individual provider outages.
- Prototyping multi-backend integrations while controlling API consumption.

Repository structure
```
financial-agent/
├── providers/                     # Provider adapters (one per service)
├── core/                    # Core agent logic, routing, fallback, memory
├── main.py                
├── pyproject.toml           # Python dependencies (or package.json for JS)
└── README.md                # Project documentation
```

Installation

Prerequisites
- Python 3.9+ (or Node 16+ if implemented in JavaScript)
- Git

Clone the repository

```
git clone <repo-url>
cd financial-agent
```

Python (pip) quickstart

1. Create and activate a virtual environment

```
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
```

2. Install dependencies

```
pip install -r requirements.txt
```

3. Configure providers

Copy an example config from config/ and set API keys and provider-specific options. The agent reads the configured providers at startup and optionally prompts the user to select a preferred provider.

4. Run the agent (development)

```
python -m src.cli.main
```

Memory and cost control

This project intentionally limits conversation memory to the last 10 messages to bound API usage and cost. The memory is stored in an in-memory buffer by default; you can replace it with a persistent store if you need long-term context, but be aware of increased API usage and storage cost.


Contact
For questions or help integrating a new provider, open an issue or submit a pull request.
