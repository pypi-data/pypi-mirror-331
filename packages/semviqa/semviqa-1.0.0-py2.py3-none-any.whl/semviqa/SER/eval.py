import numpy as np
import torch
import torch.nn as nn
from pyvi import ViTokenizer
from rank_bm25 import BM25Okapi
from data_processing.pipline import split_sentence, preprocess_text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer

def qatc(claim, context, model_evidence_QA, tokenizer_QA, device):
    model_evidence_QA.to(device).eval() 
    inputs = tokenizer_QA(claim, context, return_tensors="pt", truncation=True)

    with torch.no_grad():
        outputs = model_evidence_QA(**inputs)

    start_index, end_index = np.argmax(outputs.start_logits.cpu().numpy()), np.argmax(outputs.end_logits.cpu().numpy())
    evidence = tokenizer_QA.decode(inputs['input_ids'][0][start_index:end_index + 1]).replace('<s>', '').replace('</s>', '')

    if not evidence or len(split_sentence(evidence)) > 1:
        return -1

    for line in split_sentence(context):
        if preprocess_text(evidence) in preprocess_text(line):
            return line

    print('error: not find evi in context')
    return evidence
    
def qatc_faster(claim, context, full_context, model_evidence_QA, tokenizer_QA, device):
    claim, context = ([claim], [context]) if isinstance(claim, str) else (claim, context)
    
    model_evidence_QA.to(device)
    model_evidence_QA.eval()

    inputs = tokenizer_QA(claim, context, return_tensors="pt", truncation=True)
    
    with torch.no_grad():
        outputs = model_evidence_QA(**inputs)

    start_index = outputs.start_logits.argmax(dim=-1).tolist()
    end_index = outputs.end_logits.argmax(dim=-1).tolist()

    evidences = tokenizer_QA.batch_decode(
        [inputs['input_ids'][0][s:e + 1] for s, e in zip(start_index, end_index)], 
        skip_special_tokens=True
    )

    true_evi = [(evi.lstrip("."), i) for i, evi in enumerate(evidences) if isinstance(evi, str) and len(preprocess_text(evi).split()) > 3]

    if len(true_evi) != 1:
        return -1  

    evidence = preprocess_text(true_evi[0][0]) 
    for line in split_sentence(full_context):
        if evidence in preprocess_text(line):
            return line  

    return -1  

def tfidf_topk(context, claim, thres=0.6, top_k=1):
    corpus = split_sentence(context)
    processed_claim = preprocess_text(ViTokenizer.tokenize(claim).lower())
    len_claim = len(processed_claim.split())
 
    corpus_pro = []
    for i, sentence in enumerate(corpus):
        sentence = preprocess_text(ViTokenizer.tokenize(sentence).lower())
        if i > 0 and 1 < len(sentence.split()) / len_claim < thres:
            sentence = f"{corpus[i-1]}. {sentence}"
        corpus_pro.append(sentence)
 
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(corpus_pro + [processed_claim])
    cosine_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()
 
    return sorted(zip(cosine_sim, corpus), reverse=True)[:top_k]


def bm25_topk(context, claim, top_k=None):
    context = split_sentence(context)
    if top_k is None:
        return context

    tokenized_context = [doc.split(' ') for doc in context]
    bm25 = BM25Okapi(tokenized_context)
    scores = bm25.get_scores(claim.split())
 
    max_score = max(scores)
    min_score = min(scores)
    normalized_scores = [
        (score - min_score) / (max_score - min_score) if max_score > min_score else 0
        for score in scores
    ]
 
    score_sentence_pairs = sorted(zip(normalized_scores, context), reverse=True)
    highest_sentence = score_sentence_pairs[:top_k] if top_k else score_sentence_pairs

    return highest_sentence

def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]  
    mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * mask_expanded, dim=1) / torch.clamp(mask_expanded.sum(dim=1), min=1e-9)

def sbert_topk(context, claim, tokenizer_sbert, model_sbert, top_k=1, device='cuda'):
    sentences = [claim] + split_sentence(context)
    
    encoded_input = tokenizer_sbert(sentences, padding=True, truncation=True, return_tensors='pt').to(device)
    
    with torch.no_grad():
        model_output = model_sbert(**encoded_input)

    sentence_embeddings = mean_pooling(model_output, encoded_input["attention_mask"])

    claim_embedding = sentence_embeddings[0].unsqueeze(0)
    cosine_sim = nn.CosineSimilarity(dim=1, eps=1e-6)
    similarities = cosine_sim(claim_embedding, sentence_embeddings[1:]).cpu().numpy()

    scaled_similarities = MinMaxScaler().fit_transform(similarities.reshape(-1, 1)).flatten()

    top_sentences = sorted(zip(scaled_similarities, sentences[1:]), reverse=True)[:top_k]
    
    return [(round(score, 2), sentence) for score, sentence in top_sentences]

def find_evidence(claim, context, model_evidence_QA, tokenizer_QA, device, thres=0.5, is_qatc_faster=False):
    evidence_tf = tfidf_topk(context, claim, top_k=1)[0]
    if evidence_tf[0] > thres:
        return evidence_tf[1]
    lines = split_sentence(context)
    tokens = context.split(' ')

    if len(tokens) <= 400: 
        evi = qatc(claim=claim, context=context, model_evidence_QA=model_evidence_QA, tokenizer_QA=tokenizer_QA, device=device)
        return evi if evi != -1 else evidence_tf[1]

    token_line = [l.split(' ') for l in lines]
    tmp_context_token, tmp_context = [], []
    evidence_list, subsentence_list = [], []

    for idx, tokens in enumerate(token_line):
        tmp_context_token += tokens
        tmp_context.append(lines[idx])

        if len(tmp_context_token) > 400 or idx == len(token_line) - 1:
            context_sub = '. '.join(tmp_context)
            if context_sub:
                subsentence_list.append(context_sub)

                if not is_qatc_faster:
                    evidence = qatc(claim=claim, context=context_sub, model_evidence_QA=model_evidence_QA, tokenizer_QA=tokenizer_QA, device=device)
                    if evidence != -1:
                        evidence_list.append(evidence)

            tmp_context_token, tmp_context = (tokens, [lines[idx]]) if len(tmp_context_token) > 400 else ([], [])

    if is_qatc_faster:
        evidence = qatc_faster(claim=[claim] * len(subsentence_list), context=subsentence_list,
                               full_context=context, model_evidence_QA=model_evidence_QA,
                               tokenizer_QA=tokenizer_QA, device=device)
        return evidence if isinstance(evidence, str) else evidence_tf[1]

    return evidence_list[0] if len(evidence_list) == 1 else evidence_tf[1]