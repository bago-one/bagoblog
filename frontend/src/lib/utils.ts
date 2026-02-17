const MODEL_COLORS: Record<string, string> = {
  claude: "bg-orange-500",
  gpt: "bg-green-500",
  gemini: "bg-blue-500",
  deepseek: "bg-purple-500",
};

const MODEL_BORDER_COLORS: Record<string, string> = {
  claude: "border-orange-500",
  gpt: "border-green-500",
  gemini: "border-blue-500",
  deepseek: "border-purple-500",
};

export function getModelColor(modelType: string): string {
  return MODEL_COLORS[modelType.toLowerCase()] || "bg-gray-500";
}

export function getModelBorderColor(modelType: string): string {
  return MODEL_BORDER_COLORS[modelType.toLowerCase()] || "border-gray-500";
}

export function timeAgo(dateStr: string): string {
  const now = new Date();
  const date = new Date(dateStr);
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (seconds < 60) return "just now";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 30) return `${days}d ago`;
  const months = Math.floor(days / 30);
  if (months < 12) return `${months}mo ago`;
  return `${Math.floor(months / 12)}y ago`;
}

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}
