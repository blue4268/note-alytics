import json
import os
import glob

today = os.environ['TODAY']

with open('/tmp/profile.json') as f:
    profile_raw = json.load(f)
with open('/tmp/articles.json') as f:
    articles_raw = json.load(f)

profile = profile_raw.get('data', {})

articles = []
for a in articles_raw.get('data', {}).get('contents', []):
    articles.append({
        'title': a.get('name', ''),
        'likes': a.get('likeCount', 0),
        'comments': a.get('commentCount', 0),
        'published_at': (a.get('publishAt') or '')[:10],
        'is_paid': a.get('isPayment', False),
        'price': a.get('price', 0)
    })

data = {
    'date': today,
    'followers': profile.get('followerCount', 0),
    'following': profile.get('followingCount', 0),
    'article_count': profile.get('noteCount', 0),
    'articles': articles
}

with open(f'data/{today}.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

data_files = sorted(glob.glob('data/*.json'))
data_files = [f for f in data_files if f != f'data/{today}.json']
prev = None
if data_files:
    with open(data_files[-1], encoding='utf-8') as f:
        prev = json.load(f)

follower_diff = ''
if prev:
    diff = data['followers'] - prev['followers']
    follower_diff = f'（前週比 {"+" if diff >= 0 else ""}{diff}人）'

rows = ''
for a in data['articles']:
    diff_str = ''
    if prev:
        pa = next((p for p in prev['articles'] if p['title'] == a['title']), None)
        if pa:
            d = a['likes'] - pa['likes']
            diff_str = f'{"+" if d >= 0 else ""}{d}'
    rows += f"| {a['title'][:30]} | {a['likes']} | {diff_str} |\n"

if prev:
    prev_titles = {p['title'] for p in prev['articles']}
    new = [a['title'] for a in data['articles'] if a['title'] not in prev_titles]
    new_articles = '\n'.join(f'- {t}' for t in new) if new else 'なし'
else:
    new_articles = '（初回記録のため比較なし）'

summary = '初回記録' if not prev else f'フォロワー{follower_diff}、記事数{data["article_count"]}本'

report = f"""# note週次レポート {today}

## アカウント概況
- フォロワー: {data["followers"]}人{follower_diff}
- 記事数: {data["article_count"]}本

## 記事別いいね数
| タイトル | いいね | 前週比 |
|---|---|---|
{rows}
## 今週の新規記事
{new_articles}

## サマリー
{summary}
"""

with open(f'reports/{today}-weekly.md', 'w', encoding='utf-8') as f:
    f.write(report)

print(f'Done: data/{today}.json and reports/{today}-weekly.md')
