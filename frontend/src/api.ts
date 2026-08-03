import axios from 'axios';

export type StoryRequest = {
  child_name: string;
  age: number;
  animal: string;
  themes: string[];
  favorite_color: string;
};

export type StoryResponse = {
  title: string;
  baslangic: string;
  macera: string;
  sonuc: string;
  moral: string;
};

const apiClient = axios.create({
  baseURL: '/',
  headers: {
    'Content-Type': 'application/json',
  },
});

export async function generateStory(payload: StoryRequest): Promise<StoryResponse> {
  const response = await apiClient.post<StoryResponse>('/api/stories/generate', payload);
  return response.data;
}
