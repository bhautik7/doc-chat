import axios, { AxiosError } from "axios";

const apiClient = axios.create({
  baseURL: "http://localhost:8000",
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    const url = error.config?.url ?? "";
    const isAuthRequest = url.startsWith("/auth/");

    // Redirecting on a failed login/register would hide the credentials error
    // from the form that is already handling it.
    if (error.response?.status === 401 && !isAuthRequest) {
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export function getErrorMessage(error: unknown, fallback: string): string {
  if (axios.isAxiosError(error)) {
    const detail = (error.response?.data as { detail?: unknown } | undefined)?.detail;
    if (typeof detail === "string") {
      return detail;
    }
    if (!error.response) {
      return "Could not reach the server. Check your connection and try again.";
    }
  }
  return fallback;
}

export default apiClient;
