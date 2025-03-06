import os
from pathlib import Path
from typing import Literal
import ffmpeg


def convert_images_to_mp4(
    image_folder: str | Path,
    output_video_path: str | Path,
    fps: int = 30,
    image_format: str = "jpg",
    codec: str = "libx264",
    crf: int = 0,
    preset: Literal[
        "ultrafast",
        "superfast",
        "veryfast",
        "faster",
        "fast",
        "medium",
        "slow",
        "slower",
        "veryslow",
    ] = "medium",
) -> None:
    """Convert a folder of images to an MP4 video.

    Assumes that the images are sorted lexically by filename.

    Parameters
    ----------
    crf : int
        Constant Rate Factor (CRF) for video quality. The range is 0-51, where 0 is lossless, 23 is the default, and 51 is the worst quality.
    preset : str
        The preset for the x264 encoder. A slower preset will provide better compression efficiency.
    """

    image_folder = Path(image_folder)
    output_video_path = Path(output_video_path)

    # Create a temporary text file listing the image files
    temp_file_list = image_folder / "input_images.txt"
    with open(temp_file_list, "w") as f:
        for image_file in sorted(
            image_folder.glob(f"*.{image_format}"), key=lambda p: p.stem
        ):
            f.write(f"file '{image_file.name}'\n")

    (
        ffmpeg.input(temp_file_list, format="concat", safe=0, r=fps)
        .output(
            str(output_video_path),
            vcodec=codec,
            pix_fmt="yuv420p",
            crf=crf,
            preset=preset,
            r=fps,
            loglevel="error",
        )
        .run(overwrite_output=True)
    )

    # Clean up temporary file
    temp_file_list.unlink()


def _ffmpeg_assert_quality(quality: int) -> None:
    """Assert that the quality is between 2 and 31 (inclusive)."""
    assert 2 <= quality <= 31, (
        "Quality must be between 2 and 31 (inclusive), lower is better."
    )


def convert_mp4_to_images(
    video_path: str | Path,
    output_folder: str | Path,
    quality: int = 2,
    image_format: str = "jpg",
    file_names_pattern: str = "%05d",
) -> None:
    """Convert an MP4 video to a folder of JPG images.

    Example
    -------
    >>> video_path = 'video.mp4'
    >>> output_folder = 'video_jpg'
    >>> convert_mp4_to_jpg(video_path, output_folder)
    """
    os.makedirs(output_folder, exist_ok=True)
    output_pattern = os.path.join(output_folder, f"{file_names_pattern}.{image_format}")
    _ffmpeg_assert_quality(quality)
    ffmpeg.input(str(video_path)).output(output_pattern, **{"q:v": quality}).run()


def convert_mp4_to_images_every_nth_frame(
    video_path: str | Path,
    output_folder: str | Path,
    n: int = 30,
    quality: int = 2,
    image_format: str = "jpg",
    file_names_pattern: str = "%05d",
) -> None:
    """Convert an MP4 video to a folder of JPG images by selecting every `n`-th frame.

    Example
    -------
    >>> video_path = 'video.mp4'
    >>> output_folder = 'video_jpg'
    >>> convert_mp4_to_jpg_every_nth_frame(video_path, output_folder)
    """
    os.makedirs(output_folder, exist_ok=True)
    output_pattern = os.path.join(output_folder, f"{file_names_pattern}.{image_format}")
    _ffmpeg_assert_quality(quality)
    ffmpeg.input(str(video_path)).output(
        output_pattern,
        vf=f"select=not(mod(n\\,{n}))",  # Select every `n`-th frame
        vsync="vfr",  # Variable frame rate
        frame_pts=True,  # Preserve frame timestamps
        **{"q:v": quality},  # q:v = 2 corresponds to the highest quality (ranges 2-31)
    ).run()


