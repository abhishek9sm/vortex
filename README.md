# BuzzKill projects

The repository contains a connected local web demo and a separate Android
notification app:

- `frontend/`: React/Vite interface.
- `slm/`: Python/scikit-learn classifier, API bridge, model files, and training
  scripts.
- `android-backend/`: independent Kotlin/Android implementation with native
  notification access and Room storage.

## Run the connected web demo

The web frontend uses the Python SLM service for classification, keyword-rule
storage, and feedback persistence. Run both processes from the project root in
separate terminals:

```sh
python -m pip install -r slm/requirements.txt
python slm/local_api.py
```

In the second terminal:

```sh
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite. It proxies API requests to a Python server
bound only to `127.0.0.1`; notification content is not sent to a cloud service.
Feedback is stored in `slm/feedback.csv`, and high-priority keyword rules are
stored in `slm/user_preferences.json`.

## Android app

`android-backend/` is a separate Android application. It uses Android's
notification-listener permission and its own Room database and classifier
interface. It is not connected to the web demo; the web process cannot access
Android notifications, and the Android app does not make requests to the local
Python server. This separation preserves the local-only Android pipeline.

See `frontend/README.md` for web development details and
`android-backend/README.md` for Android setup and notification-access steps.
