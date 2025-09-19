# logic.py
from fuzzywuzzy import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- alias expansion ---
ALIAS = {
    'py': 'python',
    'js': 'javascript',
    'reactjs': 'react',
    'nodejs': 'node'
}

def expand_aliases(lst):
    return [ALIAS.get(x, x) for x in lst]

# --- normalization ---
def norm_list(s):
    if not s:
        return []
    # handle both list and comma-separated string
    if isinstance(s, list):
        return [x.strip().lower() for x in s if isinstance(x, str) and x.strip()]
    return [x.strip().lower() for x in str(s).split(',') if x.strip()]

# --- scoring helpers ---
def skills_overlap_score(profile_skills, job_skills):
    if not profile_skills or not job_skills:
        return 0.0
    p = set(profile_skills); j = set(job_skills)
    inter = len(p & j)
    union = len(p | j)
    return inter / union if union else 0.0

def fuzzy_location_score(profile_loc, job_loc):
    if not profile_loc or not job_loc:
        return 0.0
    try:
        return fuzz.token_set_ratio(profile_loc.lower(), job_loc.lower()) / 100.0
    except:
        return 0.0

def text_similarity_fallback(profile_texts, job_text):
    try:
        corpus = [job_text] + profile_texts
        vect = TfidfVectorizer().fit_transform(corpus)
        sim = cosine_similarity(vect[0:1], vect[1:]).flatten()
        return float(max(sim)) if sim.size else 0.0
    except:
        return 0.0

# --- main recommend ---
def recommend(profile, internships, top_k=5, weights=None):
    if weights is None:
        weights = {'skills':0.55, 'interests':0.15, 'education':0.10, 'location':0.20}

    p_skills = expand_aliases(norm_list(profile.get('skills','')))
    p_interests = expand_aliases(norm_list(profile.get('interests','')))
    p_education = (profile.get('education') or '').strip().lower()
    p_location = (profile.get('location') or '').strip().lower()

    profile_texts = [' '.join(p_skills + p_interests + [p_education, p_location])]

    scored = []
    for job in internships:
        j_skills = norm_list(job.get('skills',''))
        j_tags = norm_list(job.get('tags',''))
        j_education = (job.get('education') or '').strip().lower()
        j_location = (job.get('location') or '').strip().lower()

        s_score = skills_overlap_score(p_skills, j_skills)
        i_score = skills_overlap_score(p_interests, j_tags)
        e_score = 1.0 if (p_education and p_education in j_education) else 0.0
        l_score = fuzzy_location_score(p_location, j_location)

        fallback = 0.0
        if s_score < 0.20:
            job_text = ' '.join([job.get('title',''), job.get('tags',''), job.get('description','')])
            fallback = text_similarity_fallback(profile_texts, job_text)

        final = (weights['skills'] * max(s_score, fallback)
                 + weights['interests'] * i_score
                 + weights['education'] * e_score
                 + weights['location'] * l_score)

        factors = {
            'skills': max(s_score, fallback),
            'interests': i_score,
            'education': e_score,
            'location': l_score
        }
        top_factor = max(factors, key=factors.get)

        scored.append((final, job, top_factor))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for score, job, tf in scored[:top_k]:
        results.append({
            "id": job.get('id'),
            "title": job.get('title'),
            "company": job.get('company'),
            "location": job.get('location'),
            "skills": job.get('skills'),
            "tags": job.get('tags'),
            "stipend": job.get('stipend'),
            "score": round(float(score),4),
            "matched_by": tf
        })
    return results
