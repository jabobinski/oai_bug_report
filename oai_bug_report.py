import os
from openai import OpenAI
import tkinter as tk
from tkinter import scrolledtext, messagebox

#Script is based on fine-tuned model, will not work properly without changing it to User's own fine-tuned model. Generate it at fine_tune.py and change model below.

oai_key = os.getenv('OPENAI_API_KEY')
if not oai_key:
    raise ValueError("OPENAI API KEY was not set")

client = OpenAI(api_key=oai_key)

FINETUNED_MODEL = "ft:gpt-3.5-turbo-0125:personal::C10DdGOL" #change to your fine-tuned model

SEGMENTS = [
    "Summary",
    "Repro Steps",
    "Observed Results",
    "Expected Results"
]

class BugTicketApp:
    def __init__(self, master):
        self.master = master
        master.title("Bug Ticket AI")
        
        tk.Label(master, text="Full Bug Description:").pack(anchor='w')
        self.desc_input = scrolledtext.ScrolledText(master, height=8)
        self.desc_input.pack(fill='both', expand=True)

        self.generate_btn = tk.Button(master, text="Generate Ticket", command=self.generate_ticket)
        self.generate_btn.pack(pady=5)

        tk.Label(master, text="Generated Bug Ticket:").pack(anchor='w')
        self.output = scrolledtext.ScrolledText(master, height=16)
        self.output.pack(fill='both', expand=True)

    def call_ai(self, segment, full_desc):
        messages = [
            {"role": "system", "content": "Bug ticket generator"},
            {"role": "user", "content": (
            f"Write ONLY the {segment} part for the bug described below."
            f"Do not include any other sections or text out of this range."
            f"Keep the response short and complete."
            f"End with '[END OF {segment}]'.\n\n"
            f"Bug Description:\n{full_desc}"
        )}
        ]

        resp = client.chat.completions.create(
            model=FINETUNED_MODEL,
            messages=messages,
            temperature=0.1
        )
        answer = resp.choices[0].message.content.strip()
        answer = answer.replace(f"[END OF {segment}]", "").strip()
        tokens_used = resp.usage.total_tokens
        return answer, tokens_used

    def generate_ticket(self):
        full_desc = self.desc_input.get('1.0', tk.END).strip()
        if not full_desc:
            messagebox.showwarning("Input needed", "Please enter the full bug description")
            return

        results = []

        for segment in SEGMENTS:
            answer, tokens = self.call_ai(segment, full_desc)
            print(f"Segment '{segment}' used {tokens} tokens")
            results.append((segment, answer))

        ticket_text = ""
        for seg, text in results:
            ticket_text += f"{seg}\n{text}\n\n"

        self.output.delete('1.0', tk.END)
        self.output.insert(tk.END, ticket_text)

if __name__ == '__main__':
    root = tk.Tk()
    app = BugTicketApp(root)
    root.mainloop()