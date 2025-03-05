from liteauto import google, parse, wlanswer

from litegen import LLM

def llm(query,
        api_key='ollama',
        model="hf.co/bartowski/DeepSeek-R1-Distill-Qwen-1.5B-GGUF:Q8_0"):
    llm = LLM(api_key=api_key)
    for _ in llm.completion(model=model, prompt=query,
                            stream=True):
        if _:
            yield _.choices[0].delta.content

def search_ai(query):
    responses = [x for x in parse(google(query,max_urls=3)) if x.content]
    res = [(r.url,wlanswer(r.content,query,k=3)) for r in responses]
    for x in llm("\n".join([r[1] for  r in res]) + f" \n Quickly think about the above results and write a summary of the above results for question : {query}"):
        yield x
    yield "\n"+"-"*20+"\n".join(r[0] for r in res)

if __name__ == '__main__':
    for x in search_ai('what is ai agents'):
        print(x,end="",flush=True)
