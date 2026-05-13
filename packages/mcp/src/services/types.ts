export type RequestContext = {
  tenantId: string;
  userId: string;
  workspaceId: string;
  roles: string[];
};

export type Task = {
  id: string;
  title: string;
  status: 'todo' | 'in_progress' | 'blocked' | 'done';
  assigneeId?: string | null;
  sprintId?: string | null;
  updatedAtIso: string;
};

export type Sprint = {
  id: string;
  name: string;
  startDateIso: string;
  endDateIso: string;
};

export type MemorySearchHit = {
  itemId: string;
  score: number;
  preview?: string;
  metadata?: Record<string, unknown>;
};

export type TeamLoad = {
  memberId: string;
  capacityPoints: number;
  allocatedPoints: number;
  availablePoints: number;
};

export type RiskAlert = {
  id: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  createdAtIso: string;
};
