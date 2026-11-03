# BlueHire showcase MVP

BlueHire is a four-screen marketplace showcase for blue-collar workers and employers.

## Showcase screens

- **Home** introduces the BlueHire marketplace.
- **Jobs** lets users browse demo listings with search and filters.
- **Job details** shows a listing and a demo **Apply** interaction.
- **Employer job posting** lets employers create a job listing.

## Demo behavior

Job listings use static demo data because the backend API timed out during the MVP work. Jobs created through the employer posting screen are saved in the browser's local storage, so they are available in that browser and are not sent to a server. **Apply** is a demo interaction and does not submit a real application.

## Tech stack

- **Frontend:** Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS 4, and shadcn/ui components.
- **Backend in the repository:** FastAPI, SQLAlchemy, and PostgreSQL. The showcase does not require the backend to run.

## Run the showcase locally

Prerequisites: Node.js compatible with Next.js 16 and npm.

From the repository root:

```bash
cd frontend
npm ci
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). No backend setup is needed for the showcase. The optional `NEXT_PUBLIC_API_URL` setting in `frontend/.env.example` is for API-connected development; the showcase listings use static demo data.

## Frontend checks

Run these from `frontend/`:

```bash
npm run lint
npx tsc --noEmit
npm run build
```

## Repository layout

```text
bluehire/
├── frontend/  # Next.js showcase
└── backend/   # FastAPI service and database integration
```
