import apiClient from './client';
import { TokenResponse, RegisterResponse, User } from '../types';

export const login = async (email: string, password: string): Promise<TokenResponse> => {
  const { data } = await apiClient.post<TokenResponse>('/auth/login', { email, password });
  return data;
};

export const register = async (email: string, password: string): Promise<RegisterResponse> => {
  const { data } = await apiClient.post<RegisterResponse>('/auth/register', { email, password });
  return data;
};

export const logout = async (refreshToken: string): Promise<void> => {
  await apiClient.post('/auth/logout', { refresh_token: refreshToken });
};

export const refreshToken = async (token: string): Promise<TokenResponse> => {
  const { data } = await apiClient.post<TokenResponse>('/auth/refresh', { refresh_token: token });
  return data;
};

export const getMe = async (): Promise<User> => {
  const { data } = await apiClient.get<User>('/auth/me');
  return data;
};
