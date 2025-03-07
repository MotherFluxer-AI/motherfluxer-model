/**
 * @ai-context: Manages instance selection and load distribution across active model instances
 * @ai-dependencies: ModelInstance, useStore, React hooks
 * @ai-critical-points: Must maintain round-robin selection while respecting health thresholds
 *
 * LEARNING POINTS:
 * 1. Uses modulo operation for circular instance selection
 * 2. Integrates with global state while maintaining local state
 */

import { useState, useEffect, useCallback } from 'react';
import { ModelInstance } from '@/lib/api/types';
import { useStore } from '@/lib/store';

interface LoadBalancerProps {
  instances: ModelInstance[];
  onInstanceSelect: (instance: ModelInstance) => void;
  healthThreshold?: number;
}

export const LoadBalancer: React.FC<LoadBalancerProps> = ({ 
  instances, 
  onInstanceSelect,
  healthThreshold = 50
}) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const { instanceHealth } = useStore();

  /**
   * @ai-function: Selects next available instance using round-robin algorithm
   * @ai-requires: Active instances with health scores above threshold
   * @ai-affects: Current index state and instance selection
   */
  const selectNextInstance = useCallback(() => {
    const activeInstances = instances.filter(instance => 
      instance.isActive && 
      (instanceHealth[instance.id] || instance.healthScore) > healthThreshold
    );

    if (activeInstances.length === 0) return null;

    const nextIndex = (currentIndex + 1) % activeInstances.length;
    const nextInstance = activeInstances[nextIndex];
    
    setCurrentIndex(nextIndex);
    return nextInstance;
  }, [instances, currentIndex, healthThreshold, instanceHealth]);

  /**
   * @ai-function: Periodically checks for better instance selection
   * @ai-requires: Valid instances array and health scores
   * @ai-affects: Instance selection
   */
  useEffect(() => {
    const interval = setInterval(() => {
      const nextInstance = selectNextInstance();
      if (nextInstance) {
        onInstanceSelect(nextInstance);
      }
    }, 60000); // Check every minute

    return () => clearInterval(interval);
  }, [selectNextInstance, onInstanceSelect]);

  /**
   * @ai-function: Initial instance selection
   * @ai-requires: Valid instances array
   * @ai-affects: Instance selection
   */
  useEffect(() => {
    if (instances.length > 0) {
      const initialInstance = selectNextInstance();
      if (initialInstance) {
        onInstanceSelect(initialInstance);
      }
    }
  }, [instances, selectNextInstance, onInstanceSelect]);

  // This is a logical component, no UI needed
  return null;
}; 