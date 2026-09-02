# 🚀 Deploying LongCat-Video to Hugging Face Spaces

## Quick Start

### Option 1: Using Web UI (Easiest)

1. **Create a Hugging Face Account**
   - Go to [huggingface.co](https://huggingface.co) and sign up

2. **Create a New Space**
   - Click your profile → "New Space"
   - Fill in details:
     - **Space name**: `longcat-video-demo` (or your choice)
     - **License**: MIT
     - **Select Gradio**
     - **Select GPU** (A100 or H100 recommended)

3. **Upload Files**
   - Upload `app.py` (or use `app_lite.py` for lighter version)
   - Upload `requirements.txt`
   - Upload `README.md`

4. **Deploy**
   - Spaces will auto-detect `app.py` and start building
   - Wait for the build to complete (~10-15 minutes)
   - Your Space is live!

### Option 2: Using Git (Recommended for Development)

```bash
# 1. Create Space on HF web UI (without uploading files)

# 2. Clone the Space repository
git clone https://huggingface.co/spaces/USERNAME/longcat-video-demo
cd longcat-video-demo

# 3. Add your files
cp ../app.py .
cp ../requirements.txt .
cp ../README.md .

# 4. Commit and push
git add .
git commit -m "Add LongCat-Video demo"
git push

# Space auto-deploys on push!
```

### Option 3: Using HF CLI

```bash
# Install HF CLI
pip install huggingface-hub

# Login
huggingface-cli login

# Create and upload
huggingface-cli repo create longcat-video-demo --type=space --space-sdk=gradio
cd longcat-video-demo
git clone https://huggingface.co/spaces/USERNAME/longcat-video-demo
cd longcat-video-demo

# Add files and push
cp ../../app.py .
cp ../../requirements.txt .
cp ../../README.md .

git add .
git commit -m "Add LongCat-Video demo"
git push
```

## File Options

### `app.py` (Full Featured)
- ✅ Text-to-Video
- ✅ Image-to-Video  
- ✅ Video Continuation
- ✅ Multiple tabs and examples
- ⚠️ Higher resource usage, slower inference
- 📋 Best for: Showcasing all features

### `app_lite.py` (Lightweight)
- ✅ Text-to-Video only
- ✅ Faster inference
- ✅ Lower resource usage
- ✅ Better UX for demos
- 📋 Best for: Quick demos, cost-effective

## Recommended Hardware

| GPU | VRAM | Resolution | Speed |
|-----|------|-----------|-------|
| T4 | 16GB | 480p | ~5 min |
| A100 | 40GB | 720p | ~2 min |
| H100 | 80GB | 1080p | ~1 min |

**Recommendation**: Use **A100 large** for best balance of speed and cost.

## Configuration Tips

### To Use `app_lite.py`:
Replace `app.py` reference with `app_lite.py` in your Space settings, or rename the file:
```bash
mv app_lite.py app.py
```

### Environment Variables (Optional)
Add to Space settings for custom behavior:

```bash
# Reduce memory usage
TORCH_CUDA_MAX_MEMORY_MB=20000

# Force FP16 (faster, less VRAM)
TORCH_PRECISION=fp16

# Enable gradient checkpointing (saves memory)
ENABLE_GRADIENT_CHECKPOINTING=true
```

## Troubleshooting

### "Out of Memory" Error
- Use `app_lite.py` version
- Lower default resolution in app
- Use A100 GPU instead of smaller models
- Enable gradient checkpointing

### Slow Inference
- Check Space logs for errors
- Use GPU with more VRAM
- Reduce number of inference steps
- Lower output resolution

### Model Download Fails
- Check internet connection
- Verify HF authentication
- Increase timeout in `app.py`
- Use smaller model variant

### Space Won't Build
- Check `requirements.txt` syntax
- Verify Python version compatibility (3.9+)
- Look at build logs for specific errors
- Try removing optional dependencies

## Monitoring & Analytics

1. **View Space Stats**
   - Go to Space settings → "Space metrics"
   - Monitor resource usage and crashes

2. **Check Logs**
   - Click "View logs" in Space header
   - Debug any runtime errors

3. **Uptime Monitoring**
   - Spaces auto-restart on crash
   - Check "Activity" tab for history

## Cost Management

**Estimate for A100 large:**
- Free tier: ~30 GPU hours/month
- Paid tier: $0.50-2.00 per GPU hour

**Tips to reduce costs:**
- Use free GPUs with smaller batch size
- Implement caching
- Set Space to "sleep" when unused
- Use `app_lite.py` for smaller model

## Customization Ideas

1. **Add your own examples**
   - Modify `gr.Examples()` with your prompts

2. **Change styling**
   - Modify Gradio theme colors
   - Add custom CSS

3. **Integrate with other models**
   - Add Avatar model support
   - Combine with image generation

4. **Add user feedback**
   - Save generated videos
   - Track popular prompts
   - Implement ratings

## Next Steps

- 🌟 Star the [LongCat-Video repo](https://github.com/meituan-longcat/LongCat-Video)
- 📖 Read the [Technical Paper](https://arxiv.org/abs/2510.22200)
- 💬 Join the [Discord Community](https://discord.gg/EXsG52D8SW)
- 🔗 Explore other [Meituan LongCat projects](https://github.com/meituan-longcat)

## FAQ

**Q: Can I use free GPU tier?**  
A: Yes, but with limitations. Use `app_lite.py` and lower resolution.

**Q: How long does inference take?**  
A: 2-5 minutes depending on GPU and settings.

**Q: Can I modify the model?**  
A: Yes! Fine-tune on your own data using the original repo.

**Q: Is there an API?**  
A: Yes, you can call HF Spaces as an API. See HF docs.

**Q: How do I cite this?**  
A: See README.md for citation information.

---

**Happy generating! 🎬✨**
