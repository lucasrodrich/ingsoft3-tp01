import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import { AuthProvider } from "./auth/AuthContext";
import "./styles.css";
import * as Sentry from "@sentry/react";

// El DSN de un front NO es un secreto: solo sirve para ENVIAR datos, y viaja en el JS que baja el navegador.
Sentry.init({
  dsn: "https://95c011086df2c523a11c722d1e7099e8@o4512285057024000.ingest.us.sentry.io/4512285097328640",
  environment: window.location.hostname,   // de que sitio vino: QA, produccion o localhost
  integrations: [Sentry.browserTracingIntegration()],
  tracesSampleRate: 1.0,
});

ReactDOM.createRoot(document.getElementById("root")).render(<React.StrictMode><BrowserRouter><AuthProvider><App/></AuthProvider></BrowserRouter></React.StrictMode>);

