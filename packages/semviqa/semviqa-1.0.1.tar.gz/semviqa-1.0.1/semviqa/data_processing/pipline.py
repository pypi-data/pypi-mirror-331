import re
from rank_bm25 import BM25Okapi
from underthesea import word_tokenize

def preprocess_text(text: str) -> str:    
    text = re.sub(r"['\",\.\?:\!]", "", text)
    text = text.strip()
    text = " ".join(text.split())
    return text.lower()


def split_sentence(paragraph):
    context_list = []
    if paragraph[-2:] == '\n\n':
        paragraph = paragraph[:-2]

    paragraph = paragraph.rstrip()  
    start = 0
    paragraph_length = len(paragraph)

    while start < paragraph_length:  
        context = ""
        initial_start = start

        for i in range(start, paragraph_length):
            if paragraph[i] == ".":

                if i + 2 < paragraph_length and paragraph[i + 1] == "\n":
                    if paragraph[i + 2].isalpha() and paragraph[i + 2].isupper():
                        break

                if i + 1 < paragraph_length and paragraph[i + 1] == " ":
                    context += paragraph[i]
                    start = i + 1
                    break

            context += paragraph[i]

            if i == paragraph_length - 1:
                start = paragraph_length
                break

        if start == paragraph_length:
            context += paragraph[start:]
        
        context = preprocess_text(context.strip())  
        if len(context.split()) > 2:
            context_list.append(context)

        if start == initial_start:
            print("Warning: No progress detected. Exiting loop.")
            break

    return context_list

def process_data(text):
    return '. '.join(split_sentence(text))

def load_data(data):
    data_old = {}

    for i in data.index:
        if data.id[i] not in data_old.keys():
            data_old[data.id[i]] = [
                {
                    'id': data.id[i],
                    'context': data.context[i],
                    'claim': data.claim[i]
                }
            ]
        else:
            data_old[data.id[i]].append(
                    {
                        'id': data.id[i],
                        'context': data.context[i],
                        'claim': data.claim[i]
                    }
                )
    return data_old
