# Third-Party Notices

BlueHire depends on third-party software components. This document lists the
known dependencies and their licenses. It is provided for informational
purposes and does not constitute legal advice.

## Dependency Inventory Status

A complete, verified license inventory for all direct and transitive
dependencies has not yet been finalized. The table below lists licenses that
can be verified from package metadata. Additional dependency license review is
pending.

## Backend Dependencies

The backend is a Python application. Its direct dependencies are declared in
`backend/requirements.txt`.

| Package | Version constraint | License (verified from package metadata) |
|---------|-------------------|------------------------------------------|
| fastapi[standard] | >=0.115.0 | MIT |
| sqlalchemy | >=2.0.0 | MIT |
| psycopg2-binary | >=2.9.0 | LGPLv3 (with linking exception) |
| pydantic-settings | >=2.0.0 | MIT |
| python-dotenv | >=1.0.0 | BSD-3-Clause |
| uvicorn | >=0.30.0 | BSD-3-Clause |
| pwdlib[argon2] | >=0.2.1 | BSD-3-Clause |
| python-jose[cryptography] | >=3.3.0 | MIT |
| alembic | >=1.13.1 | MIT |
| email-validator | >=2.1.1 | MIT |
| slowapi | >=0.1.9 | MIT |
| pytest | >=7.0.0 | MIT |
| httpx | >=0.24.0 | MIT |
| ruff | >=0.9.0 | MIT |

Note: `psycopg2-binary` is distributed under the GNU Lesser General Public
License v3 with a linking exception, which permits use in proprietary and
closed-source applications when linked dynamically.

## Frontend Dependencies

The frontend is a Next.js application. Its direct dependencies are declared in
`frontend/package.json`.

### Production Dependencies

| Package | Version constraint | License (verified from package metadata) |
|---------|-------------------|------------------------------------------|
| next | 16.2.6 | MIT |
| react | 19.2.4 | MIT |
| react-dom | 19.2.4 | MIT |
| lucide-react | ^1.16.0 | ISC |
| clsx | ^2.1.1 | MIT |
| tailwind-merge | ^3.6.0 | MIT |
| class-variance-authority | ^0.7.1 | MIT |
| @radix-ui/react-slot | ^1.2.4 | MIT |
| shadcn | ^4.8.0 | MIT |
| tw-animate-css | ^1.4.0 | MIT |
| @base-ui/react | ^1.5.0 | Not independently verified |

### Development Dependencies

| Package | Version constraint | License (verified from package metadata) |
|---------|-------------------|------------------------------------------|
| eslint | ^9 | MIT |
| eslint-config-next | 16.2.6 | MIT |
| typescript | ^5 | Apache-2.0 |
| vitest | ^2.1.8 | MIT |
| @testing-library/jest-dom | ^6.6.3 | MIT |
| @testing-library/react | ^16.1.0 | MIT |
| happy-dom | ^15.0.0 | MIT |
| @vitejs/plugin-react | ^4.3.4 | MIT |
| @tailwindcss/postcss | ^4 | MIT |
| tailwindcss | ^4 | MIT |

## License Verification Process

To verify the license of any dependency:

1. Backend: Inspect the package metadata via `pip show <package-name>` or
   review the `LICENSE` file within the installed package directory.
2. Frontend: Inspect the package metadata via `npm view <package-name>
   license` or review the `LICENSE` file within `node_modules/<package-name>/`.

## Pending Items

- A complete transitive dependency license inventory has not been completed.
- Some package licenses (e.g., `@base-ui/react`) could not be independently
  verified from package metadata at the time of writing.
- This document will be updated as dependency license review progresses.

## How to Report a Licensing Concern

If you believe a dependency's license is incorrectly listed, or if you are
aware of a licensing obligation that is not reflected here, please open an
Issue on the GitHub repository with details.
