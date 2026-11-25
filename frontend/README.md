# Frontend

# Frontend

The React/Vite dashboard displays the catalog and creates simulated checkout orders through the API gateway.

## Run locally

```sh
npm install
npm run dev
```

The Vite development server proxies `/api` to `http://localhost:8000`.

## Container build

The production image is built with Node 22 and served by Nginx on port 8080.
