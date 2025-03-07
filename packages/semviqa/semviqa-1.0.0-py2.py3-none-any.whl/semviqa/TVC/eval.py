import torch
import torch.nn.functional as F

def find_classify(claim, context, model, tokenizer, device):
    model.to(device)
    model.eval()

    encoding = tokenizer(
        claim,
        context,
        truncation="only_second",
        add_special_tokens=True,
        max_length=256,
        padding='max_length',
        return_attention_mask=True,
        return_token_type_ids=False,
        return_tensors='pt',
    )

    input_ids = encoding['input_ids'].to(device)
    attention_mask = encoding['attention_mask'].to(device)

    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)

    outputs = F.softmax(outputs, dim=1)
    prob, pred = torch.max(outputs, dim=1)

    return prob, pred.item()