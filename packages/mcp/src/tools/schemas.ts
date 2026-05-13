import { z } from 'zod';

// Shared
export const workspaceIdSchema = z.string().min(1);

// get_tasks
export const getTasksInput = z.object({
  workspaceId: workspaceIdSchema,
  status: z.enum(['todo', 'in_progress', 'done']).optional(),
  limit: z.number().int().min(1).max(200).default(50),
});

export const getTasksOutput = z.object({
  tasks: z.array(
    z.object({
      id: z.string(),
      title: z.string(),
      status: z.enum(['todo', 'in_progress', 'done']),
      assigneeId: z.string().nullable().optional(),
      updatedAt: z.string(),
    }),
  ),
});

// create_task
export const createTaskInput = z.object({
  workspaceId: workspaceIdSchema,
  title: z.string().min(1),
  description: z.string().optional(),
  assigneeId: z.string().optional(),
});

export const createTaskOutput = z.object({
  taskId: z.string(),
});

// update_task
export const updateTaskInput = z.object({
  workspaceId: workspaceIdSchema,
  taskId: z.string().min(1),
  title: z.string().min(1).optional(),
  description: z.string().optional(),
  status: z.enum(['todo', 'in_progress', 'done']).optional(),
  assigneeId: z.string().nullable().optional(),
});

export const updateTaskOutput = z.object({
  ok: z.boolean(),
});

// create_sprint
export const createSprintInput = z.object({
  workspaceId: workspaceIdSchema,
  name: z.string().min(1),
  startDate: z.string().min(1),
  endDate: z.string().min(1),
});

export const createSprintOutput = z.object({
  sprintId: z.string(),
});

// search_memory
export const searchMemoryInput = z.object({
  workspaceId: workspaceIdSchema,
  query: z.string().min(1),
  topK: z.number().int().min(1).max(50).default(5),
});

export const searchMemoryOutput = z.object({
  hits: z.array(
    z.object({
      id: z.string(),
      score: z.number(),
      preview: z.string().optional(),
      metadata: z.record(z.unknown()).optional(),
    }),
  ),
});

// get_team_load
export const getTeamLoadInput = z.object({
  workspaceId: workspaceIdSchema,
});

export const getTeamLoadOutput = z.object({
  members: z.array(
    z.object({
      userId: z.string(),
      load: z.number(),
      capacity: z.number(),
    }),
  ),
});

// get_risk_alerts
export const getRiskAlertsInput = z.object({
  workspaceId: workspaceIdSchema,
  severity: z.enum(['low', 'medium', 'high', 'critical']).optional(),
  limit: z.number().int().min(1).max(200).default(50),
});

export const getRiskAlertsOutput = z.object({
  alerts: z.array(
    z.object({
      id: z.string(),
      severity: z.enum(['low', 'medium', 'high', 'critical']),
      title: z.string(),
      createdAt: z.string(),
    }),
  ),
});
