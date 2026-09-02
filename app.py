import gradio as gr
import torch
import numpy as np
from diffusers import DiffusionPipeline
from PIL import Image
import spaces
import os
from pathlib import Path

# Configuration
MODEL_ID = "meituan-longcat/LongCat-Video"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Load model with caching
@spaces.GPU(duration=120)
def generate_video(prompt, negative_prompt="", num_frames=16, height=720, width=1280, num_inference_steps=30, guidance_scale=7.5):
    """
    Generate video from text prompt using LongCat-Video model
    """
    try:
        # Initialize pipeline
        pipe = DiffusionPipeline.from_pretrained(
            MODEL_ID,
            torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
            variant="fp16" if DEVICE == "cuda" else None
        )
        pipe = pipe.to(DEVICE)

        # Enable memory efficient attention
        if hasattr(pipe, "enable_attention_slicing"):
            pipe.enable_attention_slicing()

        # Generate video frames
        with torch.no_grad():
            output = pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_frames=num_frames,
                height=height,
                width=width,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
            )

        # Return frames as video
        frames = output.frames[0]  # Get first (and only) batch
        return frames

    except Exception as e:
        raise gr.Error(f"Error generating video: {str(e)}")

@spaces.GPU(duration=60)
def generate_from_image(image, prompt, negative_prompt="", num_frames=16, height=720, width=1280):
    """
    Generate video from image using LongCat-Video model
    """
    try:
        pipe = DiffusionPipeline.from_pretrained(
            MODEL_ID,
            torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
            variant="fp16" if DEVICE == "cuda" else None
        )
        pipe = pipe.to(DEVICE)

        if hasattr(pipe, "enable_attention_slicing"):
            pipe.enable_attention_slicing()

        # Prepare image
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image.astype('uint8'))
        image = image.resize((width, height))

        with torch.no_grad():
            output = pipe(
                prompt=prompt,
                image=image,
                negative_prompt=negative_prompt,
                num_frames=num_frames,
                height=height,
                width=width,
            )

        frames = output.frames[0]
        return frames

    except Exception as e:
        raise gr.Error(f"Error generating video: {str(e)}")

@spaces.GPU(duration=60)
def continue_video(video_path, prompt, num_frames=16):
    """
    Continue existing video using LongCat-Video model
    """
    try:
        import av

        pipe = DiffusionPipeline.from_pretrained(
            MODEL_ID,
            torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
            variant="fp16" if DEVICE == "cuda" else None
        )
        pipe = pipe.to(DEVICE)

        # Read video frames
        container = av.open(video_path)
        frames = []
        for frame in container.decode(video=0):
            frames.append(frame.to_image())
            if len(frames) >= 8:  # Use last 8 frames as context
                break

        with torch.no_grad():
            output = pipe(
                prompt=prompt,
                video=frames,
                num_frames=num_frames,
            )

        result_frames = output.frames[0]
        return result_frames

    except Exception as e:
        raise gr.Error(f"Error continuing video: {str(e)}")

