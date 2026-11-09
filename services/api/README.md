# Maze Guardians Content API (optional)

Java 21 / Spring Boot read-only API that serves the same JSON contract as the static site
(`apps/web/src/content/*.json` is packaged into the jar at build time). **The public website does not need
or call it**; it exists so a future app, CMS or partner feed can reuse the content.

```bash
cd services/api
mvn spring-boot:run            # http://localhost:8080/api/v1/issues
mvn verify                     # tests
COMIC_CORS_ALLOWED_ORIGINS=https://<site>.pages.dev mvn spring-boot:run
```

Endpoints: `GET /api/v1/issues`, `/api/v1/issues/{slug}`, `/api/v1/characters/{heroes|villains}`,
`/api/v1/characters/{kind}/{id}`, `/actuator/health`. Contract: `docs/api/openapi.yaml`.

Privacy defaults: stateless, no sessions or cookies, Tomcat access log off, CORS closed unless configured.
Before exposing it publicly, re-run the compliance checklist (section F) — a public API is a feature change.
Spring Boot 3.5.x is pinned; plan the move to Spring Boot 4.x before any production use.
