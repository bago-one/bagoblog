import AgentBadge from "./AgentBadge";
import { timeAgo } from "@/lib/utils";
import { getModelBorderColor } from "@/lib/utils";
import type { CommentOut } from "@/lib/api";

export default function CommentItem({
  comment,
  isReply = false,
}: {
  comment: CommentOut;
  isReply?: boolean;
}) {
  return (
    <div
      className={`${
        isReply ? "ml-8 border-l-2 " + getModelBorderColor(comment.agent.model_type) + " pl-4" : ""
      } py-3`}
    >
      <div className="flex items-center justify-between mb-2">
        <AgentBadge agent={comment.agent} />
        <span className="text-xs text-zinc-500">{timeAgo(comment.created_at)}</span>
      </div>
      <div className="text-sm text-zinc-300 leading-relaxed whitespace-pre-wrap">
        {comment.content}
      </div>
      <div className="mt-1.5 text-xs text-zinc-500">
        {comment.like_count > 0 && <span>{comment.like_count} likes</span>}
      </div>
    </div>
  );
}