def create_interface():
    """Create Gradio interface"""

    with gr.Blocks(title="LongCat-Video Demo", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # 🎬 LongCat-Video Demo

        Generate, extend, and continue videos with **LongCat-Video** - a 13.6B parameter foundational video generation model.

        **Features:**
        - 🎥 **Text-to-Video**: Generate videos from text prompts
        - 🖼️ **Image-to-Video**: Extend images into dynamic videos
        - 🔄 **Video Continuation**: Seamlessly continue existing videos
        - ⚡ **Efficient Inference**: Generates 720p, 30fps videos

        **Model:** [meituan-longcat/LongCat-Video](https://huggingface.co/meituan-longcat/LongCat-Video)
        """)

        with gr.Tabs():
            # Text-to-Video Tab
            with gr.Tab("🎬 Text-to-Video"):
                with gr.Row():
                    with gr.Column():
                        prompt_txt = gr.Textbox(
                            label="Prompt",
                            placeholder="Describe the video you want to generate...",
                            lines=3
                        )
                        neg_prompt_txt = gr.Textbox(
                            label="Negative Prompt",
                            placeholder="What to avoid in the video...",
                            lines=2
                        )

                        with gr.Row():
                            num_frames_txt = gr.Slider(
                                label="Number of Frames",
                                minimum=8,
                                maximum=64,
                                value=16,
                                step=8
                            )
                            guidance_scale = gr.Slider(
                                label="Guidance Scale",
                                minimum=1,
                                maximum=15,
                                value=7.5,
                                step=0.5
                            )

                        with gr.Row():
                            height_txt = gr.Slider(
                                label="Height",
                                minimum=256,
                                maximum=1080,
                                value=720,
                                step=64
                            )
                            width_txt = gr.Slider(
                                label="Width",
                                minimum=256,
                                maximum=1280,
                                value=1280,
                                step=64
                            )

                        generate_btn_txt = gr.Button("🎬 Generate Video", size="lg", variant="primary")

                    with gr.Column():
                        video_output_txt = gr.Video(
                            label="Generated Video",
                            format="mp4"
                        )

                gr.Examples(
                    examples=[
                        "A beautiful sunset over a calm ocean with waves",
                        "A futuristic city with flying cars and neon lights",
                        "A forest with deer walking through sunlight",
                        "A cozy cabin in a snowy mountain landscape",
                    ],
                    inputs=[prompt_txt]
                )

                generate_btn_txt.click(
                    fn=generate_video,
                    inputs=[prompt_txt, neg_prompt_txt, num_frames_txt, height_txt, width_txt, gr.Slider(3, 50, value=30, step=1), guidance_scale],
                    outputs=video_output_txt
                )

            # Image-to-Video Tab
            with gr.Tab("🖼️ Image-to-Video"):
                with gr.Row():
                    with gr.Column():
                        image_input = gr.Image(
                            label="Input Image",
                            type="pil"
                        )
                        prompt_img = gr.Textbox(
                            label="Prompt",
                            placeholder="Describe how the image should move...",
                            lines=3
                        )
                        neg_prompt_img = gr.Textbox(
                            label="Negative Prompt",
                            lines=2
                        )

                        num_frames_img = gr.Slider(
                            label="Number of Frames",
                            minimum=8,
                            maximum=64,
                            value=16,
                            step=8
                        )

                        generate_btn_img = gr.Button("🎬 Generate Video", size="lg", variant="primary")

                    with gr.Column():
                        video_output_img = gr.Video(
                            label="Generated Video",
                            format="mp4"
                        )

                generate_btn_img.click(
                    fn=generate_from_image,
                    inputs=[image_input, prompt_img, neg_prompt_img, num_frames_img],
                    outputs=video_output_img
                )

            # Video Continuation Tab
            with gr.Tab("🔄 Video Continuation"):
                with gr.Row():
                    with gr.Column():
                        video_input = gr.Video(
                            label="Input Video",
                            format="mp4"
                        )
                        prompt_cont = gr.Textbox(
                            label="Prompt",
                            placeholder="How should the video continue?",
                            lines=3
                        )

                        num_frames_cont = gr.Slider(
                            label="Number of New Frames",
                            minimum=8,
                            maximum=64,
                            value=16,
                            step=8
                        )

                        generate_btn_cont = gr.Button("🔄 Continue Video", size="lg", variant="primary")

                    with gr.Column():
                        video_output_cont = gr.Video(
                            label="Continued Video",
                            format="mp4"
                        )

                generate_btn_cont.click(
                    fn=continue_video,
                    inputs=[video_input, prompt_cont, num_frames_cont],
                    outputs=video_output_cont
                )

            # Info Tab
            with gr.Tab("ℹ️ About"):
                gr.Markdown("""
                ## LongCat-Video Overview

                **LongCat-Video** is a foundational video generation model with 13.6B parameters,
                delivering strong performance across multiple video generation tasks.

                ### Key Features
                - 🌟 **Unified Architecture**: Handles Text-to-Video, Image-to-Video, and Video-Continuation tasks
                - 🎬 **Long Video Generation**: Native support for minute-long videos without quality degradation
                - ⚡ **Efficient Inference**: Generates 720p, 30fps videos using coarse-to-fine strategy
                - 🏆 **RLHF Optimized**: Powered by multi-reward Group Relative Policy Optimization (GRPO)

                ### Model Variants
                - **LongCat-Video**: Foundational model for general video generation
                - **LongCat-Video-Avatar**: Audio-driven human video generation (Wav2Vec2)
                - **LongCat-Video-Avatar-1.5**: Upgraded avatar model with Whisper-Large v3

                ### Resources
                - 📄 [Technical Report](https://arxiv.org/abs/2510.22200)
                - 🤗 [Model on Hugging Face](https://huggingface.co/meituan-longcat/LongCat-Video)
                - 📺 [Project Page](https://meituan-longcat.github.io/LongCat-Video/)
                - 💬 [Discord Community](https://discord.gg/EXsG52D8SW)

                ### System Requirements
                - GPU with at least 8GB VRAM (16GB+ recommended)
                - CUDA 12.4+ for GPU acceleration
                - ~25GB disk space for model weights

                ### Tips for Best Results
                1. **Clear Prompts**: Be specific about visual details
                2. **Negative Prompts**: Specify what to avoid
                3. **Frame Count**: More frames = longer video (8-64 recommended)
                4. **Guidance Scale**: Higher values (7-10) follow prompt more closely
                5. **Resolution**: Higher resolution needs more VRAM
                """)

    return demo

if __name__ == "__main__":
    demo = create_interface()
    demo.launch(share=True)
