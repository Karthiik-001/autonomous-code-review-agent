# Frontend

This directory contains the React, TypeScript, and Vite user interface for the
first milestone.

## Current behavior

- Paste Python source or choose one `.py` file.
- Show a friendly warning for empty, unsupported, or larger-than-50 KB input.
- Send valid requests to the local FastAPI `POST /api/reviews` route.
- Display loading, backend-error, network-error, and success states.
- Display deterministic backend findings labelled **Mock/demo mode**.

The Vite development server proxies `/api` requests to
`http://127.0.0.1:8000`. The frontend does not call a real AI provider. It does
not execute, import, compile, or send submitted Python code to a shell.

## Local commands

After dependencies are installed:

```text
npm run dev
npm run build
npm test
```

Start the backend separately from the repository root:

```text
cd backend
.venv\Scripts\activate
python -m uvicorn app.main:app --reload
```

Then start the frontend from another terminal:

```text
cd frontend
npm run dev
```

The project uses plain CSS and does not include a UI framework.