def merge_videos(video_paths: list[Path], output_path: str | Path) -> None:
    """Merge multiple videos into a single video.

    Example
    -------
    >>> video_paths = list(Path('images').rglob('*.mp4'))
    >>> output_path = 'merged_video.mp4'
    >>> merge_videos(video_paths, output_path)
    """
    import cv2
    from tqdm import tqdm

    # Initialize variables for video properties
    frame_width = None
    frame_height = None
    fps = None

    # Create a VideoCapture object for each video
    video_captures = [cv2.VideoCapture(video) for video in video_paths]

    # Get video properties from the first video
    if video_captures:
        frame_width = int(video_captures[0].get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(video_captures[0].get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(video_captures[0].get(cv2.CAP_PROP_FPS))

    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(output_path), fourcc, fps, (frame_width, frame_height))

    for capture in tqdm(video_captures, desc="Merging videos"):
        while capture.isOpened():
            ret, frame = capture.read()
            if ret:
                # Write the frame into the final video
                out.write(frame)
            else:
                break
        capture.release()  # Release the capture object for each video

    out.release()  # Release the VideoWriter object
    cv2.destroyAllWindows()


def rename_files_in_folder(
    folder_path: str | Path, zero_padding_length: int = 5
) -> None:
    """Rename files in a folder by padding the numeric part of the filename with zeros."""
    import re

    for filename in os.listdir(folder_path):
        # Use regular expression to find numeric part in the filename
        match = re.search(r"(\d+)", filename)
        if match:
            # Extract numeric part and pad with zeros
            numeric_part = match.group(0)
            padded_numeric_part = numeric_part.zfill(zero_padding_length)

            # Replace numeric part in filename with padded version
            new_filename = re.sub(r"\d+", padded_numeric_part, filename).strip()

            try:
                # Rename the file
                os.rename(
                    os.path.join(folder_path, filename),
                    os.path.join(folder_path, new_filename),
                )
                print(f"Renamed {filename} to {new_filename}")
            except Exception as e:
                print(f"Error renaming {filename}: {e}")


def sam2_output_export(
    video_segments, frame_names: list[str | Path], output_dir: str | Path = "output"
) -> None:
    """Export SAM2 output to masks and visualization images.

    Example
    -------
    >>> video_predictor = build_sam2_video_predictor(CONFIG, CHECKPOINT, device=DEVICE, apply_postprocessing=False)
    >>> frame_names = list(IMAGES_DIR.glob('*.jpg'))
    >>> frame_names.sort(key=lambda p: int(p.stem))
    >>> video_segments = {}  # video_segments contains the per-frame segmentation results
    >>> for out_frame_idx, out_obj_ids, out_mask_logits in video_predictor.propagate_in_video(inference_state):
    >>>     video_segments[out_frame_idx] = {
    >>>         out_obj_id: (out_mask_logits[i] > 0.0).cpu().numpy()
    >>>         for i, out_obj_id in enumerate(out_obj_ids)
    >>>     }
    >>> sam2_output_export(video_segments, frame_names, IMAGES_DIR / 'sam2_output')
    """
    import numpy as np
    from PIL import Image
    from tqdm import tqdm

    out_dir = Path(output_dir)
    masks_dir = out_dir / "masks"
    vis_dir = out_dir / "visualization"

    masks_dir.mkdir(parents=True, exist_ok=True)
    vis_dir.mkdir(parents=True, exist_ok=True)

    for out_frame_idx in tqdm(range(0, len(frame_names)), desc="Exporting SAM2 output"):
        for out_obj_id, out_mask in video_segments[out_frame_idx].items():
            # Save mask
            mask = out_mask.squeeze()
            mask_img = Image.fromarray(
                (mask * 255).astype(np.uint8)
            )  # Convert mask to 0-255 range
            mask_img.save(masks_dir / f"{out_frame_idx:05d}.png")

            # Save overlay
            mask_rgba = np.zeros((*mask.shape, 4), dtype=np.uint8)
            mask_rgba[..., 0] = 255  # Red
            mask_rgba[..., 3] = (mask > 0.5) * 102  # Alpha channel with transparency
            mask_img = Image.fromarray(mask_rgba, "RGBA")
            frame_img_rgba = Image.open(frame_names[out_frame_idx]).convert("RGBA")
            overlay_img = Image.alpha_composite(frame_img_rgba, mask_img)
            overlay_img.convert("RGB").save(vis_dir / f"{out_frame_idx:05d}.jpg")
