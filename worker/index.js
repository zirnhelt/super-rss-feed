const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, X-API-Key',
};

const INIT_SQL = `
  CREATE TABLE IF NOT EXISTS articles (
    url TEXT PRIMARY KEY,
    read_at TEXT,
    starred INTEGER NOT NULL DEFAULT 0,
    category_override TEXT,
    score_override INTEGER,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
  )
`;

export default {
  async fetch(request, env) {
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: CORS });
    }

    if (request.headers.get('X-API-Key') !== env.API_KEY) {
      return resp({ error: 'Unauthorized' }, 401);
    }

    await env.DB.exec(INIT_SQL);

    const { pathname } = new URL(request.url);

    if (request.method === 'GET' && pathname === '/state') {
      const { results } = await env.DB.prepare('SELECT * FROM articles').all();
      return resp({ articles: results });
    }

    if (request.method !== 'POST') {
      return resp({ error: 'Not found' }, 404);
    }

    const body = await request.json().catch(() => ({}));
    const url  = body.url;
    if (!url) return resp({ error: 'Missing url' }, 400);
    const now  = new Date().toISOString();

    async function upsert(fields) {
      const entries = Object.entries(fields);
      const cols    = entries.map(([k]) => k).join(', ');
      const vals    = entries.map(([, v]) => v);
      const ph      = vals.map(() => '?').join(', ');
      const updates = entries.map(([k]) => `${k}=excluded.${k}`).join(', ');
      await env.DB.prepare(
        `INSERT INTO articles (url, ${cols}, updated_at)
         VALUES (?, ${ph}, ?)
         ON CONFLICT(url) DO UPDATE SET ${updates}, updated_at=excluded.updated_at`
      ).bind(url, ...vals, now).run();
    }

    switch (pathname) {
      case '/mark-read':   await upsert({ read_at: now });   break;
      case '/mark-unread': await upsert({ read_at: null });  break;
      case '/star':        await upsert({ starred: 1 });     break;
      case '/unstar':      await upsert({ starred: 0 });     break;
      case '/correct': {
        const { category_override = null, score_override = null } = body;
        await upsert({ category_override, score_override });
        break;
      }
      default: return resp({ error: 'Not found' }, 404);
    }

    return resp({ ok: true });
  },
};

function resp(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { ...CORS, 'Content-Type': 'application/json' },
  });
}
