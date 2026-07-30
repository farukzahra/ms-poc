export type BriefingBlock =
  | { kind: "subheading"; text: string }
  | { kind: "bullet"; text: string }
  | { kind: "numbered"; text: string; order: number }
  | { kind: "text"; text: string };

export interface BriefingSection {
  blocks: BriefingBlock[];
}

export interface ParsedBriefing {
  title: string;
  facts: BriefingSection | null;
  recommendations: BriefingSection | null;
  hasStructure: boolean;
}

const SECTION_FACT = /^(#+\s*)?(AI\s+)?FACTS?(?::|\s|$)/i;
const SECTION_REC = /^(#+\s*)?(AI\s+)?RECOMMENDATIONS?(?::|\s|$)/i;
const NUMBERED = /^(\d+)\.\s+(.+)$/;
const BULLET = /^[-*•]\s+(.+)$/;

function isSubheading(line: string): boolean {
  if (NUMBERED.test(line) || BULLET.test(line)) return false;
  if (line.length > 80) return false;
  if (line.endsWith(":") && line.length <= 56) return true;
  if (!line.includes(".") && line.split(/\s+/).length <= 7) return true;
  return false;
}

function splitFactBullet(text: string): { label: string; value: string } {
  const boldMatch = text.match(/^\*\*(.+?)\*\*:?\s*(.*)$/);
  if (boldMatch) {
    return { label: boldMatch[1], value: boldMatch[2] || "—" };
  }
  const colonIndex = text.indexOf(":");
  if (colonIndex > 0 && colonIndex < 52) {
    return {
      label: text.slice(0, colonIndex).trim(),
      value: text.slice(colonIndex + 1).trim() || "—",
    };
  }
  return { label: "", value: text };
}

export function parseBriefing(content: string): ParsedBriefing {
  let title = "";
  const preLines: string[] = [];
  const factBlocks: BriefingBlock[] = [];
  const recBlocks: BriefingBlock[] = [];
  let mode: "pre" | "facts" | "recommendations" = "pre";

  function push(block: BriefingBlock) {
    if (mode === "facts") factBlocks.push(block);
    else if (mode === "recommendations") recBlocks.push(block);
    else if (block.kind === "text") preLines.push(block.text);
  }

  for (const rawLine of content.split("\n")) {
    const line = rawLine.trim();
    if (!line) continue;

    if (line.startsWith("# ")) {
      title = line.slice(2).trim();
      continue;
    }

    if (SECTION_FACT.test(line)) {
      mode = "facts";
      const rest = line.replace(SECTION_FACT, "").trim();
      if (rest) factBlocks.push({ kind: "text", text: rest });
      continue;
    }

    if (SECTION_REC.test(line)) {
      mode = "recommendations";
      const rest = line.replace(SECTION_REC, "").trim();
      if (rest) recBlocks.push({ kind: "text", text: rest });
      continue;
    }

    const numbered = line.match(NUMBERED);
    if (numbered) {
      push({ kind: "numbered", text: numbered[2], order: Number(numbered[1]) });
      continue;
    }

    const bullet = line.match(BULLET);
    if (bullet) {
      push({ kind: "bullet", text: bullet[1] });
      continue;
    }

    if (mode !== "pre" && isSubheading(line)) {
      push({ kind: "subheading", text: line.replace(/:$/, "") });
      continue;
    }

    push({ kind: "text", text: line });
  }

  if (!title && preLines.length > 0) {
    title = preLines[0];
    for (const extra of preLines.slice(1)) {
      factBlocks.unshift({ kind: "text", text: extra });
    }
  }

  const facts = factBlocks.length ? { blocks: factBlocks } : null;
  const recommendations = recBlocks.length ? { blocks: recBlocks } : null;

  return {
    title,
    facts,
    recommendations,
    hasStructure: Boolean(facts || recommendations),
  };
}

export function factGridItems(blocks: BriefingBlock[]): Array<{ label: string; value: string }> {
  return blocks
    .filter((block): block is { kind: "bullet"; text: string } => block.kind === "bullet")
    .map((block) => splitFactBullet(block.text))
    .filter((item) => item.label !== "");
}

export function splitRecommendationBullet(text: string): { title: string; detail: string } {
  const boldMatch = text.match(/^\*\*(.+?)\*\*:?\s*(.*)$/);
  if (boldMatch) {
    return { title: boldMatch[1], detail: boldMatch[2] };
  }
  const colonIndex = text.indexOf(":");
  if (colonIndex > 0 && colonIndex < 56) {
    return {
      title: text.slice(0, colonIndex).trim(),
      detail: text.slice(colonIndex + 1).trim(),
    };
  }
  return { title: "", detail: text };
}
