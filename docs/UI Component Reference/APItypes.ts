export interface ModelInstance {
  id: string;
  modelId: string;
  instanceName: string;
  hostAddress: string;
  healthScore: number;
  isActive: boolean;
  version: string;
  containerVersion?: string;
  adminId?: string;
  registeredAt?: Date;
  lastHealthCheck?: Date;
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
} 