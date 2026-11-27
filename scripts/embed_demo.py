import time

from app.services.embedder import embed_passages, embed_query

passages = [
    "مبلغ کل قرارداد معادل ۲۵٬۰۰۰٬۰۰۰٬۰۰۰ ریال است.",
    "محل تحویل: تهران، خیابان آزادی.",
    "مدت این قرارداد شش ماه از تاریخ امضا است.",
    "در صورت تأخیر فروشنده، روزانه یک درصد جریمه اعمال می‌شود.",
]
questions = [
    "مبلغ قرارداد چقدر است؟",
    "تحویل کالا کجا انجام می‌شود؟",
    "اگر فروشنده دیر کند چه می‌شود؟",
]

t0 = time.time()
passage_vecs = embed_passages(passages)
print(f"embedded {len(passages)} passages in {time.time() - t0:.1f}s, dim={len(passage_vecs[0])}")

for q in questions:
    q_vec = embed_query(q)
    scores = [sum(a * b for a, b in zip(q_vec, p)) for p in passage_vecs]
    best = max(range(len(passages)), key=lambda i: scores[i])
    print(f"\nسؤال: {q}")
    for i, s in enumerate(scores):
        mark = "  <-- best" if i == best else ""
        print(f"  {s:.3f}  [{i}]{mark}")