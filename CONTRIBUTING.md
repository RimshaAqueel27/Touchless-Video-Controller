# Contributing to Touchless Video Controller

First off, thank you for considering contributing to Touchless Video Controller! 🎉

## 🤔 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the problem
- **Expected vs actual behavior**
- **Screenshots** if applicable
- **Environment details:**
  - OS (Windows/Linux/Jetson)
  - Python version
  - TensorFlow version
  - Camera type

**Example:**
```
Title: Model fails to load on Jetson Nano with TF 2.3.1

Description:
When running media_control_mpv.py on Jetson Nano, I get:
"ValueError: Not a valid TFLite model"

Environment:
- Jetson Nano 4GB
- JetPack 4.4
- TensorFlow 2.3.1
- Python 3.6.9

Steps to reproduce:
1. Transfer gesture_model_v2.tflite to Jetson
2. Run python3 media_control_mpv.py
3. Error appears during model loading
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear and descriptive title**
- **Detailed description** of the proposed feature
- **Use cases** - why is this needed?
- **Mockups or examples** if applicable

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes:**
   - Follow the existing code style
   - Add comments for complex logic
   - Update documentation as needed
3. **Test thoroughly:**
   - Test on PC if training-related
   - Test on Jetson if deployment-related
   - Ensure existing gestures still work
4. **Commit with clear messages:**
   ```
   git commit -m "Add brightness control gesture"
   ```
5. **Push to your fork** and submit a pull request

## 🎨 Code Style Guidelines

### Python Code Style

- Follow **PEP 8** conventions
- Use **4 spaces** for indentation
- Maximum line length: **100 characters**
- Use descriptive variable names

```python
# Good
def predict_gesture(roi_input):
    """Run inference with TFLite model"""
    interpreter.set_tensor(input_details[0]['index'], roi_input)
    interpreter.invoke()
    return interpreter.get_tensor(output_details[0]['index'])

# Avoid
def pg(ri):
    interpreter.set_tensor(input_details[0]['index'], ri)
    interpreter.invoke()
    return interpreter.get_tensor(output_details[0]['index'])
```

### Documentation

- Add **docstrings** to all functions
- Update **README.md** if adding features
- Include **comments** for non-obvious code
- Update **CHANGELOG.md** (if we add one)

### Commit Messages

Use clear, descriptive commit messages:

```
✅ Good:
- "Add brightness control gesture"
- "Fix model loading error on TF 2.3.1"
- "Update README with troubleshooting section"

❌ Avoid:
- "fix bug"
- "update"
- "changes"
```

## 🧪 Testing

### Before Submitting PR

- [ ] Code runs without errors on PC
- [ ] Model training/conversion still works
- [ ] Gesture detection accuracy not degraded
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)

### Testing on Jetson Nano

If you don't have a Jetson Nano:
- Clearly mark PR as "Untested on Jetson"
- Other contributors can test and verify

## 📁 File Structure

When adding new files, follow this structure:

```
PC-TRAINING/          # All training-related code
  ├── *.py            # Python scripts
  ├── *.md            # Documentation
  └── dataset/        # Training data

JETSON-NANO-PROJECT/  # Deployment code only
  ├── media_control_mpv.py
  ├── *.tflite
  └── model_info.json
```

## 🆕 Adding New Gestures

To add a new gesture:

1. **Update dataset structure:**
   ```
   dataset/new_gesture/  (add 200+ images)
   ```

2. **Update class_names.txt:**
   ```
   forward
   play
   reverse
   stop

   volume_up
   new_gesture  ← Add here
   ```

3. **Update model_info.json:**
   ```json
   {
     "class_names": [..., "new_gesture"],
     ...
   }
   ```

4. **Add command mapping in media_control_mpv.py:**
   ```python
   MPV_COMMANDS = {
       ...
       'new_gesture': {'command': ['your', 'mpv', 'command']}
   }
   ```

5. **Update documentation:**
   - README.md gesture table
   - PC-TRAINING/README.md

## 🐛 Debugging Tips

### Enable Verbose Logging

```python
# In media_control_mpv.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Individual Components

```python
# Test TFLite model loading
python3 -c "import tensorflow as tf; print(tf.lite.Interpreter('gesture_model.tflite'))"

# Test camera
python3 -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"

# Test MPV socket
python3 -c "import socket; s = socket.socket(socket.AF_UNIX); s.connect('/tmp/mpv-socket')"
```

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## ❓ Questions?

Feel free to:
- Open an issue with the "question" label
- Reach out via email
- Start a discussion in GitHub Discussions

## 🎯 Priority Areas

We especially welcome contributions in:

- [ ] **New gesture commands** (brightness, contrast, subtitle toggle)
- [ ] **VLC player support** (alternative to MPV)
- [ ] **Performance optimization** (faster inference)
- [ ] **Pre-trained models** (ready-to-use models)
- [ ] **Web interface** (browser-based control panel)
- [ ] **Mobile app** (gesture control from phone)
- [ ] **Documentation** (tutorials, videos, translations)

---

Thank you for contributing! 🙌
