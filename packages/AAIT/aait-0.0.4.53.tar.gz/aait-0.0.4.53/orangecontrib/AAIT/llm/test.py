from gpt4all import GPT4All
from process_documents import extract_text_from_pdf

text = extract_text_from_pdf(r"C:\Users\lucas\Desktop\Datasets\BDD_Helico\4.a. MANUEL SGS FAMA SCHOOL -  01-03-17  -  APRES CORRECTION.pdf")

text = text[0:3000] #doesn't change occupied RAM
print(len(text))

# p = r"C:\Users\lucas\aait_store\Models\NLP\Falcon3-7B-Instruct-q6_k.gguf"
# p = r"C:\Users\lucas\aait_store\Models\NLP\solar-10.7b-instruct-v1.0.Q6_K.gguf"
# p = r"C:\Users\lucas\aait_store\Models\NLP\Qwen2.5.1-Coder-7B-Instruct-Q6_K.gguf"
p = r"C:\Users\lucas\aait_store\Models\NLP\Qwen2.5-Dyanka-7B-Preview.Q6_K.gguf"

model = GPT4All(p, device="cuda", n_ctx=30000, allow_download=False)

stop_sequences = ["<|endoftext|>", "### User"]
answer = ""

for token in model.generate(fr"### User: Résume ce texte :\n\n{text}\n\n\n\n Arrête-toi après le résumé.### Assistant:",
                            max_tokens=4096, streaming=True, temp=0):
    answer += token
    print(token, end="")
    if any(seq in answer for seq in stop_sequences):  # Check only in the rolling buffer
        break

for stop in stop_sequences:
    answer = answer.replace(stop, "")

print(answer)



### Qwen
# VRAM = a*n_ctx + b
# y = 0,1109x + 5660

# import subprocess
# import os
#
# # Path to your index.html
# html_path = r"C:\Users\lucas\Documents\Projets\KNDS\Interface\index.html"
#
# edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
#
# # Run the Edge browser with the HTML file
# subprocess.run([edge_path, html_path])