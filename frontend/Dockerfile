FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# ---- Etapa de test: reutiliza build (mismas dependencias, mismo código) ----
# npm ci de arriba ya instaló vitest y @vitest/coverage-v8: son devDependencies
# del package.json, y "npm ci" (sin --omit=dev) las instala igual que las otras.
FROM build AS test
ENTRYPOINT ["npx", "vitest", "run", "--coverage", "--coverage.reportsDirectory=/out/coverage"]

FROM nginx:1.27-alpine
COPY default.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html
ENV BACKEND_URL=http://backend:8080 \
    DNS_RESOLVER=127.0.0.11
EXPOSE 80
HEALTHCHECK --interval=10s --timeout=3s --retries=5 CMD wget -q -O /dev/null http://127.0.0.1/ || exit 1

