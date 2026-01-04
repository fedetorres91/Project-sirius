import os
from openai import OpenAI

# Paste your token here directly
os.environ["HF_TOKEN"] = "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"


class MedicalInfoService:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=os.environ["HF_TOKEN"],
        )
    def get_disease_info(self, disease):
        """Fetch medical info about a disease from HuggingFace LLM"""
        completion = self.client.chat.completions.create(
            model="HuggingFaceTB/SmolLM3-3B",
            messages=[{
                "role": "user", 
                "content": f"Answer if you can with mayo clinic info for patients. What is {disease}. Summarize in aprox 150-200 words, try to summarize, and end with a link to mayo clinic or cleveland clinic url, or the corresponding american medical academy with info for patients"
            }],
            temperature=0.6,
            top_p=0.95,
            max_tokens=512,
            extra_body={"chat_template_kwargs": {"enable_thinking": False}}
        )
        return completion.choices[0].message.content
        
    def get_medical_exams(self, file_name):
        # upload files images to analyze

        return 1

    
def main():
    disease = input("Ask about a disease? ")
    info = MedicalInfoService()
    print(info.get_disease_info(disease))

if __name__ == "__main__":
    main()

