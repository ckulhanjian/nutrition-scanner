// mobile/config.js
const API_BASE_URL = 'http://100.70.105.32:5002';
// keeps changing

export const API = {
  upload: `${API_BASE_URL}/api/upload`,
  analyze: `${API_BASE_URL}/api/analyze`,
  status: (jobId) => `${API_BASE_URL}/api/status/${jobId}`,
  results: (jobId) => `${API_BASE_URL}/api/results/${jobId}`,
};