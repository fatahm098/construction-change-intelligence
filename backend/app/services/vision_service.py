import os
import cv2
import numpy as np


def align_drawings_sift(img_ref, img_target):
    """
    Menyelaraskan img_target ke ruang koordinat img_ref menggunakan SIFT + Homography.
    """
    gray_ref = cv2.cvtColor(img_ref, cv2.COLOR_BGR2GRAY) if len(img_ref.shape) == 3 else img_ref
    gray_target = cv2.cvtColor(img_target, cv2.COLOR_BGR2GRAY) if len(img_target.shape) == 3 else img_target

    sift = cv2.SIFT_create()
    kp_target, des_target = sift.detectAndCompute(gray_target, None)
    kp_ref, des_ref = sift.detectAndCompute(gray_ref, None)

    if des_target is None or des_ref is None:
        return img_target, None

    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des_target, des_ref, k=2)

    good = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good.append(m)

    if len(good) > 10:
        src_pts = np.float32([kp_target[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp_ref[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

        H, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        h, w = gray_ref.shape
        aligned = cv2.warpPerspective(img_target, H, (w, h))
        return aligned, H

    return img_target, None


def detect_changed_regions(img_v0, img_v1, min_area=350, padding=12, output_dir=None):
    """
    Deteksi perbedaan piksel dan ekstrak bounding boxes.
    Returns: list of region dicts, annotated_image_path
    """
    gray_v0 = cv2.cvtColor(img_v0, cv2.COLOR_BGR2GRAY) if len(img_v0.shape) == 3 else img_v0
    gray_v1 = cv2.cvtColor(img_v1, cv2.COLOR_BGR2GRAY) if len(img_v1.shape) == 3 else img_v1

    diff = cv2.absdiff(gray_v0, gray_v1)
    _, thresh = cv2.threshold(diff, 28, 255, cv2.THRESH_BINARY)

    kernel = np.ones((9, 9), np.uint8)
    dilated = cv2.dilate(thresh, kernel, iterations=2)

    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    vis_img = img_v1.copy()
    regions = []

    for idx, cnt in enumerate(contours):
        area = cv2.contourArea(cnt)
        if area >= min_area:
            x, y, w, h = cv2.boundingRect(cnt)
            x1 = max(0, x - padding)
            y1 = max(0, y - padding)
            x2 = min(img_v1.shape[1], x + w + padding)
            y2 = min(img_v1.shape[0], y + h + padding)

            crop_v0 = img_v0[y1:y2, x1:x2]
            crop_v1 = img_v1[y1:y2, x1:x2]

            crop_v0_path = None
            crop_v1_path = None
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                crop_v0_path = os.path.join(output_dir, f"crop_r{len(regions)+1}_v0.png")
                crop_v1_path = os.path.join(output_dir, f"crop_r{len(regions)+1}_v1.png")
                cv2.imwrite(crop_v0_path, crop_v0)
                cv2.imwrite(crop_v1_path, crop_v1)

            regions.append({
                "region_index": len(regions) + 1,
                "bbox": (x1, y1, x2 - x1, y2 - y1),
                "area": float(area),
                "crop_v0": crop_v0,
                "crop_v1": crop_v1,
                "crop_v0_path": crop_v0_path,
                "crop_v1_path": crop_v1_path,
            })

            cv2.rectangle(vis_img, (x1, y1), (x2, y2), (0, 0, 255), 3)
            cv2.putText(vis_img, f"#{len(regions)}", (x1, max(20, y1 - 6)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    diff_image_path = None
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        diff_image_path = os.path.join(output_dir, "annotated_diff.png")
        cv2.imwrite(diff_image_path, vis_img)

    return regions, diff_image_path
