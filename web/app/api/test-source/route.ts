import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  const { url } = await req.json();

  if (!url || typeof url !== "string") {
    return NextResponse.json({ ok: false, error: "URL manquante" }, { status: 400 });
  }

  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 10_000);

    const res = await fetch(url, {
      method: "HEAD",
      signal: controller.signal,
      redirect: "follow",
      headers: {
        "User-Agent":
          "Mozilla/5.0 (compatible; VeilleAO-Config/1.0; +https://github.com/zizcreatifdev/VeilleAO)",
      },
    });
    clearTimeout(timeout);

    if (res.ok || res.status === 405) {
      return NextResponse.json({ ok: true, status: res.status });
    }

    // Try GET if HEAD returned a suspicious status
    if (res.status >= 400) {
      const controller2 = new AbortController();
      const timeout2 = setTimeout(() => controller2.abort(), 10_000);
      const res2 = await fetch(url, {
        method: "GET",
        signal: controller2.signal,
        redirect: "follow",
        headers: {
          "User-Agent":
            "Mozilla/5.0 (compatible; VeilleAO-Config/1.0; +https://github.com/zizcreatifdev/VeilleAO)",
        },
      });
      clearTimeout(timeout2);

      if (res2.ok) {
        return NextResponse.json({ ok: true, status: res2.status });
      }
      return NextResponse.json(
        { ok: false, error: `HTTP ${res2.status}` },
        { status: 200 }
      );
    }

    return NextResponse.json({ ok: false, error: `HTTP ${res.status}` }, { status: 200 });
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    if (msg.includes("abort") || msg.includes("timeout")) {
      return NextResponse.json({ ok: false, error: "Timeout (>10s)" }, { status: 200 });
    }
    return NextResponse.json({ ok: false, error: msg }, { status: 200 });
  }
}
