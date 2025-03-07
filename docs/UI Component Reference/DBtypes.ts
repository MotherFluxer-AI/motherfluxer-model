export interface User {
  id: string;
  email: string;
  hashed_password: string;
  role: 'user' | 'admin';
  is_active: boolean;
  request_limit: number;
  created_at: Date;
  last_login: Date;
}

export interface ModelInstance {
  id: string;
  admin_id: string;
  instance_name: string;
  host_address: string;
  health_score: number;
  is_active: boolean;
  version: string;
  registered_at: Date;
  last_health_check: Date;
  container_version: string;
}

export interface RateLimit {
  id: string;
  user_id: string;
  window_start: Date;
  request_count: number;
  last_request: Date;
} 