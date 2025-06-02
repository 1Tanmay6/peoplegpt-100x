**Project Title: 100X Full-Stack Application**

A comprehensive full-stack project split into two main folders:

* **`100x_backend`**: Python-based REST API using Uvicorn (ASGI server).
* **`100x_frontend/pplgpt`**: React + Shadcn + Tailwind + TypeScript front-end application.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Tech Stack](#tech-stack)
3. [Folder Structure](#folder-structure)
4. [Environment Variables](#environment-variables)
5. [Backend (`100x_backend`)](#backend-100x_backend)

   1. [Prerequisites](#backend-prerequisites)
   2. [Installation & Setup](#backend-installation--setup)
   3. [Running the Server](#backend-running-the-server)
   4. [Available Endpoints](#backend-available-endpoints)
   5. [Testing](#backend-testing)
6. [Frontend (`100x_frontend/pplgpt`)](#frontend-100x_frontendpplgpt)

   1. [Prerequisites](#frontend-prerequisites)
   2. [Installation & Setup](#frontend-installation--setup)
   3. [Running the Dev Server](#frontend-running-the-dev-server)
   4. [Building for Production](#frontend-building-for-production)
   5. [Folder Structure & Key Files](#frontend-folder-structure--key-files)
7. [Development Workflow](#development-workflow)
8. [Contributing](#contributing)
9. [License](#license)

---

## Project Overview

This repository houses a full-stack application divided into:

* **Backend** (`100x_backend`):

  * Built with **Python 3.x**, using a lightweight ASGI framework (FastAPI or similar) served by **Uvicorn**.
  * Exposes RESTful endpoints for data processing, authentication, and business logic.

* **Frontend** (`100x_frontend/pplgpt`):

  * A **React** application bootstrapped with **TypeScript**, styled using **Tailwind CSS** and **Shadcn UI** components.
  * Fetches data from the backend, renders dynamic UI, and provides an interactive user experience.

Both parts live in the same repository but maintain separate environment configurations, dependencies, and start scripts.

---

## Tech Stack

* **Backend**

  * Language: Python 3.9+
  * Framework: FastAPI (or equivalent ASGI framework)
  * Server: Uvicorn (ASGI server)
  * Dependency Management: `venv` or `virtualenv`, `uv`
  * Environment Variables: `.env`

* **Frontend**

  * Language: TypeScript
  * Framework: React 18+
  * Styling: Tailwind CSS v3.x, Shadcn UI components
  * Bundler/Toolchain: Vite (recommended) or Create React App (with TypeScript template)
  * Package Manager: `npm` or `yarn`
  * Environment Variables: `.env`

---

## Folder Structure

```
/
├── 100x_backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/
│   │   │   └── ...
│   │   ├── models/
│   │   │   └── ...
│   │   ├── services/
│   │   │   └── ...
│   │   └── utils/
│   ├── requirements.txt
│   ├── .env
│   └── README.md  ← (this README describes both sides)
│
└── 100x_frontend/
    └── pplgpt/
        ├── public/
        │   └── index.html
        ├── src/
        │   ├── components/
        │   │   └── UI components (Shadcn-based)
        │   ├── pages/
        │   │   └── ...
        │   ├── styles/
        │   │   └── tailwind.css
        │   ├── App.tsx
        │   ├── index.tsx
        │   └── vite.config.ts  (or react-scripts config)
        ├── package.json
        ├── tsconfig.json
        ├── tailwind.config.js
        ├── postcss.config.js
        ├── .env
        └── README.md  ← (can contain front-end–specific info, but master README also covers it)
```

---

## Backend (`100x_backend`)

### Backend Prerequisites

* Python 3.9 or newer
* `uv` by Astral
* (Optional) PostgreSQL or your database of choice running locally
* `virtualenv` or built-in `venv`

### Installation & Setup

1. **Clone the repository** (if not already done):

   ```bash
   git clone https://github.com/your-org/100x-fullstack.git
   cd 100x_backend
   ```

2. **Create and activate a virtual environment**

   ```bash
   uv sync
   source .venv/bin/activate      # macOS/Linux
   .venv\Scripts\activate         # Windows (PowerShell)
   ```

3. **Install dependencies**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Copy and configure environment variables**

   ```bash
   cp .env_backend.example .env_backend
   # Open .env_backend in your editor and fill in the values
   ```

5. **Database Migrations (if applicable)**
   If you are using an ORM (e.g., SQLModel, SQLAlchemy, Tortoise ORM) you might need to run migrations:

   ```bash
   # Example with Alembic (if you’ve set it up)
   alembic upgrade head
   ```

   Adjust this step to your chosen migration tool.

### Running the Server

> The backend exposes a set of RESTful endpoints, served via Uvicorn as an ASGI server.

1. **Activate your virtual environment** (if not already active):

   ```bash
   source .venv/bin/activate   # macOS/Linux
   .venv\Scripts\activate      # Windows
   ```

2. **Ensure `.env` is correctly configured.**

3. **Start Uvicorn**

   ```bash
   # From within the 100x_backend directory
   uvicorn app.main:app \
     --reload \           # for hot-reload in development
     --host ${HOST:-0.0.0.0} \
     --port ${PORT:-8000}
   ```

   * **`app.main:app`** assumes your FastAPI (or ASGI) instance is named `app` in `app/main.py`.
   * Adjust `--host` and `--port` according to your `.env_backend` values or command-line overrides.

4. **Open your browser** to [http://localhost:8000](http://localhost:8000) (or your chosen host/port).

   * Using FastAPI, the Swagger UI docs will be available at `/docs` and the Redoc docs at `/redoc`.

### Available Endpoints

Below is a sample list of endpoints (adjust to your implementation):


* **Data Resource**

  * `GET /get-history`
  * `POST /upload_and_run`
  * `GET /hits`

> ⚠️ **Note:** Update this list to match your actual routers in `app/routers/`.

### Testing

If you’ve included tests (e.g., with `pytest`), you can run them as follows:

```bash
# from 100x_backend root (and with venv activated)
uv sync  # if you have dev dependencies
pytest --cov=app tests/
```

Adjust paths according to where your `tests/` folder resides.

---

## Frontend (`100x_frontend/pplgpt`)

### Frontend Prerequisites

* Node.js (≥ 16.x)
* npm (≥ 8.x) or Yarn (≥ 1.22.x)
* Git (for cloning/updating)

### Installation & Setup

1. **Navigate to the Frontend Directory**

   ```bash
   cd 100x_frontend/pplgpt
   ```

2. **Install Dependencies**
   Using npm:

   ```bash
   npm install
   ```

   Or using Yarn:

   ```bash
   yarn install
   ```

3. **Copy and configure environment variables**

   ```bash
   cp example.env .env
   # Edit example.env to set VITE_API_BASE_URL, etc.
   ```

4. **Tailwind CSS Configuration**

   * `tailwind.config.js` and `postcss.config.js` should already be present.
   * If starting from scratch, run:

     ```bash
     npx tailwindcss init -p
     ```
   * Ensure `tailwind.config.js` includes the correct `content` paths (e.g., `./src/**/*.{js,ts,jsx,tsx}`).

5. **Shadcn UI Setup**

   * If you used the Shadcn CLI, you should already have a `components/` folder containing reusable UI primitives.
   * Ensure you’ve imported the Shadcn CSS into your global `index.css` (usually via `@import "tailwindcss/base";`, etc.).

### Running the Dev Server

```bash
npm run dev
# or
yarn dev
```

* By default, Vite will spin up a local server at [http://localhost:5173](http://localhost:5173) (or the port shown in your terminal).
* The React app will proxy or fetch from `VITE_API_BASE_URL` as defined in your `.env_frontend`.

### Building for Production

```bash
npm run build
# or
yarn build
```

* This produces an optimized production build under `dist/`.
* You can then serve the `dist/` folder using any static-file server (e.g., `serve`, Nginx, or in a container).

### Folder Structure & Key Files

```
pplgpt/
├── public/
│   └── index.html          # HTML template
├── src/
│   ├── components/..       # Shadcn-based UI components (e.g., Button, Card)
│   ├── pages/..            # Page-level components or routes
│   ├── styles/
│   │   └── tailwind.css    # Tailwind base imports
│   ├── App.tsx             # Root React component
│   ├── index.tsx           # React entry point
│   ├── vite-env.d.ts       # TypeScript declarations
│   └── vite.config.ts      # Vite configuration
├── package.json
├── tsconfig.json
├── tailwind.config.js
├── postcss.config.js
├── .env_frontend
└── README.md               # (Optional) Frontend-specific docs
```

* **`src/components/`**:
  Reusable UI primitives generated by the Shadcn CLI (e.g., Accordions, Buttons, etc.). They are pre-styled with Tailwind classes.

* **`src/pages/`**:
  Route-based or view-based components (e.g., `Home.tsx`, `Dashboard.tsx`, `Settings.tsx`).

* **`tailwind.config.js`**:
  Controls Tailwind’s purge paths, theme extensions, and plugins. Make sure the `content` array correctly targets all `tsx`/`jsx`/`js` files.

---

## Development Workflow

1. **Backend Development**

   * Create feature branches (e.g., `feature/add-new-endpoint`).
   * Write or modify routers inside `app/routers/`.
   * Update models or schemas in `app/models/`.
   * Use FastAPI’s interactive docs (`/docs`) to debug/request endpoints.
   * Write tests under `tests/` and ensure coverage remains high.

2. **Frontend Development**

   * Create feature branches (e.g., `feature/ux-improvement`).
   * Add or refine Shadcn components inside `src/components/`.
   * Create new pages in `src/pages/` and add corresponding routes (if using a router).
   * Use Vite’s HMR (Hot Module Replacement) to see UI changes in real-time.
   * Follow TypeScript best practices: define proper interfaces/props for each component.
   * Write unit tests (e.g., with React Testing Library + Jest) in `src/__tests__/` if desired.

3. **Coordinating Backend & Frontend**

   * Make sure the frontend’s `VITE_API_BASE_URL` correctly points to your local or deployed backend.
   * When deploying, consider setting up a reverse proxy (e.g., Nginx) that serves the React static files and proxies API calls to Uvicorn.
   * For CORS, configure your backend to allow requests from your frontend domain during both dev and production.

---

## Contributing

We welcome contributions! To propose changes:

1. **Fork** this repository.
2. **Create a branch** (`git checkout -b feature/your-feature-name`).
3. **Make your changes**, adhering to the project’s coding style:

   * **Backend**: PEP8, type hints, and docstrings (if using FastAPI, add OpenAPI docstrings).
   * **Frontend**: Tailwind classes for styling, Shadcn primitives, and TypeScript typings.
4. **Add tests** (where applicable) and ensure all existing tests still pass.
5. **Commit your changes** (`git commit -m "feat: add new endpoint for XYZ"`).
6. **Push to your fork** (`git push origin feature/your-feature-name`).
7. **Open a Pull Request** against `main` in the original repo. Describe your changes in detail.

Please ensure your code passes linting and formatting checks before opening a PR. Use `flake8` or `black` for Python and `eslint`/`prettier` for the frontend.

---

## License

This project is released under the **MIT License**. See [LICENSE](LICENSE) for details.
