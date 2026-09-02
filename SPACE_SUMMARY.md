# 🎬 LongCat-Video Hugging Face Space - Complete Package

## 📦 What's Included

This package contains everything needed to deploy a LongCat-Video demo to Hugging Face Spaces.

### Files

```
├── app.py                    # Full-featured Gradio app (Text/Image/Continuation)
├── app_lite.py              # Lightweight version (Text-to-Video only, faster)
├── requirements.txt         # Python dependencies
├── README.md                # Space description & documentation
├── DEPLOYMENT_GUIDE.md      # Step-by-step deployment instructions
└── SPACE_SUMMARY.md         # This file
```

## 🚀 Quick Deploy (3 Steps)

### Step 1: Prepare Files
```bash
cd /home/user/agenticSeek
ls -la app*.py requirements.txt README.md
```

### Step 2: Create Space on HuggingFace
1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
2. Fill in:
   - **Space name**: `longcat-video-demo`
   - **License**: MIT
   - **SDK**: Gradio
   - **GPU**: A100 or H100 (recommended)

### Step 3: Upload & Deploy
**Option A - Web Upload (Easiest):**
1. Drag & drop files into Space
2. System auto-detects `app.py`
3. Build starts automatically (~10-15 min)

**Option B - Git Push (Recommended):**
```bash
git clone https://huggingface.co/spaces/YOUR_USERNAME/longcat-video-demo
cd longcat-video-demo

# Copy files
cp /home/user/agenticSeek/app.py .
cp /home/user/agenticSeek/requirements.txt .
cp /home/user/agenticSeek/README.md .

# Push
git add .
git commit -m "Add LongCat-Video demo"
git push
```

## 📊 Feature Comparison

| Feature | `app.py` | `app_lite.py` |
|---------|----------|--------------|
| Text-to-Video | ✅ | ✅ |
| Image-to-Video | ✅ | ❌ |
| Video Continuation | ✅ | ❌ |
| Inference Speed | ~3 min | ~2 min |
| Memory Usage | High | Lower |
| UI Complexity | Advanced | Simple |
| **Best For** | Full showcase | Quick demo |

**Recommendation**: Use `app.py` for complete demo, or rename `app_lite.py` to `app.py` for lightweight version.

## 💾 Resource Requirements

### Minimum
- **GPU**: T4 (16GB VRAM)
- **Time**: 5-10 minutes per video
- **Cost**: Free tier available

### Recommended
- **GPU**: A100 (40GB VRAM)
- **Time**: 2-3 minutes per video
- **Cost**: ~$0.50-1.00 per GPU hour

### Optimal
- **GPU**: H100 (80GB VRAM)
- **Time**: 1-2 minutes per video
- **Cost**: ~$2.00 per GPU hour

## 🔧 Customization Options

### Change Default Prompts
Edit in `app.py` or `app_lite.py`:
```python
gr.Examples(
    examples=[
        "Your custom prompt here",
        "Another example prompt",
    ],
    inputs=[prompt]
)
```

### Adjust Inference Parameters
```python
# In generate_video function:
num_inference_steps=30,  # 20-50 (lower=faster but lower quality)
guidance_scale=7.5,       # 1-15 (higher=more prompt adherence)
```

### Change UI Theme
```python
gr.Blocks(theme=gr.themes.Monochrome())  # Other options: Soft, Base, Glass
```

## 📈 Performance Tips

1. **Start smaller**: Use 480p resolution before scaling to 720p
2. **Cache model**: Avoid reloading on each request (app already does this)
3. **Enable attention slicing**: Saves VRAM (app already enables this)
4. **Use FP16**: Faster and lower VRAM (app uses this by default)
5. **Batch processing**: For multiple requests, queue them

## 🛠️ Troubleshooting

**Space Won't Build?**
- Check `requirements.txt` for syntax errors
- Verify Python version compatibility
- Look at build logs for specific errors

**Out of Memory?**
- Use `app_lite.py`
- Reduce default resolution
- Upgrade to A100 GPU

**Slow Generation?**
- Check if GPU is being used (monitor Space logs)
- Increase GPU memory allocation
- Reduce inference steps

**Model Download Fails?**
- Check HuggingFace authentication
- Verify internet connectivity
- Increase download timeout

See `DEPLOYMENT_GUIDE.md` for detailed troubleshooting.

## 📚 Additional Resources

- **Model Card**: https://huggingface.co/meituan-longcat/LongCat-Video
- **Technical Paper**: https://arxiv.org/abs/2510.22200
- **Project Page**: https://meituan-longcat.github.io/LongCat-Video/
- **GitHub Repo**: https://github.com/meituan-longcat/LongCat-Video
- **Discord**: https://discord.gg/EXsG52D8SW

## 🎓 Learning Resources

- [Gradio Documentation](https://gradio.app/guides/)
- [HuggingFace Spaces Docs](https://huggingface.co/docs/hub/spaces)
- [Diffusers Library](https://huggingface.co/docs/diffusers/)
- [PyTorch Documentation](https://pytorch.org/docs/)

## 📋 Pre-Deployment Checklist

- [ ] Downloaded all files to local machine
- [ ] Created HuggingFace account
- [ ] Have A100 or H100 GPU available (or T4 for lite version)
- [ ] Read `DEPLOYMENT_GUIDE.md`
- [ ] Decided between `app.py` (full) or `app_lite.py` (lite)
- [ ] Ready to upload to new Space

## 🚀 After Deployment

1. **Test the Space**
   - Try Text-to-Video generation
   - Test with different prompts
   - Check inference time

2. **Monitor Performance**
   - View Space metrics
   - Check resource usage
   - Review user feedback

3. **Iterate & Improve**
   - Add custom examples
   - Optimize parameters
   - Enhance UI/UX

4. **Share & Promote**
   - Share Space link
   - Add to portfolio
   - Contribute to community

## 📞 Support

If you encounter issues:
1. Check `DEPLOYMENT_GUIDE.md` troubleshooting section
2. Review HuggingFace Spaces documentation
3. Check Space logs for error messages
4. Join LongCat Discord community

## 📝 Citation

If you use LongCat-Video in research/projects:

```bibtex
@article{longcatvideo2024,
  title={LongCat-Video: A Foundational Video Generation Model},
  author={Meituan LongCat Team},
  journal={arXiv preprint arXiv:2510.22200},
  year={2024}
}
```

---

**Created with ❤️ for the AI Community**

**Last Updated**: 2025-09-02
**Version**: 1.0
**Status**: Ready to Deploy ✅
