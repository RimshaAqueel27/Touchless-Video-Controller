# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-19

### 🎉 Initial Release

#### Added
- **6 hand gesture commands** for video control:
  - Play/Pause toggle
  - Stop (pause)
  - Forward (+10 seconds)
  - Reverse (-10 seconds)
  - Volume Up (+10%)
  - Volume Down (-10%)
- **PC Training Environment**:
  - Data collection script with auto-capture mode
  - MobileNetV2-based training pipeline
  - TFLite conversion with Jetson Nano compatibility
  - Model testing utilities
- **Jetson Nano Deployment**:
  - Real-time gesture recognition (30 FPS)
  - MPV integration via IPC socket
  - Confidence threshold filtering (90%)
  - Gesture hold time validation (0.5s)
- **Documentation**:
  - Comprehensive README with quick start guide
  - PC training guide
  - Jetson setup guide
  - Data collection checklist
  - Contribution guidelines
- **Model Features**:
  - TensorFlow Lite optimization (8.5 MB)
  - 96.67% validation accuracy
  - Cross-platform compatibility
  - 128×128 input resolution

#### Technical Details
- Base Model: MobileNetV2 (ImageNet pretrained)
- Framework: TensorFlow 2.3.1+ compatible
- Input Resolution: 128×128×3 RGB
- Inference Latency: ~33-50ms on Jetson Nano
- Training Framework: TensorFlow 2.8+ on PC

---

## [Unreleased]

### Planned Features
- [ ] VLC player support (alternative to MPV)
- [ ] Additional gestures (brightness, contrast, subtitle toggle)
- [ ] Web-based configuration interface
- [ ] Pre-trained model distribution
- [ ] Mobile app version
- [ ] Real-time hand tracking visualization
- [ ] Multi-gesture sequence support
- [ ] Custom gesture training UI

### Known Issues
- Model requires consistent lighting conditions for best accuracy
- Volume continuous control may lag on slower systems
- Dataset collection requires manual gesture name editing

---

## Version History

### Version Numbering
- **Major.Minor.Patch** (e.g., 1.0.0)
- **Major**: Breaking changes
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes (backward compatible)

### Categories
- **Added**: New features
- **Changed**: Changes to existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements

---

## How to Contribute

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on submitting changes and updates to this changelog.
