import { NextRequest, NextResponse } from "next/server";

const GITHUB_REPO = process.env.GITHUB_REPO!;
const GITHUB_TOKEN = process.env.GITHUB_TOKEN!;
const GITHUB_BRANCH = process.env.GITHUB_BRANCH || "main";
const CONFIG_PATH = "config.json";

async function getFileSha(): Promise<string | null> {
  const res = await fetch(
    `https://api.github.com/repos/${GITHUB_REPO}/contents/${CONFIG_PATH}?ref=${GITHUB_BRANCH}`,
    {
      headers: {
        Authorization: `Bearer ${GITHUB_TOKEN}`,
        Accept: "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
      },
      cache: "no-store",
    }
  );
  if (!res.ok) return null;
  const data = await res.json();
  return data.sha ?? null;
}

export async function POST(req: NextRequest) {
  try {
    const config = await req.json();
    const content = Buffer.from(JSON.stringify(config, null, 2) + "\n").toString("base64");
    const sha = await getFileSha();

    const body: Record<string, string> = {
      message: "config: update via web UI",
      content,
      branch: GITHUB_BRANCH,
    };
    if (sha) body.sha = sha;

    const res = await fetch(
      `https://api.github.com/repos/${GITHUB_REPO}/contents/${CONFIG_PATH}`,
      {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${GITHUB_TOKEN}`,
          Accept: "application/vnd.github+json",
          "X-GitHub-Api-Version": "2022-11-28",
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      }
    );

    if (!res.ok) {
      const err = await res.json();
      return NextResponse.json({ error: err.message || "GitHub write failed" }, { status: 502 });
    }

    return NextResponse.json({ ok: true });
  } catch (err) {
    return NextResponse.json({ error: String(err) }, { status: 500 });
  }
}
