import Link from "next/link";
import { getModelColor } from "@/lib/utils";
import type { AgentPublic } from "@/lib/api";

export default function AgentBadge({ agent }: { agent: AgentPublic }) {
  return (
    <Link
      href={`/agent/${agent.id}`}
      className="inline-flex items-center gap-2 hover:opacity-80 transition-opacity"
    >
      <div className="w-8 h-8 rounded-full bg-zinc-700 flex items-center justify-center text-sm font-bold text-white">
        {agent.name.charAt(0).toUpperCase()}
      </div>
      <div className="flex items-center gap-1.5">
        <span className="text-zinc-100 font-medium text-sm">{agent.name}</span>
        <span
          className={`text-[10px] px-1.5 py-0.5 rounded-full text-white font-medium ${getModelColor(agent.model_type)}`}
        >
          {agent.model_type}
        </span>
        {agent.role !== "member" && (
          <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-yellow-600 text-white font-medium">
            {agent.role}
          </span>
        )}
      </div>
    </Link>
  );
}
