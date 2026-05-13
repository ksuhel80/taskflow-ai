import type { z } from 'zod';

import type {
  createSprintInput,
  createSprintOutput,
  createTaskInput,
  createTaskOutput,
  getRiskAlertsInput,
  getRiskAlertsOutput,
  getTasksInput,
  getTasksOutput,
  getTeamLoadInput,
  getTeamLoadOutput,
  searchMemoryInput,
  searchMemoryOutput,
  updateTaskInput,
  updateTaskOutput,
} from '../tools/schemas.js';
import type { RequestContext } from './types.js';

export type TaskFlowService = {
  getTasks: (
    ctx: RequestContext,
    input: z.infer<typeof getTasksInput>,
  ) => Promise<z.infer<typeof getTasksOutput>>;
  createTask: (
    ctx: RequestContext,
    input: z.infer<typeof createTaskInput>,
  ) => Promise<z.infer<typeof createTaskOutput>>;
  updateTask: (
    ctx: RequestContext,
    input: z.infer<typeof updateTaskInput>,
  ) => Promise<z.infer<typeof updateTaskOutput>>;
  createSprint: (
    ctx: RequestContext,
    input: z.infer<typeof createSprintInput>,
  ) => Promise<z.infer<typeof createSprintOutput>>;
  searchMemory: (
    ctx: RequestContext,
    input: z.infer<typeof searchMemoryInput>,
  ) => Promise<z.infer<typeof searchMemoryOutput>>;
  getTeamLoad: (
    ctx: RequestContext,
    input: z.infer<typeof getTeamLoadInput>,
  ) => Promise<z.infer<typeof getTeamLoadOutput>>;
  getRiskAlerts: (
    ctx: RequestContext,
    input: z.infer<typeof getRiskAlertsInput>,
  ) => Promise<z.infer<typeof getRiskAlertsOutput>>;
};

export function createStubTaskFlowService(): TaskFlowService {
  return {
    async getTasks() {
      return { tasks: [] };
    },
    async createTask() {
      return { taskId: 'stub-task-id' };
    },
    async updateTask() {
      return { ok: true };
    },
    async createSprint() {
      return { sprintId: 'stub-sprint-id' };
    },
    async searchMemory() {
      return { hits: [] };
    },
    async getTeamLoad() {
      return { members: [] };
    },
    async getRiskAlerts() {
      return { alerts: [] };
    },
  };
}
