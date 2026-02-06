import axios from "axios";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";
const API_V1 = "/api/v1";

const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data) => api.post(`${API_V1}/auth/register`, data),
  login: (data) => api.post(`${API_V1}/auth/login`, data),
};

// Chat API
export const chatAPI = {
  query: (data) => api.post(`${API_V1}/chat/query`, data),
  queryStream: async (data, onChunk, onDone, onError) => {
    const token = localStorage.getItem("token");
    const response = await fetch(`${API_URL}${API_V1}/chat/query-stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop(); // Keep incomplete line in buffer

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.type === "content") {
                onChunk(data.content);
              } else if (data.type === "done") {
                onDone(data.citations, data.sources_count);
              } else if (data.type === "error") {
                onError(data.content);
              }
            } catch (e) {
              console.error("Failed to parse SSE data:", e);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  },
};

// Documents API
export const documentsAPI = {
  list: () => api.get(`${API_V1}/documents/list`),
  reload: (force = false) =>
    api.post(`${API_V1}/documents/reload?force=${force}`),
  status: () => api.get(`${API_V1}/documents/status`),
};

// Assessment API
export const assessmentAPI = {
  start: () => api.post(`${API_V1}/assessment/start`),
  answer: (data) => api.post(`${API_V1}/assessment/answer`, data),
  cancel: (data) => api.post(`${API_V1}/assessment/cancel`, data),
  downloadReport: async (assessmentId) => {
    const token = localStorage.getItem("token");
    const response = await fetch(`${API_URL}${API_V1}/assessment/report/${assessmentId}`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    
    if (!response.ok) {
      throw new Error(`Failed to download report: ${response.statusText}`);
    }
    
    // Get the filename from Content-Disposition header or use default
    const contentDisposition = response.headers.get("Content-Disposition");
    let filename = `assessment-report-${assessmentId}.pdf`;
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i);
      if (filenameMatch) {
        filename = filenameMatch[1];
      }
    }
    
    // Convert response to blob and trigger download
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  },
};

export default api;
