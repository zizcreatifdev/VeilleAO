import { NextResponse } from "next/server";

const GITHUB_REPO = process.env.GITHUB_REPO!;
const GITHUB_TOKEN = process.env.GITHUB_TOKEN!;
const GITHUB_BRANCH = process.env.GITHUB_BRANCH || "main";
const WORKFLOW_FILE = process.env.WORKFLOW_FILE || "veille-ao.yml";

export async function POST() {
  try {
    const res = await fetch(
      `https://api.github.com/repos/${GITHUB_REPO}/actions/workflows/${WORKFLOW_FILE}/dispatches`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${GITHUB_TOKEN}`,
          Accept: "application/vnd.github+json",
          "X-GitHub-Api-Version": "2022-11-28",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ ref: GITHUB_BRANCH }),
      }
    );

    if (res.status === 204) {
      return NextResponse.json({ ok: true });
    }

    const err = await res.json().catch(() => ({ message: `HTTP ${res.status}` }));
    return NextResponse.json(
      { error: err.message || "GitHub Actions dispatch failed" },
      { status: 502 }
    );
  } catch (err) {
    return NextResponse.json({ error: String(err) }, { status: 500 });
  }
}
