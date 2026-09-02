"""
Lightweight LongCat-Video Demo for Hugging Face Spaces
Optimized for faster inference and lower resource usage
"""
import gradio as gr
import torch
from diffusers import DiffusionPipeline
import spaces

MODEL_ID = "meituan-longcat/LongCat-Video"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Cache model globally to avoid reloading
_pipe = None

def load_model():
    global _pipe
    if _pipe is None:
        _pipe = DiffusionPipeline.from_pretrained(
            MODEL_ID,
            torch_dtype=torch.float16,
            variant="fp16"
        )
        _pipe = _pipe.to(DEVICE)
        _pipe.enable_attention_slicing()
    return _pipe

@spaces.GPU(duration=120)
def generate_video(prompt, negative_prompt, num_frames, height, width):
    """Generate video from text prompt"""
    try:
        pipe = load_model()

        with torch.no_grad():
            output = pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_frames=num_frames,
                height=height,
                width=width,
                num_inference_steps=30,
                guidance_scale=7.5,
            )

        return output.frames[0]
    except Exception as e:
        raise gr.Error(f"Generation failed: {str(e)}")

# Create interface
with gr.Blocks(title="LongCat-Video", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🎬 LongCat-Video Demo

    Generate stunning videos from text descriptions using LongCat-Video, a 13.6B parameter
    foundational video generation model.

    **[Model Card](https://huggingface.co/meituan-longcat/LongCat-Video)** |
    **[Paper](https://arxiv.org/abs/2510.22200)** |
    **[Project Page](https://meituan-longcat.github.io/LongCat-Video/)**
    """)

    with gr.Row():
        with gr.Column():
            prompt = gr.Textbox(
                label="📝 Prompt",
                placeholder="Describe the video you want to generate...",
                lines=3,
                value="A serene lake with mountains in the background at sunset"
            )

            neg_prompt = gr.Textbox(
                label="❌ Negative Prompt (optional)",
                placeholder="What to avoid...",
                lines=2
            )

            with gr.Row():
                num_frames = gr.Slider(
                    label="🎞️ Frames",
                    minimum=8,
                    maximum=32,
                    value=16,
                    step=8
                )

            with gr.Row():
                height = gr.Slider(
                    label="📏 Height",
                    minimum=256,
                    maximum=720,
                    value=480,
                    step=64
                )
                width = gr.Slider(
                    label="📏 Width",
                    minimum=256,
                    maximum=1280,
                    value=848,
                    step=64
                )

            generate_btn = gr.Button("🚀 Generate Video", size="lg", variant="primary")

        with gr.Column():
            video_output = gr.Video(label="Generated Video", format="mp4")

    gr.Examples(
        examples=[
            ["A sunset over calm ocean waves", "", 16, 480, 848],
            ["A forest with sunlight filtering through trees", "", 16, 480, 848],
            ["A modern city at night with neon lights", "", 16, 480, 848],
            ["A field of flowers swaying in the wind", "", 16, 480, 848],
        ],
        inputs=[prompt, neg_prompt, num_frames, height, width]
    )

    gr.Markdown("""
    ### ℹ️ Tips
    - **Be specific** in your description
    - **Avoid artifacts**: Use negative prompts to exclude unwanted elements
    - **Frame count**: 8-16 frames for short clips, 24-32 for longer
    - **Resolution**: Lower resolution = faster generation
    - **GPU**: Requires NVIDIA GPU with 12GB+ VRAM
    """)

    generate_btn.click(
        fn=generate_video,
        inputs=[prompt, neg_prompt, num_frames, height, width],
        outputs=video_output
    )

if __name__ == "__main__":
    demo.launch()
