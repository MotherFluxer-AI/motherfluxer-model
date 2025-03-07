/**
 * @ai-context: Performs periodic health checks on model instances
 * @ai-dependencies: ApiClient, ModelInstance interface
 * @ai-critical-points: Must clean up intervals and handle failed checks gracefully
 *
 * LEARNING POINTS:
 * 1. Implements interval-based health monitoring
 * 2. Uses callback pattern for health updates
 */

import { useEffect, useCallback } from 'react';
import { ModelInstance } from '@/lib/api/types';
import { ApiClient } from '@/lib/api/client';
import { useStore } from '@/lib/store';

interface HealthCheckerProps {
  instance: ModelInstance;
  onHealthUpdate: (healthScore: number) => void;
  checkInterval?: number; // in milliseconds
}

interface HealthResponse {
  health: number;
  timestamp: string;
  metrics?: {
    latency: number;
    errorRate: number;
    successRate: number;
  };
}

export const HealthChecker: React.FC<HealthCheckerProps> = ({
  instance,
  onHealthUpdate,
  checkInterval = 30000 // Default to 30 seconds
}) => {
  const { updateInstanceHealth } = useStore();

  /**
   * @ai-function: Performs health check for a specific instance
   * @ai-requires: Valid instance ID and API endpoint availability
   * @ai-affects: Instance health score through callback and store
   */
  const checkHealth = useCallback(async () => {
    try {
      const response = await ApiClient.get<HealthResponse>(
        `/health/${instance.id}`
      );
      
      if (response.data) {
        const healthScore = response.data.health;
        
        // Update both local handler and global store
        onHealthUpdate(healthScore);
        updateInstanceHealth(instance.id, healthScore);

        if (process.env.NODE_ENV === 'development' && response.data.metrics) {
          // Only log metrics in development
          console.debug('Health metrics:', response.data.metrics);
        }
      }
    } catch (error) {
      // On failure, set health to 0 and log error
      onHealthUpdate(0);
      updateInstanceHealth(instance.id, 0);
      
      if (process.env.NODE_ENV === 'development') {
        console.error('Health check failed:', error);
      }
    }
  }, [instance.id, onHealthUpdate, updateInstanceHealth]);

  /**
   * @ai-function: Sets up and manages periodic health check interval
   * @ai-requires: Valid checkHealth callback and interval duration
   * @ai-affects: Instance health monitoring lifecycle
   */
  useEffect(() => {
    // Perform initial health check
    checkHealth();
    
    // Set up periodic health checks
    const interval = setInterval(checkHealth, checkInterval);
    
    // Cleanup on unmount or when dependencies change
    return () => clearInterval(interval);
  }, [checkHealth, checkInterval]);

  // This is a logical component, no UI needed
  return null;
};