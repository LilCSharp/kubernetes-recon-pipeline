import os
import zipfile
import tempfile
import boto3
import subprocess
from pathlib import Path
import uuid

# Required ENV variables
S3_BUCKET = os.environ["S3_BUCKET"]
ZIP_KEY = os.environ["ZIP_KEY"]
S3_ENDPOINT = os.getenv("S3_ENDPOINT")  # for MinIO/localstack, optional
OUTPUT_PREFIX = os.environ.get("OUTPUT_PREFIX", "results/")

s3 = boto3.client("s3", endpoint_url=S3_ENDPOINT) if S3_ENDPOINT else boto3.client("s3")

def download_zip(s3_bucket, zip_key, dest_path):
    print(f"Downloading {zip_key} from S3 bucket {s3_bucket} to {dest_path}")
    s3.download_file(s3_bucket, zip_key, dest_path)

def extract_zip(zip_path, extract_dir):
    print(f"Extracting {zip_path} to {extract_dir}")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_dir)

def find_images(directory):
    image_extensions = [".png", ".jpg", ".jpeg"]
    return [str(p) for p in Path(directory).rglob("*") if p.suffix.lower() in image_extensions]

def run_pipeline(image_path, output_dir):
    print(f"Running Matrix3D pipeline on image: {image_path}")
    scene_id = Path(image_path).stem
    result_dir = os.path.join(output_dir, "results", "single-to-3d", scene_id)
    cmd = [
        "python", "pipeline_single_to_3d.py",
        "--gpu", "0",
        "--exp_name", "single-to-3d",
        "--data_path", image_path,
        "--mixed_precision", "fp16",
        "--config", "configs/config_stage3.yaml",
        "--checkpoint_path", "checkpoints/matrix3d-general-use.pt",
        "--default_fov", "60.0",
        "--random_seed", "1",
        "--num_samples", "80",
        "--nvs_with_depth_cond", "1"
    ]
    subprocess.run(cmd, check=True, cwd="/workspace/ml-matrix3d")
    return os.path.join(result_dir, "ref_pred_pointcloud.ply")

def upload_to_s3(local_path, bucket, key):
    print(f"Uploading {local_path} to s3://{bucket}/{key}")
    s3.upload_file(local_path, bucket, key)

def main():
    job_id = str(uuid.uuid4())
    with tempfile.TemporaryDirectory() as workdir:
        zip_path = os.path.join(workdir, "input.zip")
        download_zip(S3_BUCKET, ZIP_KEY, zip_path)

        extract_dir = os.path.join(workdir, "extracted")
        os.makedirs(extract_dir, exist_ok=True)
        extract_zip(zip_path, extract_dir)

        images = find_images(extract_dir)
        if not images:
            raise RuntimeError("No valid images found in extracted ZIP.")

        for image_path in images:
            ply_path = run_pipeline(image_path, "/workspace/ml-matrix3d")
            ply_name = f"{Path(image_path).stem}.ply"
            upload_to_s3(ply_path, S3_BUCKET, os.path.join(OUTPUT_PREFIX, ply_name))

if __name__ == "__main__":
    main()
