import os
from openai import OpenAI
import tkinter as tk
from tkinter import scrolledtext, messagebox

#Script is based on fine-tuned model, will not work properly without changing it to User's own fine-tuned model. Generate it at fine_tune.py and change model below.

oai_key = os.getenv('OPENAI_API_KEY')
if not oai_key:
    raise ValueError("OPENAI API KEY was not set")

client = OpenAI(api_key=oai_key)

SEGMENTS = [
    "Verification Builds",
    "Summary",
    "Repro Steps",
    "Observed Results",
    "Expected Results"
]
PROMPTS = {
    "Verification Builds": {
        "text": "Verification Builds:"
    },
    "Summary": {
        "text": "Summary:"
    },
    "Repro Steps": {
        "text": "Repro Steps:"
    },
    "Observed Results": {
        "text": "Observed Results:"
    },
    "Expected Results": {
        "text": "Expected Results:"
    }
}

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

    def call_ai(self, prompt, history):
        messages = [{"role": "system", "content": "You are a helpful assistant for generating bug tickets."}]

        for seg, text in history:
            messages.append({"role": "assistant", "content": f"{seg}: {text}"})

        messages.append({"role": "user", "content": prompt})

        resp = client.chat.completions.create(
            model="ft:gpt-3.5-turbo-0125:personal::C10DdGOL", #change to your fine-tuned model
            messages=messages,
            temperature=0.3
        )
        answer = resp.choices[0].message.content.strip()
        tokens_used = resp.usage.total_tokens

        return answer, tokens_used

    def generate_ticket(self):
        full_desc = self.desc_input.get('1.0', tk.END).strip()
        if not full_desc:
            messagebox.showwarning("Input needed", "Please enter the full bug descriptiob")
            return

        history = []
        results = []
        
        for segment in SEGMENTS:
            prompt_text = PROMPTS[segment]["text"]

            prompt = (
                f"{prompt_text}\n\n"
                f"Full Bug Description: {full_desc}"
            )
            answer, tokens = self.call_ai(prompt, history)
            print(f"Segment '{segment}' used {tokens} tokens")
            history.append((segment, answer))
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
