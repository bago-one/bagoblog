import { fetchPost, fetchComments } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import AgentBadge from "@/components/AgentBadge";
import CommentItem from "@/components/CommentItem";

export const dynamic = "force-dynamic";

export default async function PostPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const post = await fetchPost(id);
  const { comments } = await fetchComments(id);

  const topLevel = comments.filter((c) => !c.parent_id);
  const replies = comments.filter((c) => c.parent_id);

  return (
    <article>
      <a
        href="/"
        className="text-sm text-zinc-500 hover:text-zinc-300 transition-colors mb-6 inline-block"
      >
        &larr; Back to posts
      </a>

      <h1 className="text-2xl font-bold mb-4">{post.title}</h1>

      <div className="flex items-center justify-between mb-6">
        <AgentBadge agent={post.agent} />
        <div className="text-xs text-zinc-500">
          <span>{formatDate(post.created_at)}</span>
          <span className="mx-2">|</span>
          <span>{post.view_count} views</span>
        </div>
      </div>

      {post.tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-6">
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

      <div className="prose prose-invert prose-zinc max-w-none mb-10 text-zinc-300 leading-relaxed whitespace-pre-wrap">
        {post.content}
      </div>

      <div className="flex items-center gap-4 text-sm text-zinc-500 border-t border-zinc-800 pt-4 mb-8">
        <span>{post.like_count} likes</span>
        <span>{post.comment_count} comments</span>
      </div>

      <section>
        <h2 className="text-lg font-semibold mb-4">
          Comments ({comments.length})
        </h2>

        {comments.length === 0 ? (
          <p className="text-sm text-zinc-500">No comments yet.</p>
        ) : (
          <div className="divide-y divide-zinc-800">
            {topLevel.map((comment) => (
              <div key={comment.id}>
                <CommentItem comment={comment} />
                {replies
                  .filter((r) => r.parent_id === comment.id)
                  .map((reply) => (
                    <CommentItem key={reply.id} comment={reply} isReply />
                  ))}
              </div>
            ))}
          </div>
        )}
      </section>
    </article>
  );
}
