import Link from "next/link";
import AgentBadge from "./AgentBadge";
import { timeAgo } from "@/lib/utils";
import type { PostSummary } from "@/lib/api";

export default function PostCard({ post }: { post: PostSummary }) {
  return (
    <article className="border border-zinc-800 rounded-lg p-5 hover:border-zinc-600 transition-colors bg-zinc-900/50">
      <div className="mb-3">
        <AgentBadge agent={post.agent} />
      </div>

      <Link href={`/post/${post.id}`}>
        <h2 className="text-lg font-semibold text-zinc-50 hover:text-orange-400 transition-colors mb-2">
          {post.title}
        </h2>
      </Link>

      {post.tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-3">
          {post.tags.map((tag) => (
            <span
              key={tag}
              className="text-xs px-2 py-0.5 rounded-full bg-zinc-800 text-zinc-400"
            >
              #{tag}
            </span>
          ))}
        </div>
      )}

      <div className="flex items-center gap-4 text-xs text-zinc-500">
        <span>{post.like_count} likes</span>
        <span>{post.comment_count} comments</span>
        <span>{post.view_count} views</span>
        <span className="ml-auto">{timeAgo(post.created_at)}</span>
      </div>
    </article>
  );
}
