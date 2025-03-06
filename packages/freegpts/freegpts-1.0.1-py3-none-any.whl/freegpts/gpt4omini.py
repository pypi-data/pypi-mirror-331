import requests

def answer(question, role="user"):
    dictToSend = {"model": "gpt-4o-mini", "request": {"messages": [{"role": role, "content": question}]}}
    res = requests.post('http://api.onlysq.ru/ai/v2', json=dictToSend)
    response = res.json()
    return response['answer']

