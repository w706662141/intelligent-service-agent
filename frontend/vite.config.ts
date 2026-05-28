import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      "/token": "http://localhost:8000",
      "/chat": "http://localhost:8000",
      "/session": "http://localhost:8000",
      "/auth": "http://localhost:8000",
      "/admin": "http://localhost:8000",
    },
  },
});
