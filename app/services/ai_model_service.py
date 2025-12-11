import torch
import torchvision.transforms as T
from PIL import Image
from torchvision.transforms.functional import InterpolationMode
from transformers import AutoModel, AutoTokenizer
from typing import Optional

from app.config.settings import Config

IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)


class AIModelService:
    """Service for AI model operations"""

    _model: Optional[AutoModel] = None
    _tokenizer: Optional[AutoTokenizer] = None
    _device: Optional[str] = None
    _dtype: Optional[torch.dtype] = None

    @classmethod
    def initialize_model(cls):
        """Initialize model and tokenizer (singleton pattern)"""
        if cls._model is not None:
            return

        # Determine device
        cls._device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Initializing model on device: {cls._device}")

        # Set dtype
        cls._dtype = torch.bfloat16 if cls._device == "cuda" else torch.float32

        # Load model
        cls._model = AutoModel.from_pretrained(
            Config.MODEL_NAME,
            torch_dtype=cls._dtype,
            low_cpu_mem_usage=True,
            trust_remote_code=True,
            use_flash_attn=False,
        ).eval()

        # Move to device
        if cls._device == "cuda":
            cls._model = cls._model.cuda()

        # Load tokenizer
        cls._tokenizer = AutoTokenizer.from_pretrained(
            Config.MODEL_NAME,
            trust_remote_code=True,
            use_fast=False
        )

        print("Model initialized successfully!")

    @classmethod
    def extract_text_from_image(cls, image_path: str) -> str:
        """
        Extract text from image using AI model

        Args:
            image_path: Path to the image file

        Returns:
            Extracted text from the image
        """
        # Ensure model is initialized
        cls.initialize_model()

        # Load and preprocess image
        pixel_values = cls._load_image(image_path).to(cls._dtype)

        # Move to device
        if cls._device == "cuda":
            pixel_values = pixel_values.cuda()

        # Generation config
        generation_config = dict(
            max_new_tokens=Config.MAX_NEW_TOKENS,
            do_sample=False,
            num_beams=Config.NUM_BEAMS,
            repetition_penalty=Config.REPETITION_PENALTY
        )

        # Question prompt
        question = '<image>\nTrích xuất giá trị của các cột tên hàng, số lượng, đơn giá, thành tiền của các sản phẩm trong hóa đơn.'

        # Get response
        response, _ = cls._model.chat(
            cls._tokenizer,
            pixel_values,
            question,
            generation_config,
            history=None,
            return_history=True
        )

        print(f'User: {question}\nAssistant: {response}')
        return response

    @classmethod
    def _build_transform(cls, input_size: int):
        """Build image transformation pipeline"""
        transform = T.Compose([
            T.Lambda(lambda img: img.convert('RGB') if img.mode != 'RGB' else img),
            T.Resize((input_size, input_size), interpolation=InterpolationMode.BICUBIC),
            T.ToTensor(),
            T.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
        ])
        return transform

    @classmethod
    def _find_closest_aspect_ratio(cls, aspect_ratio, target_ratios, width, height, image_size):
        """Find closest aspect ratio from target ratios"""
        best_ratio_diff = float('inf')
        best_ratio = (1, 1)
        area = width * height

        for ratio in target_ratios:
            target_aspect_ratio = ratio[0] / ratio[1]
            ratio_diff = abs(aspect_ratio - target_aspect_ratio)
            if ratio_diff < best_ratio_diff:
                best_ratio_diff = ratio_diff
                best_ratio = ratio
            elif ratio_diff == best_ratio_diff:
                if area > 0.5 * image_size * image_size * ratio[0] * ratio[1]:
                    best_ratio = ratio

        return best_ratio

    @classmethod
    def _dynamic_preprocess(cls, image, min_num=1, max_num=12, image_size=448, use_thumbnail=False):
        """Dynamically preprocess image"""
        orig_width, orig_height = image.size
        aspect_ratio = orig_width / orig_height

        # Calculate target ratios
        target_ratios = set(
            (i, j) for n in range(min_num, max_num + 1)
            for i in range(1, n + 1)
            for j in range(1, n + 1)
            if i * j <= max_num and i * j >= min_num
        )
        target_ratios = sorted(target_ratios, key=lambda x: x[0] * x[1])

        # Find closest aspect ratio
        target_aspect_ratio = cls._find_closest_aspect_ratio(
            aspect_ratio, target_ratios, orig_width, orig_height, image_size
        )

        # Calculate target dimensions
        target_width = image_size * target_aspect_ratio[0]
        target_height = image_size * target_aspect_ratio[1]
        blocks = target_aspect_ratio[0] * target_aspect_ratio[1]

        # Resize and split image
        resized_img = image.resize((target_width, target_height))
        processed_images = []

        for i in range(blocks):
            box = (
                (i % (target_width // image_size)) * image_size,
                (i // (target_width // image_size)) * image_size,
                ((i % (target_width // image_size)) + 1) * image_size,
                ((i // (target_width // image_size)) + 1) * image_size
            )
            split_img = resized_img.crop(box)
            processed_images.append(split_img)

        assert len(processed_images) == blocks

        if use_thumbnail and len(processed_images) != 1:
            thumbnail_img = image.resize((image_size, image_size))
            processed_images.append(thumbnail_img)

        return processed_images

    @classmethod
    def _load_image(cls, image_file, input_size=448, max_num=None):
        """Load and preprocess image"""
        if max_num is None:
            max_num = Config.MAX_NUM_IMAGES

        image = Image.open(image_file).convert('RGB')
        transform = cls._build_transform(input_size=input_size)
        images = cls._dynamic_preprocess(image, image_size=input_size, use_thumbnail=True, max_num=max_num)
        pixel_values = [transform(image) for image in images]
        pixel_values = torch.stack(pixel_values)
        return pixel_values
