import { z } from 'zod';

export const approvalRequestSchema = z.object({
  tenantId: z.string().min(1),
  workspaceId: z.string().min(1),
  workflowRunId: z.string().min(1),
  subjectType: z.string().min(1),
  subjectId: z.string().min(1),
  reason: z.string().optional(),
  approverUserIds: z.array(z.string().min(1)).min(1),
});

export const approvalDecisionSchema = z.object({
  approvalId: z.string().min(1),
  decision: z.enum(['APPROVED', 'REJECTED']),
  decidedBy: z.string().min(1),
  decisionReason: z.string().optional(),
});

export type ApprovalRequestInput = z.infer<typeof approvalRequestSchema>;
export type ApprovalDecisionInput = z.infer<typeof approvalDecisionSchema>;
