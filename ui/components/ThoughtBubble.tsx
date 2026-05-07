type ThoughtBubbleProps = {
  source: string;
  body: string;
};

export function ThoughtBubble({ source, body }: ThoughtBubbleProps) {
  return (
    <div className="rounded-md border border-black/10 bg-mist p-3">
      <div className="text-xs font-semibold uppercase tracking-normal text-moss">{source}</div>
      <div className="mt-1 text-sm text-ink">{body}</div>
    </div>
  );
}
