from gpt4all import GPT4All
from process_documents import extract_text_from_pdf

text = extract_text_from_pdf(r"C:\Users\lucas\Desktop\Datasets\BDD_Helico\4.a. MANUEL SGS FAMA SCHOOL -  01-03-17  -  APRES CORRECTION.pdf")

text = text[0:10000]
print(len(text))

p = r"C:\Users\lucas\aait_store\Models\NLP\Falcon3-7B-Instruct-q6_k.gguf"
p = r"C:\Users\lucas\aait_store\Models\NLP\solar-10.7b-instruct-v1.0.Q6_K.gguf"
p = r"C:\Users\lucas\aait_store\Models\NLP\Qwen2.5.1-Coder-7B-Instruct-Q6_K.gguf"
p = r"C:\Users\lucas\aait_store\Models\NLP\Qwen2.5-Dyanka-7B-Preview.Q6_K.gguf"

model = GPT4All(p, device="cuda", n_ctx=30000)

a = model.generate(fr"### User: Résume ce texte :\n\n{text}\n\n\n\n### Assistant:", max_tokens=4096)

print(a)
