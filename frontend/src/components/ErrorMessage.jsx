export default function ErrorMessage({ error }) { return error ? <div className="alert error" role="alert">{error}</div> : null; }

