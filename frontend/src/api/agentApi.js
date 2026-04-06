import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
  timeout: 60000,
});

export async function uploadCSV(file) {
  const formData = new FormData();
  formData.append("file", file);
  const response = await api.post("/orders/upload-csv", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

export async function prioritizeOrders(batch) {
  const response = await api.post("/orders/prioritize", batch);
  return response.data;
}
