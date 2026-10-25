# BuzzKill web frontend

The React/Vite frontend connects to the local Python classifier service in
`../slm/local_api.py`. Classification, high-priority keywords, and correction
feedback use that service; no browser local storage or cloud API is used.

## Run

Install the Python requirements from the project root:

```sh
python -m pip install -r slm/requirements.txt
```

Open two terminals from the project root. Start the SLM service in the first:

```sh
python slm/local_api.py
```

Start Vite in the second:

```sh
cd frontend
npm install
npm run dev
```

Open the Vite URL printed in the terminal. Vite proxies `/api` to
`127.0.0.1:8765`; the Python service binds to loopback only. The SLM loads the
existing category and importance `.joblib` models and `user_preferences.json`.

Run frontend checks with `npm test` and `npm run build`.
