from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import os
from open_recall.utils.settings import settings_manager
from huggingface_hub import snapshot_download, hf_hub_download
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize the summarization components
model = None
tokenizer = None
current_model_name = None

# Define available models
AVAILABLE_MODELS = {
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B": {
        "name": "DeepSeek R1 1.5B",
        "description": "Lightweight reasoning model for efficient summarization"
    },
    "Qwen/Qwen2.5-0.5B": {
        "name": "Qwen 2.5 - 0.5B",
        "description": "Smaller model with faster inference"
    }
}

def is_model_downloaded(model_name):
    """
    Check if the model is already downloaded in the Hugging Face cache.
    
    Args:
        model_name (str): The name of the model to check
        
    Returns:
        bool: True if the model is downloaded, False otherwise
    """
    try:
        # Get the cache directory
        cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "hub")
        
        # Try a more reliable method using hf_hub_download to check if model exists
        try:
            # Try to download the model's config file which is small and should exist for all models
            hf_hub_download(
                repo_id=model_name,
                filename="config.json",
                local_files_only=True  # Don't actually download, just check if it exists
            )
            logger.info(f"Model {model_name} is already downloaded")
            return True
        except Exception:
            # If local_files_only=True raises an exception, the model isn't downloaded
            logger.info(f"Model {model_name} is not downloaded")
            return False
    except Exception as e:
        logger.error(f"Error checking if model is downloaded: {e}")
        return False

def download_model(model_name):
    """
    Download a model from Hugging Face.
    
    Args:
        model_name (str): The name of the model to download
        
    Returns:
        bool: True if the download was successful, False otherwise
    """
    try:
        logger.info(f"Starting download of model: {model_name}")
        
        # Use snapshot_download to get the entire model
        snapshot_download(
            repo_id=model_name,
            local_dir=None,  # Use default cache dir
            local_dir_use_symlinks=False  # Actual files, not symlinks
        )
        
        logger.info(f"Successfully downloaded model: {model_name}")
        return True
    except Exception as e:
        logger.error(f"Error downloading model {model_name}: {e}")
        return False

def get_summarizer():
    """
    Lazy initialization of the summarization model based on settings.
    Checks if the model is downloaded and downloads it if necessary.
    """
    global model, tokenizer, current_model_name
    
    # Get the model name from settings
    model_name = settings_manager.get_setting("summarization_model", "Qwen/Qwen2.5-0.5B")
    
    # If the model is already loaded and it's the same as the one in settings, return
    if model is not None and tokenizer is not None and current_model_name == model_name:
        return True
    
    # If a different model was previously loaded, unload it to free memory
    if model is not None and current_model_name != model_name:
        logger.info(f"Unloading previous model: {current_model_name}")
        # Delete the model and tokenizer to free up memory
        del model
        del tokenizer
        # Force garbage collection to free up memory
        import gc
        gc.collect()
        # Clear CUDA cache if available
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        model = None
        tokenizer = None
    
    try:
        # Check if the model is downloaded
        if not is_model_downloaded(model_name):
            logger.info(f"Model {model_name} not found locally. Attempting to download...")
            # Download the model
            if not download_model(model_name):
                logger.error(f"Failed to download model: {model_name}")
                return False
            logger.info(f"Model {model_name} downloaded successfully")
        
        # Initialize the model and tokenizer
        logger.info(f"Loading model: {model_name}")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,  # Use half precision to save memory
            device_map="auto",  # Automatically choose the best device
            low_cpu_mem_usage=True  # Optimize for lower memory usage
        )
        current_model_name = model_name
        logger.info(f"Model {model_name} loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing model {model_name}: {e}")
        return False

def get_available_models():
    """
    Get a list of available models with their download status.
    
    Returns:
        list: List of model information dictionaries
    """
    models = []
    for model_id, model_info in AVAILABLE_MODELS.items():
        models.append({
            "id": model_id,
            "name": model_info["name"],
            "description": model_info["description"],
            "downloaded": is_model_downloaded(model_id)
        })
    return models

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

def generate_search_results_summary(text, max_length=300, min_length=100):
    """
    Generate a summary specifically for search results, which may contain multiple screenshots.
    
    Args:
        text (str): The text to summarize
        max_length (int, optional): The maximum length of the summary. Defaults to 300.
        min_length (int, optional): The minimum length of the summary. Defaults to 100.
        
    Returns:
        str: The generated summary
    """
    if not get_summarizer():
        return "Summarization model not initialized. Please check your settings."
    
    try:
        global model, tokenizer
        
        # Create prompt for summarization
        prompt = f"""
The following text contains information about multiple screenshots captured from a user's computer.
Generate a concise summary (maximum 300 words) that synthesizes the main activities, applications used, 
and content viewed across these screenshots. Format the summary as a list of bullet points, with each point 
highlighting a key insight, pattern, or important piece of information. Focus on identifying:

- Main applications and websites used
- Key topics or subjects being worked on
- Recurring themes or patterns across screenshots
- Important information that appears frequently

Text: {text}

Summary (as bullet points):
"""
        
        # Generate summary
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        outputs = model.generate(
            inputs.input_ids,
            max_new_tokens=max_length,
            min_new_tokens=min_length,
            temperature=0.7,
            do_sample=True,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id
        )
        
        # Decode the generated summary
        summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        summary = summary.replace(prompt, "")
        if '</think>' in summary:
            summary = summary.split('</think>')[1].strip()
        
        return summary.strip()
    except Exception as e:
        logger.error(f"Error generating search results summary: {e}")
        return "Failed to generate summary. Please try again later."
