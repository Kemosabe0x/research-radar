import { ArticleActions } from "@/components/article-actions";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

type ApiList<T> = { items: T[] };

type Article = {
  journal_name: string;
  article_title: string;
  article_link: string;
  published_date: string;
  created_at: string;
  status?: string | null;
  alert_summary?: string | null;
  article_path?: string | null;
  digest_path?: string | null;
};

type GeneratedDoc = {
  title?: string;
  path: string;
  generated_at?: string;
  preview?: string;
};

const API_BASE =
  process.env.NEXT_PUBLIC_RSSAGENT_API_BASE_URL ?? "http://127.0.0.1:8787";

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Failed to load ${path}: ${response.status}`);
  }
  return (await response.json()) as T;
}

export default async function HomePage() {
  const [articles, generatedArticles, digests] = await Promise.all([
    getJson<ApiList<Article>>("/api/articles?limit=30"),
    getJson<ApiList<GeneratedDoc>>("/api/generated/articles"),
    getJson<ApiList<GeneratedDoc>>("/api/generated/digests"),
  ]);

  return (
    <main className="mx-auto max-w-6xl space-y-6 p-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold">RSSAgent Feed + Digestion Dashboard</h1>
        <p className="text-sm text-slate-600">
          API-driven view for latest ingestion, digestion interactions, and generated markdown.
        </p>
      </header>

      <section className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Latest feed items</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-semibold">{articles.items.length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Generated articles</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-semibold">{generatedArticles.items.length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Generated digests</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-semibold">{digests.items.length}</p>
          </CardContent>
        </Card>
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Latest Articles</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {articles.items.map((article) => (
              <div key={article.article_link} className="space-y-2 rounded-md border p-3">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="font-medium">{article.article_title}</p>
                  <Badge>{article.status ?? "new"}</Badge>
                </div>
                <p className="text-xs text-slate-600">{article.journal_name}</p>
                <a className="text-sm text-blue-700 underline" href={article.article_link}>
                  Source
                </a>
                <ArticleActions articleLink={article.article_link} />
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Generated Content Browser</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-3">
              <h2 className="text-sm font-semibold text-slate-700">Article drafts</h2>
              {generatedArticles.items.length === 0 && (
                <p className="text-sm text-slate-500">No generated article markdown yet.</p>
              )}
              {generatedArticles.items.map((item) => (
                <div key={item.path} className="rounded border p-3 text-sm">
                  <p className="font-medium">{item.title ?? item.path}</p>
                  <p className="text-slate-500">{item.path}</p>
                </div>
              ))}
            </div>

            <div className="space-y-3">
              <h2 className="text-sm font-semibold text-slate-700">Digest files</h2>
              {digests.items.length === 0 && (
                <p className="text-sm text-slate-500">No digest markdown yet.</p>
              )}
              {digests.items.map((item) => (
                <div key={item.path} className="rounded border p-3 text-sm">
                  <p className="font-medium">{item.title ?? item.path}</p>
                  <p className="text-slate-500">{item.path}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </section>
    </main>
  );
}
