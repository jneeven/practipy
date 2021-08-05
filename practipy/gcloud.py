import math
import os
from concurrent.futures import Future, ThreadPoolExecutor, as_completed, wait
from dataclasses import dataclass
from pathlib import Path
from typing import List, Literal, Sequence, Union

from google.cloud import storage as gcs
from tqdm import tqdm

from practipy.text import remove_prefix

"""
TODO:
- Return generator instead of list?
"""


@dataclass
class TransferEvent:
    """Represents a file download or upload operation."""

    num_bytes: int
    source_path: str
    target_path: str


def download_folder(
    project: str,
    source_dir: str,
    target_dir: Union[Path, str],
    progress_bar: bool = True,
):
    """Download all the contents of `source_dir` on GCS `target_dir` on the local
    filesystem.

    Note: The bucket should be included in the source path!
    """
    target_dir = Path(target_dir)

    # Remove any gs:// prefix and split the bucket name off the source dir
    source_dir = Path(remove_prefix(source_dir, "gs://"))
    bucket_name = source_dir.parts[0]
    source_dir = str(source_dir.relative_to(bucket_name))
    client = gcs.Client(project=project)

    def download_blob(blob: gcs.Blob) -> TransferEvent:
        relative_path = remove_prefix(blob.name, source_dir)
        local_path = target_dir.joinpath(relative_path.strip("/"))

        num_bytes = 0
        # If this is an empty folder, just create it, don't download it.
        if relative_path.endswith("/"):
            local_path.mkdir(exist_ok=True)
        # Otherwise, make sure the folder for this file exists and download the file.
        elif not local_path.exists():
            local_path.parent.mkdir(exist_ok=True, parents=True)
            blob.download_to_filename(str(local_path))
            # blob.size is unreliable and may return None for some reason...
            num_bytes = local_path.stat().st_size

        return TransferEvent(num_bytes, blob.name, str(local_path))

    # We simply download all blobs that are prefixed with the source dir
    blobs = list(client.list_blobs(bucket_name, prefix=source_dir))

    # Create a ThreadPool to download multiple files in parallel
    with ThreadPoolExecutor() as e:
        futures = [e.submit(download_blob, blob) for blob in blobs]
        if progress_bar:
            network_futures_progress_bar(futures, mode="download", keep_order=False)
        else:
            wait(futures)


def download_files(
    project: str,
    bucket: str,
    gcs_paths: Sequence[str],
    download_dir: Union[Path, str],
    strip_prefix: str = "",
    keep_order: bool = True,
    progress_bar: bool = True,
) -> List[str]:
    """Strips `strip_prefix` from all GCS paths in `gcs_paths` and then downloads them
    to `download_dir` on the local filesystem, creating it if it does not yet exist.

    Returns the list of local filepaths.
    Note: paths are relative to `gs://<bucket_name>`!.
    """

    bucket = gcs.Client(project=project).get_bucket(bucket)
    blobs = [bucket.blob(gcs_path) for gcs_path in gcs_paths]
    download_dir = Path(download_dir)

    def download_blob(blob: gcs.Blob) -> TransferEvent:
        relative_path = remove_prefix(blob.name, strip_prefix)
        local_path = download_dir.joinpath(relative_path)
        num_bytes = 0
        if not local_path.exists():
            local_path.parent.mkdir(exist_ok=True, parents=True)
            blob.download_to_filename(str(local_path))
            # blob.size is unreliable and may return None for some reason...
            num_bytes = local_path.stat().st_size

        return TransferEvent(num_bytes, blob.name, str(local_path))

    # Create a ThreadPool to download multiple files in parallel
    with ThreadPoolExecutor() as e:
        futures = [e.submit(download_blob, blob) for blob in blobs]
        if progress_bar:
            events = network_futures_progress_bar(futures, keep_order=keep_order)
        else:
            events = [f.result() for f in futures]

    return [event.target_path for event in events]


