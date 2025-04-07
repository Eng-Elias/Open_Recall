from typing import Tuple

import numpy as np
from doctr.models import ocr_predictor


class OCRProcessor:
    def __init__(self):
        self.model = ocr_predictor(
            pretrained=True, det_arch="db_mobilenet_v3_large", reco_arch="crnn_mobilenet_v3_large"
        )

    def process_image(self, image: np.ndarray) -> Tuple[str, float]:
        """
        Process image with OCR and return extracted text and confidence score

        Args:
            image: numpy array of the image in RGB format

        Returns:
            tuple: (extracted_text, confidence_score)
        """
        try:
            # Process image with OCR
            result = self.model([image])

            text = ""
            confidence_scores = []

            # Extract text and confidence scores
            for page in result.pages:
                for block in page.blocks:
                    for line in block.lines:
                        for word in line.words:
                            text += word.value + " "
                            confidence_scores.append(word.confidence)
                        text += "\n"
                    text += "\n"

            # Calculate average confidence
            confidence_score = np.mean(confidence_scores) if confidence_scores else 0.0

            print(f"Extracted text length: {len(text)}")
            print(f"Confidence score: {confidence_score}")

            return text.strip(), float(confidence_score)

        except Exception as e:
            print(f"OCR processing failed: {e}")
            return "", 0.0


# Global OCR processor instance
ocr_processor = OCRProcessor()


def process_image_ocr(image: np.ndarray) -> Tuple[str, float]:
    """
    Wrapper function to process image with OCR

    Args:
        image: numpy array of the image in RGB format

    Returns:
        tuple: (extracted_text, confidence_score)
    """
    return ocr_processor.process_image(image)
