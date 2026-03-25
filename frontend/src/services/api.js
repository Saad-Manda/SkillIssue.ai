const API_BASE_URL = "http://localhost:8000/api/v1"; // Local FastAPI URL

// Helper to handle API responses
const handleResponse = async (response) => {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "API request failed");
  }
  return response.json();
};

export const api = {
  // --- Auth ---
  signup: async (userData) => {
    // expects { email, password, full_name } or whatever the backend requires
    // FastAPI expects SignupRequest model
    const response = await fetch(`${API_BASE_URL}/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(userData),
    });
    return handleResponse(response);
  },

  login: async (credentials) => {
    // expects { email, password }
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(credentials),
    });
    return handleResponse(response);
  },

  logout: async (token) => {
    const response = await fetch(`${API_BASE_URL}/auth/logout`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    // In many implementations backend might not return JSON for logout, but let's assume standard response
    return handleResponse(response);
  },

  // --- Users ---
  getUserProfile: async (userId, token) => {
    const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return handleResponse(response);
  },

  createUserProfile: async (profileData, signupToken) => {
    // Route shows `signup_token` as query parameter
    const response = await fetch(
      `${API_BASE_URL}/users/?signup_token=${signupToken}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(profileData),
      },
    );
    return handleResponse(response);
  },

  updateUserProfile: async (userId, profileData, token) => {
    const headers = { "Content-Type": "application/json" };
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
    const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
      method: "PATCH",
      headers,
      body: JSON.stringify(profileData),
    });
    return handleResponse(response);
  },

  // --- Job Description & Interview ---
  createJD: async (jdData) => {
    // expects { title, role, company, description, etc... }
    const response = await fetch(`${API_BASE_URL}/jd/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(jdData),
    });
    return handleResponse(response);
  },

  getJD: async (jdId) => {
    const response = await fetch(`${API_BASE_URL}/jd/${jdId}`);
    return handleResponse(response);
  },

  startInterview: async (userId, jdId, length = "short") => {
    const response = await fetch(
      `${API_BASE_URL}/session/user/${userId}/jd/${jdId}/length/${length}`,
    );
    return handleResponse(response);
  },

  submitAnswer: async (sessionId, answer) => {
    const response = await fetch(
      `${API_BASE_URL}/session/${sessionId}/answer`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answer }),
      },
    );
    return handleResponse(response);
  },

  getReport: async (sessionId) => {
    const response = await fetch(`${API_BASE_URL}/session/${sessionId}/report`);
    return handleResponse(response);
  },

  // --- Stored interview history ---
  getAllInterviews: async () => {
    const response = await fetch(`${API_BASE_URL}/interview/`);
    return handleResponse(response);
  },

  getInterviewDetails: async (interviewId) => {
    const response = await fetch(`${API_BASE_URL}/interview/${interviewId}`);
    return handleResponse(response);
  },

  deleteInterview: async (interviewId) => {
    const response = await fetch(`${API_BASE_URL}/interview/${interviewId}`, {
      method: 'DELETE',
    });
    return handleResponse(response);
  },

  getJDDetails: async (jdId) => {
    const response = await fetch(`${API_BASE_URL}/jd/${jdId}`);
    return handleResponse(response);
  }
};
