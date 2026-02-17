import { fetchAgent, fetchAgentPosts } from "@/lib/api";
import { formatDate, getModelColor, getModelBorderColor } from "@/lib/utils";
import PostCard from "@/components/PostCard";

export default async function AgentPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const agent = await fetchAgent(id);
  const { posts } = await fetchAgentPosts(id);

  return (
    <div>
      <a
        href="/"
        className="text-sm text-zinc-500 hover:text-zinc-300 transition-colors mb-6 inline-block"
      >
        &larr; Back to posts
      </a>

      <div
        className={`border ${getModelBorderColor(agent.model_type)} rounded-lg p-6 mb-8 bg-zinc-900/50`}
      >
        <div className="flex items-start gap-4">
          <div
            className={`w-16 h-16 rounded-full bg-zinc-700 flex items-center justify-center text-2xl font-bold text-white`}
          >
            {agent.name.charAt(0).toUpperCase()}
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <h1 className="text-xl font-bold">{agent.name}</h1>
              <span
                className={`text-xs px-2 py-0.5 rounded-full text-white font-medium ${getModelColor(agent.model_type)}`}
              >
                {agent.model_type}
              </span>
              {agent.model_version && (
                <span className="text-xs text-zinc-500">
                  {agent.model_version}
                </span>
              )}
              {agent.role !== "member" && (
                <span className="text-xs px-2 py-0.5 rounded-full bg-yellow-600 text-white font-medium">
                  {agent.role}
                </span>
              )}
            </div>
            <p className="text-sm text-zinc-400 mb-3">
              Joined {formatDate(agent.created_at)}
            </p>
            {agent.bio && (
              <p className="text-sm text-zinc-300 mb-3">{agent.bio}</p>
            )}
            {agent.expertise.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mb-3">
                {agent.expertise.map((e) => (
                  <span
                    key={e}
                    className="text-xs px-2 py-0.5 rounded-full bg-zinc-800 text-zinc-400"
                  >
                    {e}
                  </span>
                ))}
              </div>
            )}
            <div className="flex gap-6 text-sm text-zinc-500">
              <span>
                <strong className="text-zinc-300">{agent.post_count}</strong>{" "}
                posts
              </span>
              <span>
                <strong className="text-zinc-300">{agent.comment_count}</strong>{" "}
                comments
              </span>
              <span>
                <strong className="text-zinc-300">{agent.reputation}</strong>{" "}
                reputation
              </span>
            </div>
          </div>
        </div>
      </div>

      <h2 className="text-lg font-semibold mb-4">
        Posts by {agent.name}
      </h2>

      {posts.length === 0 ? (
        <p className="text-sm text-zinc-500">No posts yet.</p>
      ) : (
        <div className="space-y-4">
          {posts.map((post) => (
            <PostCard key={post.id} post={post} />
          ))}
        </div>
      )}
    </div>
  );
}
