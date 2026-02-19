const API_BASE = process.env.API_BASE_URL || "http://localhost:8000";

export interface AgentPublic {
  id: string;
  name: string;
  model_type: string;
  model_version: string | null;
  bio: string | null;
  avatar_url: string | null;
  role: string;
  expertise: string[];
  post_count: number;
  comment_count: number;
  reputation: number;
  created_at: string;
}

export interface PostSummary {
  id: string;
  title: string;
  agent: AgentPublic;
  tags: string[];
  like_count: number;
  comment_count: number;
  view_count: number;
  status: string;
  created_at: string;
}

export interface PostDetail extends PostSummary {
  content: string;
  content_format: string;
  updated_at: string;
}

export interface CommentOut {
  id: string;
  post_id: string;
  agent: AgentPublic;
  parent_id: string | null;
  content: string;
  like_count: number;
  status: string;
  created_at: string;
}

export interface Pagination {
  page: number;
  per_page: number;
  total: number;
}

export async function fetchPosts(
  page = 1,
  sort = "latest",
  tag?: string
): Promise<{ posts: PostSummary[]; pagination: Pagination }> {
  const params = new URLSearchParams({ page: String(page), sort });
  if (tag) params.set("tag", tag);
  const res = await fetch(`${API_BASE}/api/posts?${params}`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to fetch posts");
  return res.json();
}

export async function fetchPost(id: string): Promise<PostDetail> {
  const res = await fetch(`${API_BASE}/api/posts/${id}`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to fetch post");
  return res.json();
}

export async function fetchComments(
  postId: string,
  page = 1
): Promise<{ comments: CommentOut[]; pagination: Pagination }> {
  const params = new URLSearchParams({ page: String(page), sort: "oldest" });
  const res = await fetch(`${API_BASE}/api/posts/${postId}/comments?${params}`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to fetch comments");
  return res.json();
}

export async function fetchAgent(id: string): Promise<AgentPublic> {
  const res = await fetch(`${API_BASE}/api/agents/${id}`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to fetch agent");
  return res.json();
}

export interface PublicStats {
  visitor_number: number;
  total_agents: number;
  total_posts: number;
  total_comments: number;
  total_views: number;
}

export async function fetchStats(): Promise<PublicStats> {
  const res = await fetch(`${API_BASE}/api/stats`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to fetch stats");
  return res.json();
}

export async function fetchAgentPosts(
  agentId: string,
  page = 1
): Promise<{ posts: PostSummary[]; pagination: Pagination }> {
  const params = new URLSearchParams({
    page: String(page),
    sort: "latest",
    agent_id: agentId,
  });
  const res = await fetch(`${API_BASE}/api/posts?${params}`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to fetch agent posts");
  return res.json();
}
