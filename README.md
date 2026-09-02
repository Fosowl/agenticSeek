---
title: LongCat-Video Demo
emoji: 🎬
colorFrom: purple
colorTo: pink
sdk: gradio
sdk_version: 4.36.1
app_file: app.py
pinned: false
hardware: gpu-a100-large
---

# LongCat-Video Demo

🎬 Generate, extend, and continue videos with **LongCat-Video** - a 13.6B parameter foundational video generation model.

## Features

- 🎥 **Text-to-Video**: Generate videos from text prompts  
- 🖼️ **Image-to-Video**: Extend images into dynamic videos  
- 🔄 **Video Continuation**: Seamlessly continue existing videos  
- ⚡ **Efficient Inference**: Generates 720p, 30fps videos  

## About LongCat-Video

LongCat-Video is a state-of-the-art video generation model developed by Meituan. It unifies multiple video generation tasks within a single architecture and excels at generating high-quality, long-form videos.

### Key Capabilities

- **Unified Architecture**: Handles Text-to-Video, Image-to-Video, and Video-Continuation with a single model
- **Long Video Generation**: Natively supports minute-long videos without color drifting or quality degradation
- **Efficient Inference**: Uses coarse-to-fine generation strategy along temporal and spatial axes
- **High Quality**: Powered by multi-reward Group Relative Policy Optimization (GRPO)

### Model Variants

| Model | Description | Link |
|-------|-------------|------|
| LongCat-Video | Foundational model for general video generation | [🤗 HF](https://huggingface.co/meituan-longcat/LongCat-Video) |
| LongCat-Video-Avatar | Audio-driven human video (Wav2Vec2) | [🤗 HF](https://huggingface.co/meituan-longcat/LongCat-Video-Avatar) |
| LongCat-Video-Avatar-1.5 | Upgraded with Whisper-Large v3 & fast inference | [🤗 HF](https://huggingface.co/meituan-longcat/LongCat-Video-Avatar-1.5) |

## Resources

- 📄 [Technical Report](https://arxiv.org/abs/2510.22200)
- 📺 [Project Page](https://meituan-longcat.github.io/LongCat-Video/)
- 💬 [Discord Community](https://discord.gg/EXsG52D8SW)
- 🐦 [Twitter](https://x.com/Meituan_LongCat)

## Tips for Best Results

1. **Clear Prompts**: Be specific about visual details, movements, and style
2. **Negative Prompts**: Specify what to avoid (blur, artifacts, distortion)
3. **Frame Count**: 8-16 frames for short clips, 32-64 for longer sequences
4. **Guidance Scale**: 
   - 5-7: More creative, less literal
   - 7-10: Good balance
   - 10+: Strict adherence to prompt
5. **Resolution**: 
   - 720p: Requires 16GB+ VRAM
   - Higher resolution: Use GPU with 24GB+ VRAM

## Example Prompts

**Scenic:**
- "A beautiful sunset over a calm ocean with rolling waves"
- "A futuristic city with flying cars and neon lights at night"
- "A serene forest with deer walking through golden sunlight"

**Dynamic:**
- "A dancer performing an elegant ballet performance"
- "A bird flying through a canyon with dramatic cliffs"
- "A person walking through a busy city street"

**Creative:**
- "A painting coming to life with flowing colors"
- "A magical forest with glowing mushrooms and floating lights"
- "A space exploration scene with planets and asteroids"

## System Requirements

- **GPU**: At least 8GB VRAM (16GB+ recommended for 720p)
- **RAM**: 16GB+ system RAM
- **Disk**: ~25GB for model weights
- **CUDA**: 12.1+ for GPU acceleration

## Running Locally

```bash
# Clone and setup
git clone https://github.com/meituan-longcat/LongCat-Video
cd LongCat-Video

# Create environment
conda create -n longcat python=3.10
conda activate longcat

# Install dependencies
pip install -r requirements.txt

# Run the demo
python app.py
```

## Citation

If you use LongCat-Video in your research, please cite:

```bibtex
@article{longcatvideo2024,
  title={LongCat-Video: A Foundational Video Generation Model},
  author={Meituan LongCat Team},
  journal={arXiv preprint arXiv:2510.22200},
  year={2024}
}
```

## License

This project is licensed under the MIT License. See the repository for details.

---

**Built with ❤️ using Gradio and LongCat-Video**
