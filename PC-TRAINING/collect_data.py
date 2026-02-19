import cv2
import os

# Configuration
gesture_name = "forward"  # Change this for each gesture: forward, play, reverse, stop, volume_up
save_path = f"dataset/{gesture_name}"
os.makedirs(save_path, exist_ok=True)

# Check existing data for all gestures
all_gestures = ["forward", "play", "reverse", "stop", "volume_up"]
gesture_counts = {}
TARGET_IMAGES = 200

print("\n" + "="*60)
print("GESTURE DATA COLLECTION - Progress Tracker")
print("="*60)

for gesture in all_gestures:
    gesture_path = f"dataset/{gesture}"
    if os.path.exists(gesture_path):
        count = len([f for f in os.listdir(gesture_path) if f.endswith(('.jpg', '.png'))])
    else:
        count = 0
    gesture_counts[gesture] = count
    
    # Status indicator
    if count >= TARGET_IMAGES:
        status = "✓ COMPLETE"
        color = "\033[92m"  # Green
    elif count > 0:
        status = f"⚠ NEEDS MORE ({TARGET_IMAGES - count} needed)"
        color = "\033[93m"  # Yellow
    else:
        status = "✗ NOT STARTED"
        color = "\033[91m"  # Red
    
    reset = "\033[0m"
    bar_length = 30
    filled = int((count / TARGET_IMAGES) * bar_length)
    bar = "█" * filled + "░" * (bar_length - filled)
    
    print(f"{color}{gesture:12} [{bar}] {count:3}/{TARGET_IMAGES} {status}{reset}")

print("="*60)

# Try external webcam (usually index 1)
cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("External webcam not found. Trying default camera...")
    cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Could not open any camera!")
    exit(1)

print(f"✓ Camera opened successfully")

count = gesture_counts[gesture_name]
print("\n" + "="*60)
print(f"COLLECTING: {gesture_name.upper()}")
print("="*60)
print(f"Current count: {count}/{TARGET_IMAGES}")
print(f"Target: {TARGET_IMAGES} images")
print("\nInstructions:")
print("  - Place your hand inside the GREEN box")
print("  - Press 's' to save image")
print("  - Press 'q' to quit and switch gesture")
print("\nTips for BEST accuracy:")
print("  - Vary hand angles (left, right, tilted)")
print("  - Different distances from camera")
print("  - Different lighting conditions")
print("  - Slightly different hand positions in box")
print("  - Hold gesture naturally as you would during use")
print("="*60 + "\n")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Flip frame for mirror effect
    frame = cv2.flip(frame, 1)

    # Draw ROI (Region of Interest)
    cv2.rectangle(frame, (100, 100), (400, 400), (0, 255, 0), 2)

    # Extract ROI
    roi = frame[100:400, 100:400]

    # Calculate progress
    progress_pct = (count / TARGET_IMAGES) * 100
    remaining = TARGET_IMAGES - count
    
    # Status color
    if count >= TARGET_IMAGES:
        status_color = (0, 255, 0)  # Green
        status_text = "COMPLETE!"
    elif count >= TARGET_IMAGES * 0.5:
        status_color = (0, 255, 255)  # Yellow
        status_text = f"HALFWAY - {remaining} more"
    else:
        status_color = (0, 165, 255)  # Orange
        status_text = f"{remaining} needed"
    
    # Display instructions
    cv2.putText(frame, f"Gesture: {gesture_name.upper()}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(frame, f"Progress: {count}/{TARGET_IMAGES} ({progress_pct:.1f}%)", (10, 65),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
    cv2.putText(frame, status_text, (10, 95),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
    
    # Progress bar
    bar_width = 300
    bar_height = 20
    bar_x, bar_y = 10, 110
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (100, 100, 100), -1)
    filled_width = int((count / TARGET_IMAGES) * bar_width)
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + filled_width, bar_y + bar_height), status_color, -1)
    
    cv2.putText(frame, "Press 's' to save | 'q' to quit", (10, 150),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    cv2.imshow("Data Collection", frame)
    cv2.imshow("ROI", roi)

    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('s'):
        # Save image
        img_path = os.path.join(save_path, f"{gesture_name}_{count}.jpg")
        cv2.imwrite(img_path, roi)
        count += 1
        print(f"✓ Saved: {gesture_name}_{count-1}.jpg | Total: {count}/{TARGET_IMAGES}")
        
        # Show achievement messages
        if count == TARGET_IMAGES:
            print(f"\n{'='*60}")
            print(f"🎉 CONGRATULATIONS! {gesture_name.upper()} collection COMPLETE!")
            print(f"{'='*60}\n")
        elif count == TARGET_IMAGES // 2:
            print(f"\n{'='*60}")
            print(f"✓ HALFWAY THERE! {count} images collected for {gesture_name}")
            print(f"{'='*60}\n")
    
    elif key == ord('q'):
        # Show completion summary
        print(f"\n{'='*60}")
        print(f"SESSION SUMMARY - {gesture_name.upper()}")
        print(f"{'='*60}")
        print(f"Total collected: {count}/{TARGET_IMAGES}")
        
        if count >= TARGET_IMAGES:
            print(f"Status: ✓ COMPLETE!")
        else:
            remaining = TARGET_IMAGES - count
            print(f"Status: ⚠ Need {remaining} more images")
        
        print(f"{'='*60}\n")
        
        # Show overall progress
        print("OVERALL PROGRESS:")
        for gesture in all_gestures:
            gesture_path = f"dataset/{gesture}"
            if os.path.exists(gesture_path):
                g_count = len([f for f in os.listdir(gesture_path) if f.endswith(('.jpg', '.png'))])
            else:
                g_count = 0
            
            status = "✓" if g_count >= TARGET_IMAGES else "⚠" if g_count > 0 else "✗"
            print(f"  {status} {gesture:12} {g_count:3}/{TARGET_IMAGES}")
        
        print()
        break

cap.release()
cv2.destroyAllWindows()
