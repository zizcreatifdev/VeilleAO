import { NextResponse } from "next/server";

const GITHUB_REPO = process.env.GITHUB_REPO!;
const GITHUB_TOKEN = process.env.GITHUB_TOKEN!;
const CONFIG_PATH = "config.json";

export async function GET() {
  try {
    const res = await fetch(
      `https://api.github.com/repos/${GITHUB_REPO}/contents/${CONFIG_PATH}`,
      {
        headers: {
          Authorization: `Bearer ${GITHUB_TOKEN}`,
          Accept: "application/vnd.github+json",
          "X-GitHub-Api-Version": "2022-11-28",
        },
        cache: "no-store",
      }
    );

    if (!res.ok) {
      return NextResponse.json({ error: "Failed to fetch config from GitHub" }, { status: 502 });
    }

    const data = await res.json();
    const content = Buffer.from(data.content, "base64").toString("utf-8");
    const config = JSON.parse(content);

    return NextResponse.json(config);
  } catch (err) {
    return NextResponse.json({ error: String(err) }, { status: 500 });
  }
}
