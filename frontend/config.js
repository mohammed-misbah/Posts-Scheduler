const API_BASE =
  window.location.hostname === "127.0.0.1" ||
  window.location.hostname === "localhost"
    ? "http://127.0.0.1:8000"   // local backend
    : "http://143.244.133.159:8000"; // server backend