def upload_folder(
    project: str,
    source_dir: Union[Path, str],
    target_dir: str,
    progress_bar: bool = True,
) -> None:
    """Upload all the contents of `source_dir` on the local filesystem into `target_dir`
    on GCS.

    Note: The bucket should be included in the target path!
    """

    source_dir = Path(source_dir)

    # Remove any gs:// prefix and split the bucket name off the target dir
    target_dir = Path(remove_prefix(target_dir, "gs://"))
    bucket_name = target_dir.parts[0]
    target_dir = str(target_dir.relative_to(bucket_name))

    bucket = gcs.Client(project=project).get_bucket(str(bucket_name))

    # Note: This will overwrite any blobs that already exist.
    def upload_file(file: Path) -> TransferEvent:
        blob = bucket.blob(os.path.join(target_dir, str(file.relative_to(source_dir))))
        blob.upload_from_filename(str(file), checksum="md5")
        return TransferEvent(file.stat().st_size, str(file), blob.name)

    files = source_dir.glob("**/*")
    # Create a ThreadPool to upload multiple files in parallel
    with ThreadPoolExecutor() as e:
        futures = [e.submit(upload_file, file) for file in files if file.is_file()]
        if progress_bar:
            network_futures_progress_bar(futures, mode="upload", keep_order=False)
        else:
            wait(futures)


def upload_files(
    project: str,
    paths: Sequence[Union[Path, str]],
    target_dir: str,
    strip_prefix: str = "",
    progress_bar: bool = True,
) -> None:
    """Upload all provided files from the local filesystem into `target_dir` on GCS.
    `strip_prefix` is removed from each local filepath and the remainder is appended to
    `target_dir` to create the target path.

    Note: The bucket should be included in the target path!
    """

    # Remove any gs:// prefix and split the bucket name off the target dir
    target_dir = Path(remove_prefix(target_dir, "gs://"))
    bucket_name = target_dir.parts[0]
    target_dir = str(target_dir.relative_to(bucket_name))

    bucket = gcs.Client(project=project).get_bucket(str(bucket_name))

    # Note: This will overwrite any blobs that already exist.
    def upload_file(file: Path) -> TransferEvent:
        blob = bucket.blob(
            os.path.join(target_dir, remove_prefix(str(file), strip_prefix).strip("/"))
        )
        blob.upload_from_filename(str(file), checksum="md5")
        return TransferEvent(file.stat().st_size, str(file), blob.name)

    # Create a ThreadPool to upload multiple files in parallel
    with ThreadPoolExecutor() as e:
        futures = [e.submit(upload_file, path) for path in paths]
        if progress_bar:
            network_futures_progress_bar(futures, mode="upload", keep_order=False)
        else:
            wait(futures)


def network_futures_progress_bar(
    futures: Sequence[Future],
    mode: Literal["download", "upload"] = "download",
    keep_order: bool = True,
) -> List[TransferEvent]:
    """Given a sequence of futures that return TransferEvents, display a progress bar
    that computes the transfer speed and finally return the list of TransferEvents."""

    iterable = futures if keep_order else as_completed(futures)
    progress_bar = tqdm(
        iterable, total=len(futures), desc=f"{mode.capitalize()}ing files"
    )
    total_bytes = 0
    events = []
    # Update either every 100 events or every 1% of the number of events
    interval = min(100, math.ceil(len(futures) / 100.0))
    for f, future in enumerate(progress_bar):
        event = future.result()
        events.append(event)
        total_bytes += event.num_bytes

        if f % interval == 0 or f == len(futures) - 1:
            megabytes = total_bytes / 1048576.0  # 1024^2
            speed = megabytes / progress_bar.format_dict["elapsed"]
            progress_bar.set_postfix_str(
                f"{mode.capitalize()}ed {megabytes:.2f} MiB at {speed:.2f} MiB/s."
            )
    return events
