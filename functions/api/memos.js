// メモ同期API（Cloudflare Pages Functions + KV）
// KVバインディング名: MEMOS

const KV_KEY = 'all-memos';
const HEADERS = {
  'Content-Type': 'application/json',
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, PUT, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

// GET /api/memos — 全メモ取得
export async function onRequestGet(context) {
  const data = await context.env.MEMOS.get(KV_KEY, 'json') || {};
  return new Response(JSON.stringify(data), { headers: HEADERS });
}

// PUT /api/memos — 全メモ保存
export async function onRequestPut(context) {
  const body = await context.request.json();
  await context.env.MEMOS.put(KV_KEY, JSON.stringify(body));
  return new Response(JSON.stringify(body), { headers: HEADERS });
}

// OPTIONS /api/memos — CORS preflight
export async function onRequestOptions() {
  return new Response(null, { status: 204, headers: HEADERS });
}
