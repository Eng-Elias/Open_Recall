from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Initialize the summarization components
model = None
tokenizer = None

def get_summarizer():
    """
    Lazy initialization of the deepseek-r1 model to avoid loading it
    until it's actually needed.
    """
    global model, tokenizer
    if model is None or tokenizer is None:
        try:
            # Initialize the deepseek-r1 model and tokenizer
            model_name = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"  # Using the 7B model for better performance
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,  # Use half precision to save memory
                device_map="auto"  # Automatically choose the best device
            )
            return True
        except Exception as e:
            print(f"Error initializing deepseek-r1 model: {e}")
            return False
    return True

def generate_summary(text, max_length=100, min_length=30):
    """
    Generate a summary for the given text using the deepseek-r1 model.
    
    Args:
        text (str): The text to summarize
        max_length (int): Maximum length of the summary
        min_length (int): Minimum length of the summary
        
    Returns:
        str: The generated summary or empty string if summarization fails
    """
    if not text or len(text.strip()) < min_length:
        return ""
        
    try:
        # Limit input text length to avoid OOM errors
        # text = text[:4000]  # Limit input text length
        
        # Initialize the model and tokenizer if not already done
        if not get_summarizer():
            return ""
        
        # Create prompt for summarization
        prompt = f"""
The following text was extracted using OCR from a screenshot of a computer screen.
Generate a short, concise summary that describes the content or action shown in the screenshot.
Focus on what is being displayed or what action is taking place.

Text: {text}

Summary:"""
        
        # Generate summary
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_length,
                min_new_tokens=min_length,
                temperature=0.3,  # Lower temperature for more focused output
                do_sample=True,
                top_p=0.95,
                top_k=50,
                repetition_penalty=1.2
            )
        
        # Decode the generated summary
        summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        summary = summary.replace(prompt, "")
        if '</think>' in summary:
            summary = summary.split('</think>')[1].strip()
            
        
        return summary
    except Exception as e:
        print(f"Error generating summary with deepseek-r1: {e}")
        return ""
