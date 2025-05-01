from sentence_transformers import SentenceTransformer, util
from .models import Job, UserRecommendation

# load your model once
_model = SentenceTransformer('all-MiniLM-L6-v2')

def _embed(texts):
    return _model.encode(texts, convert_to_tensor=True)

def compute_nlp_recommendations(user, top_k=10):
    """Return list of (job_id, score) sorted desc."""
    info = {
        "title": user.title,
        "experience": user.experience_years,
        "education": user.education,
        "skills": user.skills,
    }
    # build one “doc” for the user
    user_doc = ' '.join([
        info.get('title',''),
        info.get('education',''),
        ' '.join(info.get('skills',[]))
    ])
    user_emb = _embed([user_doc])[0]

    # prepare job embeddings in batch
    jobs     = list(Job.objects.all())
    job_docs = [f"{j.job_title} {j.job_description or ''}" for j in jobs]
    job_embs = _embed(job_docs)

    # cosine similarities
    sims = util.cos_sim(user_emb, job_embs)[0]
    # pick top_k
    top_idxs = sims.argsort(descending=True)[:top_k]
    return [(jobs[i].id, float(sims[i])) for i in top_idxs]

def refresh_user_recommendations(user, top_k=10):
    """Compute, delete old & bulk‐insert new recommendations."""
    # compute
    recs = compute_nlp_recommendations(user, top_k=top_k)
    # clear old
    UserRecommendation.objects.filter(user=user).delete()
    # bulk create
    objs = [
        UserRecommendation(user=user, job_id=job_id, score=score)
        for job_id, score in recs
    ]
    UserRecommendation.objects.bulk_create(objs)
    # return the fresh QuerySet
    return UserRecommendation.objects.filter(user=user).select_related('job')[:top_k]

